"""Automatic original-source statblock loading (SG-TODO-022.12).

While at least one statblock-listener socket is connected, every committed
change (and every new connection) checks the battle's tile monsters. A tile
monster without a saved statblock whose tracker source fields hold an exact
identity (``monster_source_*``) is prepared once from that identity only, with
the shared job scheduler, fetcher and isolated workers, and saved when it
completes -- if the campaign, encounter, monster, species, source identity and
"no statblock yet" still hold. Nothing else is searched or substituted.

Per (campaign, encounter token, monster, identity): one attempt at a time; a
transient failure waits ``failure_cooldown_seconds`` before the next event may
retry; an unavailable record (not found, no public statblock, provider
disabled) is not retried until the encounter or identity changes. A full queue
just leaves the monster for the next event. The tile status shows
``loading``, ``error`` (with retry time) or ``unavailable``.
"""
from __future__ import annotations

import asyncio
import copy

from .scrying_glass_statblock_contract import FAILURE_MESSAGES, _iso, _now_iso
from .scrying_glass_statblock_discovery import identity_key, original_identity, source_fields
from .scrying_glass_statblock_jobs import Job, JobCapacity

UNAVAILABLE = frozenset(('not_found', 'selected_unavailable', 'statblock_unavailable', 'provider_disabled',
                         'identity_mismatch', 'malformed_file'))
AUTO_OWNER = 'automatic-original-source'


def member(monster):
    return bool(monster.get('active') and (monster.get('alive') or monster.get('life_state') in ('down', 'stable')))


class AutoLoadingMixin:
    def _auto_states(self):
        value = getattr(self, '_auto', None)
        if value is None:
            value = self._auto = {}
        return value

    def _auto_key(self, campaign, token, monster, config):
        original = original_identity(monster, config)
        if original is None:
            return None, None
        provider, identity = original
        return (campaign, token, monster['id'], identity_key(provider, identity)), original

    def original_status(self, monster, campaign=None, config=None):
        """Operational status for a monster without a saved statblock: (status, detail)."""
        try:
            campaign = campaign or str(self.context.active_campaign())
        except Exception:
            return 'missing', None
        config = config or self.config()
        key, original = self._auto_key(campaign, self.encounter_token(campaign), monster, config)
        if key is None:
            return 'missing', None
        state = self._auto_states().get(key)
        if state is None:
            if not config.enabled.get(original[0]):
                return 'unavailable', {'code': 'provider_disabled', 'message': f'{original[0]} is disabled.'}
            return 'missing', None
        detail = {key_: state[key_] for key_ in ('code', 'message') if state.get(key_)}
        if state.get('until') is not None and state['state'] == 'error':
            detail['retry_at'] = _iso(self.wall() + max(0.0, state['until'] - self.clock()))
        return state['state'], detail or None

    def schedule_original_loads(self):
        """Call under the operation lock from async code (the transport does)."""
        try:
            campaign = str(self.context.active_campaign())
        except Exception:
            return 0
        self._auto_loop = asyncio.get_running_loop()
        token, config, now = self.encounter_token(campaign), self.config(), self.clock()
        states = self._auto_states()
        for key in [k for k, v in states.items() if (k[0], k[1]) != (campaign, token) and v['state'] != 'loading']:
            del states[key]
        private, started = self._private(), 0
        for monster in self.context.STATE.get('monsters', []):
            if not isinstance(monster, dict) or not member(monster) or private.get(monster.get('id')):
                continue
            key, original = self._auto_key(campaign, token, monster, config)
            if key is None:
                continue
            state = states.get(key)
            if state is not None and (state['state'] in ('loading', 'unavailable') or
                                      (state.get('until') is not None and state['until'] > now)):
                continue
            provider, identity = original
            if not config.enabled.get(provider):
                continue  # shown as unavailable; retried once the provider is enabled again
            info = {'auto': True, 'key': key, 'provider': provider, 'identity': identity, 'config': config,
                    'campaign': campaign, 'token': token, 'monster_id': monster['id'],
                    'species': str(monster.get('monster_species') or ''), 'fields': source_fields(monster)}
            job = Job(AUTO_OWNER, self._work, deadline=now + self.limits.preparation_seconds, info=info)
            try:
                self.scheduler.submit(job)
            except JobCapacity:
                break  # nothing evicted; the next event tries again
            states[key] = {'state': 'loading', 'job': job}
            started += 1
        return started

    def _auto_finished(self, job, state, result, error):
        """Scheduler callback (worker thread): record failures, hand successes to the event loop."""
        info, states = job.info, self._auto_states()
        if state != 'completed':
            code = error[0] if error else 'preparation_failed'
            entry = {'state': 'unavailable' if code in UNAVAILABLE else 'error', 'code': code,
                     'message': FAILURE_MESSAGES.get(code, 'The original statblock could not be loaded.')}
            if entry['state'] == 'error':
                entry['until'] = self.clock() + self.limits.failure_cooldown_seconds
            states[info['key']] = entry
            self._auto_notify()
            return state, None, error
        snapshot = copy.deepcopy(result['snapshot'])
        snapshot.pop('revision', None)
        snapshot['prepared_at'] = _now_iso()
        loop = getattr(self, '_auto_loop', None)
        if loop is None or loop.is_closed():
            states.pop(info['key'], None)
            return state, None, error
        asyncio.run_coroutine_threadsafe(self._auto_apply(info, snapshot), loop)
        return state, None, error

    def _auto_notify(self):
        loop = getattr(self, '_auto_loop', None)
        if loop is not None and not loop.is_closed():
            from .scrying_glass_statblock_transport import notify
            asyncio.run_coroutine_threadsafe(notify(self.context), loop)

    async def _auto_apply(self, info, snapshot):
        from .scrying_glass_database_transactions import transactional_handler
        from .scrying_glass_statblock_model import StatblockError, validate_snapshot
        states, service = self._auto_states(), self
        async def load_original_statblock():
            monsters = service._monsters()
            monster = monsters.get(info['monster_id'])
            try:
                campaign = str(service.context.active_campaign())
            except Exception:
                return False
            if (campaign != info['campaign'] or service.encounter_token(campaign) != info['token'] or monster is None
                    or str(monster.get('monster_species') or '') != info['species']
                    or source_fields(monster) != info['fields'] or service.revision(monster['id']) != 0
                    or not member(monster) or not service.config().enabled.get(info['provider'])):
                return False
            service._ensure_private()[monster['id']] = validate_snapshot(snapshot, service.limits.model())
            return True
        try:
            saved = await transactional_handler(self.context, load_original_statblock)()
        except (StatblockError, ValueError, RuntimeError) as exc:
            states[info['key']] = {'state': 'error', 'code': getattr(exc, 'code', 'save_failed'),
                                   'message': 'The original statblock could not be saved.',
                                   'until': self.clock() + self.limits.failure_cooldown_seconds}
            from .scrying_glass_statblock_transport import notify
            await notify(self.context)
            return False
        states.pop(info['key'], None)
        if not saved:
            from .scrying_glass_statblock_transport import notify
            await notify(self.context)
        return saved
