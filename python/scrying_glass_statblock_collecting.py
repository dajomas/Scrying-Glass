"""Statblock collection when monsters are added (SG-TODO-022.15 correction).

Add Monster with a selected lookup source collects the statblock from that same
source (the exact ``monster_source_*`` identity the selection stored); Import
.monster uses the imported file. One preparation per add runs in the shared job
scheduler and isolated workers, so the add itself never waits for it. When it
completes, the statblock is saved in one transaction to every monster of that
add that still has the same species, source identity and no statblock. No
source, a disabled provider, a full queue, an unavailable record or any failure
leaves the monsters without a statblock: the add carries on.

Nothing is overwritten without confirmation (user decision 2026-11-20): a
monster that meanwhile got a different statblock (Edit Monster, automatic
loading) or whose species or source was edited keeps its state, and the
collected statblock waits for the Admin's Replace / Keep current decision
(``collected_list`` / ``collected_decide``) until it expires after
``selection_seconds``. An identical statblock is skipped silently; removed
monsters are skipped.
"""
from __future__ import annotations

import asyncio
import copy
import hashlib
import logging
import secrets
from collections import OrderedDict

from .scrying_glass_statblock_contract import StatblockAPIError, _iso, _now_iso
from .scrying_glass_statblock_discovery import FILE, original_identity, source_fields
from .scrying_glass_statblock_jobs import Job, JobCapacity
from .scrying_glass_statblock_limits import MONSTER_FILE_BYTES

LOG = logging.getLogger(__name__)
COLLECT_OWNER = 'add-monster-collection'


