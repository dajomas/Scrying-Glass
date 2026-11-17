"""Statblock candidate discovery for the service (SG-TODO-022.08): begin under the lock, run outside it, finish under it."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from .scrying_glass_statblock_contract import (
    REFERENCE_ID, SELECTION_ERRORS, DiscoveryPlan, StatblockAPIError, _iso,
)
from .scrying_glass_statblock_discovery import (
    DNDBEYOND, FIVETOOLS, OPEN5E, ORDER, Discovery, candidate_summary, identity_key, original_identity, source_fields,
)
from .scrying_glass_statblock_fetching import FetchFailure
from .scrying_glass_statblock_limits import DISCOVERY_TARGETS
from .scrying_glass_statblock_selections import SelectionError


class DiscoveringMixin:
    # -- discovery --------------------------------------------------------------
    def discover_begin(self, principal, body):
        if type(body) is not dict or set(body) - {'campaign_id', 'encounter_token', 'monster_ids'}:
            raise StatblockAPIError(422, 'invalid_request', 'Expected campaign_id, encounter_token and monster_ids.')
        self._check_campaign(principal, body.get('campaign_id'))
        self._check_encounter(principal, body.get('encounter_token'))
        ids = body.get('monster_ids')
        if (type(ids) is not list or not ids or any(type(i) is not str or not REFERENCE_ID.match(i) for i in ids)
                or len(set(ids)) != len(ids)):
            raise StatblockAPIError(422, 'invalid_request', 'Select distinct monsters.')
        if len(ids) > DISCOVERY_TARGETS:
            raise StatblockAPIError(413, 'too_many_targets', f'Discover at most {DISCOVERY_TARGETS} monsters at once.')
        monsters, config = self._monsters(), self.config()
        targets = []
        for ident in ids:
            monster = self._target(ident, monsters)
            targets.append((ident, str(monster.get('monster_species') or '').strip(), source_fields(monster),
                            original_identity(monster, config)))
        return DiscoveryPlan(principal, body['encounter_token'], targets, config,
                             self.clock() + self.limits.preparation_seconds)

    def _fetch(self, config, cancelled=lambda: False):
        def fetch(provider, url, deadline):
            if not any(url.startswith(prefix) for prefix in self._prefixes(provider, config)):
                raise FetchFailure('unsafe_url')
            return self.shared.fetch(provider, url, lambda d: self.transport(provider, url, d, root=config.fivetools_root)
                                     if provider == FIVETOOLS else self.transport(provider, url, d),
                                     deadline=deadline, cancelled=cancelled)
        return fetch

    @staticmethod
    def _prefixes(provider, config):
        if provider == FIVETOOLS:
            return (config.fivetools_root + '/',) if config.fivetools_root else ()
        if provider == OPEN5E:
            return (config.open5e_base + '/',) if config.open5e_base else ()
        if provider == DNDBEYOND:
            return ('https://www.dndbeyond.com/', 'https://dndbeyond.com/')
        return ()

    def discover_run(self, plan):
        """Network work outside the lock: one lookup per (provider, species)."""
        discovery = Discovery(plan.config, self._fetch(plan.config), plan.deadline)
        species = sorted({target[1] for target in plan.targets if target[1]})
        jobs = [(provider, name) for name in species for provider in ORDER]
        results = {}
        if jobs:
            with ThreadPoolExecutor(max_workers=max(1, min(len(jobs), self.limits.outbound_requests))) as pool:
                for key, value in zip(jobs, pool.map(lambda job: discovery.run(*job), jobs)):
                    results[key] = value
        return results

    def discover_finish(self, principal, plan, results):
        if principal.campaign != plan.principal.campaign or principal.session != plan.principal.session:
            raise StatblockAPIError(409, 'campaign_changed', 'The active campaign changed; reload.')
        self._check_encounter(principal, plan.encounter_token)
        monsters, complete, out = self._monsters(), True, []
        config = self.config()
        for ident, species, fields, original in plan.targets:
            monster = monsters.get(ident)
            if monster is None or str(monster.get('monster_species') or '').strip() != species or source_fields(monster) != fields:
                out.append({'monster_id': ident, 'status': 'target_changed', 'candidates': [], 'providers': []})
                complete = False
                continue
            scope = self._scope(principal, plan.encounter_token, monster)
            candidates, seen, providers = [], set(), []
            if original is not None:
                provider, identity = original
                seen.add(identity_key(provider, identity))
                summary = candidate_summary(provider, identity, monster.get('monster_source_name') or species or
                                            identity.get('name') or identity.get('key') or identity.get('path'),
                                            original=True)
                if not config.enabled.get(provider):
                    summary['disabled'] = True
                candidates.append(self._issue(scope, provider, identity, summary))
            for provider in ORDER:
                if not species:
                    continue
                result = results.get((provider, species), {'status': 'error', 'code': 'not_run', 'candidates': []})
                row = {'provider': provider, 'status': result['status']}
                for key in ('code', 'omitted_versions'):
                    if key in result:
                        row[key] = result[key]
                if result.get('retry_at') is not None:
                    row['retry_at'] = _iso(self.wall() + max(0.0, result['retry_at'] - self.clock()))
                providers.append(row)
                if result['status'] not in ('complete', 'disabled'):
                    complete = False
                for identity, summary in result['candidates']:
                    key = identity_key(provider, identity)
                    if key in seen:
                        continue
                    seen.add(key)
                    candidates.append(self._issue(scope, provider, identity, summary))
            out.append({'monster_id': ident, 'species': species, 'status': 'ok' if species else 'no_species',
                        'statblock_revision': self.revision(ident), 'candidates': candidates, 'providers': providers})
        return {'campaign_id': principal.campaign, 'encounter_token': plan.encounter_token,
                'complete': complete, 'monsters': out}

    def _issue(self, scope, provider, identity, summary):
        try:
            ident = self.store.add_candidate(scope, provider, identity, summary)
        except SelectionError as exc:
            self._raise_selection(exc)
        return {'candidate_id': ident, **summary}

    @staticmethod
    def _raise_selection(exc, monster_id=None):
        status, message = SELECTION_ERRORS.get(exc.code, (409, 'The prepared statblock is not usable.'))
        items = [{'monster_id': monster_id, 'code': exc.code, 'message': message}] if monster_id else []
        raise StatblockAPIError(status, exc.code, message, items=items) from None

