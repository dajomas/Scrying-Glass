"""Atomic statblock apply and Edit Monster staging for the service (SG-TODO-022.08)."""
from __future__ import annotations

import copy
import json

from .scrying_glass_statblock_contract import (
    EDITABLE_EXPECTED, OPERATION_ID, SELECTION_ERRORS, StatblockAPIError, _digest, commit_callback,
)
from .scrying_glass_statblock_discovery import FILE, source_fields
from .scrying_glass_statblock_limits import APPLY_TARGETS
from .scrying_glass_statblock_selections import SelectionError


class ApplyingMixin:
    # -- apply ---------------------------------------------------------------------
    def _check_binding(self, principal, encounter_token, monster, expected, selection_id, config):
        """-> (binding, None) or (None, item error)."""
        ident = monster['id']
        def fail(code, message, status=409):
            return None, (status, {'monster_id': ident, 'code': code, 'message': message})
        try:
            binding = self.store.binding(selection_id, principal.session)
        except SelectionError as exc:
            status, message = SELECTION_ERRORS.get(exc.code, (409, 'Not usable.'))
            return fail(exc.code, message, status)
        scope = binding.scope
        if (scope.user_id, scope.campaign, scope.encounter_token, scope.monster_id) != (
                principal.user_id, principal.campaign, encounter_token, ident):
            return fail('selection_mismatch', 'The prepared statblock belongs to another monster or encounter.')
        if (scope.species, scope.source_identity) != (str(monster.get('monster_species') or ''), source_fields(monster)):
            return fail('target_changed', 'The monster species or source changed; prepare again.')
        if type(expected) is not int or expected != binding.expected_revision or expected != self.revision(ident):
            return fail('stale_revision', 'The statblock changed since preparation; prepare again.')
        provider = binding.summary.get('provider')
        if provider != FILE and not config.enabled.get(provider):
            return fail('provider_disabled', f'{provider} is disabled.')
        return binding, None

    def apply(self, principal, body):
        if type(body) is not dict or set(body) != {'operation_id', 'campaign_id', 'encounter_token', 'items'}:
            raise StatblockAPIError(422, 'invalid_request', 'Expected operation_id, campaign_id, encounter_token and items.')
        operation = body['operation_id']
        if type(operation) is not str or not OPERATION_ID.match(operation):
            raise StatblockAPIError(422, 'invalid_request', 'operation_id must be 1-128 letters, digits, - or _.')
        items = body['items']
        if type(items) is not list or not items:
            raise StatblockAPIError(422, 'invalid_request', 'Select at least one statblock to apply.')
        if len(items) > APPLY_TARGETS:
            raise StatblockAPIError(413, 'too_many_targets', f'Apply at most {APPLY_TARGETS} statblocks per request.')
        for item in items:
            if (type(item) is not dict or set(item) != {'monster_id', 'expected_statblock_revision', 'selection_id'}
                    or type(item['monster_id']) is not str or type(item['selection_id']) is not str
                    or type(item['expected_statblock_revision']) is not int or item['expected_statblock_revision'] < 0):
                raise StatblockAPIError(422, 'invalid_request',
                                        'Each item needs monster_id, expected_statblock_revision and selection_id.')
        if (len({item['monster_id'] for item in items}) != len(items)
                or len({item['selection_id'] for item in items}) != len(items)):
            raise StatblockAPIError(422, 'duplicate_target', 'Each monster and selection may appear once.')
        digest = _digest({'campaign_id': body['campaign_id'], 'encounter_token': body['encounter_token'], 'items': items})
        recorded = self.store.outcome(principal.session, operation)
        if recorded is not None:
            if recorded.digest != digest:
                raise StatblockAPIError(409, 'operation_conflict', 'This operation_id was used for a different request.')
            return copy.deepcopy(recorded.result)
        self._check_campaign(principal, body['campaign_id'])
        self._check_encounter(principal, body['encounter_token'])
        monsters, config, errors, bindings = self._monsters(), self.config(), [], []
        for item in items:
            monster = monsters.get(item['monster_id'])
            if monster is None:
                errors.append((404, {'monster_id': item['monster_id'], 'code': 'monster_not_found',
                                     'message': 'Monster not found.'}))
                continue
            binding, error = self._check_binding(principal, body['encounter_token'], monster,
                                                 item['expected_statblock_revision'], item['selection_id'], config)
            if error is not None:
                errors.append(error)
            else:
                bindings.append((item, binding))
        if errors:
            statuses = {status for status, _ in errors}
            status = statuses.pop() if len(statuses) == 1 else 409
            raise StatblockAPIError(status, 'apply_rejected', 'No statblocks were changed.',
                                    items=[row for _, row in errors])
        consumed = [binding.id for _, binding in bindings]
        try:
            self.store.reserve_outcome(principal.session, operation, consumed)
            snapshots = [(item, self.store.snapshot(binding)) for item, binding in bindings]
        except SelectionError as exc:
            self._raise_selection(exc)
        private = self._ensure_private()
        for item, snapshot in snapshots:
            private[item['monster_id']] = snapshot
        result = {'operation_id': operation, 'applied': []}
        def finish():
            current = self._private()
            result['applied'] = [{'monster_id': item['monster_id'],
                                  'statblock_revision': current.get(item['monster_id'], {}).get('revision', 0)}
                                 for item, _ in snapshots]
            self.store.finish_apply(principal.session, operation, digest, consumed, result)
        commit_callback(self.context, finish)
        return result

    # -- Edit Monster ------------------------------------------------------------------
    @staticmethod
    def _check_expected(monster, expected_values):
        """Reject the save when an explicitly edited field no longer has its previous value."""
        if not expected_values:
            return
        try:
            expected = json.loads(expected_values)
        except ValueError:
            raise StatblockAPIError(422, 'invalid_request', 'expected_values must be a JSON object.') from None
        if type(expected) is not dict or set(expected) - EDITABLE_EXPECTED:
            raise StatblockAPIError(422, 'invalid_request', 'expected_values names unknown fields.')
        conflicts = [key for key, value in expected.items() if monster.get(key) != value]
        if conflicts:
            raise StatblockAPIError(409, 'edit_conflict', 'The monster changed meanwhile; reload before saving.',
                                    items=[{'monster_id': monster['id'], 'code': 'edit_conflict',
                                            'message': 'Changed: ' + ', '.join(sorted(conflicts))}])

    def stage_edit(self, token, monster, fields):
        """Validate an Edit Monster save's staged statblock and explicit expected values.

        fields: selection_id, operation_id, expected_revision (text), expected_values (JSON text),
        each possibly ''. Returns None (nothing staged), {'replay': result} or a plan whose
        install() must be called after the ordinary edit has been applied.
        """
        selection = (fields.get('selection_id') or '').strip()
        expected_values = (fields.get('expected_values') or '').strip()
        if not selection and not expected_values:
            if (fields.get('operation_id') or '').strip() or (fields.get('expected_revision') or '').strip():
                raise StatblockAPIError(422, 'invalid_request', 'A staged statblock needs a selection.')
            return None
        if not selection:
            self._check_expected(monster, expected_values)
            return None
        principal = self.authorize(token)
        operation = (fields.get('operation_id') or '').strip()
        if not OPERATION_ID.match(operation):
            raise StatblockAPIError(422, 'invalid_request', 'A staged statblock needs an operation_id.')
        try:
            revision = int((fields.get('expected_revision') or '').strip())
        except ValueError:
            raise StatblockAPIError(422, 'invalid_request', 'expected_statblock_revision must be an integer.') from None
        digest = _digest({'edit': monster['id'], 'selection_id': selection, 'expected': revision,
                          'expected_values': expected_values})
        recorded = self.store.outcome(principal.session, operation)
        if recorded is not None:
            if recorded.digest != digest:
                raise StatblockAPIError(409, 'operation_conflict', 'This operation_id was used for a different request.')
            return {'replay': copy.deepcopy(recorded.result)}
        self._check_expected(monster, expected_values)
        token_value = self.encounter_token(principal.campaign)
        binding, error = self._check_binding(principal, token_value, monster, revision, selection, self.config())
        if error is not None:
            raise StatblockAPIError(error[0], 'apply_rejected', 'The monster and its statblock were not changed.',
                                    items=[error[1]])
        try:
            self.store.reserve_outcome(principal.session, operation, [binding.id])
            snapshot = self.store.snapshot(binding)
        except SelectionError as exc:
            self._raise_selection(exc, monster['id'])
        service = self
        class Plan:
            def install(self, result):
                service._ensure_private()[monster['id']] = snapshot
                def finish():
                    stored = copy.deepcopy(result)
                    stored['statblock_revision'] = service.revision(monster['id'])
                    service.store.finish_apply(principal.session, operation, digest, [binding.id], stored)
                commit_callback(service.context, finish)
        return Plan()