class CollectingMixin:
    def collect_new_monsters(self, monster_ids, *, file_bytes=None, filename=None):
        """Schedule collection for monsters just added; returns the job or None. Call from async code."""
        try:
            campaign = str(self.context.active_campaign())
        except Exception:
            return None
        monsters = self._monsters()
        targets = [monsters[ident] for ident in monster_ids if ident in monsters]
        if not targets:
            return None
        config = self.config()
        if file_bytes is not None:
            if type(file_bytes) is not bytes or not file_bytes or len(file_bytes) > MONSTER_FILE_BYTES:
                return None
            provider = FILE
            identity = {'sha256': hashlib.sha256(file_bytes).hexdigest(),
                        'filename': filename if type(filename) is str else None}
        else:
            original = original_identity(targets[0], config)
            if original is None:
                return None  # no exact source: nothing to collect
            provider, identity = original
            if not config.enabled.get(provider):
                return None
        self._auto_loop = asyncio.get_running_loop()
        info = {'collect': True, 'provider': provider, 'identity': identity, 'config': config,
                'campaign': campaign, 'token': self.encounter_token(campaign), 'file_bytes': file_bytes,
                'targets': [(m['id'], str(m.get('monster_species') or ''), source_fields(m)) for m in targets]}
        job = Job(COLLECT_OWNER, self._work, deadline=self.clock() + self.limits.preparation_seconds, info=info)
        try:
            self.scheduler.submit(job)
        except JobCapacity:
            return None
        return job

    def _collect_finished(self, job, state, result, error):
        """Scheduler callback (worker thread): hand a completed statblock to the event loop."""
        info = job.info
        file_bytes, info['file_bytes'] = info.get('file_bytes'), None
        if state != 'completed':
            LOG.info('Statblock collection for added monsters ended without a statblock: %s',
                     error[0] if error else state)
            return state, None, error
        if file_bytes is not None and info['identity'].get('sha256') != hashlib.sha256(file_bytes).hexdigest():
            return 'failed', None, ('identity_mismatch', 'The file changed during preparation.', None)
        snapshot = copy.deepcopy(result['snapshot'])
        snapshot.pop('revision', None)
        snapshot['prepared_at'] = _now_iso()
        try:
            from .scrying_glass_statblock_model import validate_snapshot
            snapshot = validate_snapshot(snapshot, self.limits.model())
        except ValueError as exc:
            return 'failed', None, (getattr(exc, 'code', 'invalid_snapshot'), 'The statblock is not valid.', None)
        loop = getattr(self, '_auto_loop', None)
        if loop is not None and not loop.is_closed():
            info['future'] = asyncio.run_coroutine_threadsafe(self._collect_apply(info, snapshot), loop)
        return state, None, error

    async def _collect_apply(self, info, snapshot):
        """Save to every unchanged target without a statblock; hold the others for confirmation.

        -> number saved directly.
        """
        from .scrying_glass_database_transactions import transactional_handler
        from .scrying_glass_statblock_model import StatblockError, content_digest
        service, digest = self, content_digest(snapshot)

        async def collect_added_monster_statblocks():
            try:
                campaign = str(service.context.active_campaign())
            except Exception:
                return 0, []
            if campaign != info['campaign'] or service.encounter_token(campaign) != info['token']:
                return 0, []
            if info['provider'] != FILE and not service.config().enabled.get(info['provider']):
                return 0, []
            monsters, private, saved, held = service._monsters(), service._private(), 0, []
            for ident, species, fields in info['targets']:
                monster = monsters.get(ident)
                if monster is None:
                    continue
                current = private.get(ident)
                reasons = []
                if str(monster.get('monster_species') or '') != species or source_fields(monster) != fields:
                    reasons.append('changed')
                if current:
                    if content_digest(current) == digest:
                        continue  # the same statblock is already saved
                    reasons.append('has_statblock')
                if reasons:
                    held.append((ident, reasons))
                    continue
                service._ensure_private()[ident] = copy.deepcopy(snapshot)
                saved += 1
            return saved, held

        try:
            saved, held = await transactional_handler(self.context, collect_added_monster_statblocks)()
        except (StatblockError, ValueError, RuntimeError) as exc:
            LOG.warning('Statblock collection for added monsters could not be saved: %s', getattr(exc, 'code', exc))
            return 0
        for ident, reasons in held:
            self._hold_collected(info, ident, reasons, snapshot)
        if saved or held:
            from .scrying_glass_statblock_transport import notify
            await notify(self.context)
        return saved

    # -- confirmation of held statblocks -----------------------------------------
    def _collected(self):
        value = getattr(self, '_collected_store', None)
        if value is None:
            value = self._collected_store = OrderedDict()
        return value

    def _hold_collected(self, info, ident, reasons, snapshot):
        store = self._collected()
        for key in [k for k, v in store.items() if v['monster_id'] == ident and v['campaign'] == info['campaign']]:
            del store[key]  # the newest collected statblock replaces an older waiting one
        store[secrets.token_hex(16)] = {
            'campaign': info['campaign'], 'token': info['token'], 'monster_id': ident, 'reasons': reasons,
            'snapshot': snapshot, 'provider': info['provider'], 'expires': self.clock() + self.limits.selection_seconds}
        while len(store) > self.limits.prepared_snapshots:
            store.popitem(last=False)

    def _purge_collected(self):
        store, now = self._collected(), self.clock()
        for key in [k for k, v in store.items() if v['expires'] <= now]:
            del store[key]
        return store

    def collected_list(self, principal):
        """Held statblocks of the active campaign and encounter, newest last."""
        store, token = self._purge_collected(), self.encounter_token(principal.campaign)
        monsters, private, items = self._monsters(), self._private(), []
        for key, entry in list(store.items()):
            if entry['campaign'] != principal.campaign or entry['token'] != token:
                continue
            monster = monsters.get(entry['monster_id'])
            if monster is None:
                del store[key]
                continue
            current = private.get(entry['monster_id'])
            items.append({'collected_id': key, 'monster_id': entry['monster_id'], 'name': monster.get('name'),
                          'species': monster.get('monster_species'), 'reasons': entry['reasons'],
                          'statblock_revision': self.revision(entry['monster_id']),
                          'current_source_label': current.get('source_label') if current else None,
                          'provider': entry['provider'], 'source_label': entry['snapshot']['source_label'],
                          'completeness': entry['snapshot']['completeness'], 'preview': entry['snapshot'],
                          'live': {'name': monster.get('name'), 'species': monster.get('monster_species'),
                                   'ac': monster.get('ac'), 'hp': monster.get('hp'), 'max_hp': monster.get('max_hp'),
                                   'initiative_bonus': monster.get('initiative_bonus')},
                          'expires_at': _iso(self.wall() + max(0.0, entry['expires'] - self.clock()))})
        return {'campaign_id': principal.campaign, 'encounter_token': token, 'items': items}

    def collected_decide(self, principal, collected_id, body):
        """Replace (under the operation lock, in the caller's transaction) or keep the current statblock."""
        if (type(body) is not dict or set(body) != {'decision', 'expected_statblock_revision'}
                or body['decision'] not in ('replace', 'keep')
                or type(body['expected_statblock_revision']) is not int or body['expected_statblock_revision'] < 0):
            raise StatblockAPIError(422, 'invalid_request',
                                    'Expected decision (replace or keep) and expected_statblock_revision.')
        store = self._purge_collected()
        entry = store.get(collected_id) if type(collected_id) is str else None
        if entry is None or entry['campaign'] != principal.campaign:
            raise StatblockAPIError(410, 'collected_expired', 'This collected statblock is no longer available.')
        ident = entry['monster_id']
        if entry['token'] != self.encounter_token(principal.campaign) or ident not in self._monsters():
            del store[collected_id]
            raise StatblockAPIError(409, 'encounter_changed', 'The monster or encounter changed; nothing was replaced.')
        if body['expected_statblock_revision'] != self.revision(ident):
            raise StatblockAPIError(409, 'stale_revision', 'The statblock changed meanwhile; review it again.',
                                    items=[{'monster_id': ident, 'code': 'stale_revision',
                                            'message': 'The statblock changed.'}])
        del store[collected_id]
        if body['decision'] == 'replace':
            self._ensure_private()[ident] = copy.deepcopy(entry['snapshot'])
        return {'collected_id': collected_id, 'monster_id': ident, 'decision': body['decision']}


def collect_after_add(context, created, *, file_bytes=None, filename=None):
    """Best effort from the Add Monster/Import handlers: never fails the add.

    Uses the application's statblock service only when it exists (the server creates it
    at start-up); a context without one (for example a test fixture) collects nothing.
    """
    service = getattr(context, 'statblocks', None)
    if service is None:
        return None
    try:
        return service.collect_new_monsters([m['id'] for m in created], file_bytes=file_bytes, filename=filename)
    except Exception:
        LOG.warning('Statblock collection for added monsters was not started', exc_info=True)
        return None
