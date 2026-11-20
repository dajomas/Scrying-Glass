"""Statblock discovery, preparation, selection and atomic apply (SG-TODO-022.08).

Request methods run under the operation lock (routes wrap them); network work
(``discover_run`` and preparation jobs) never does. Every use of a server-held
reference rechecks, for the current request: a regular admin (not superadmin
or client) with a live session and access to the active campaign; the active
campaign and encounter token; the target monster, its species and its
original-source identity; the statblock revision; the provider switch.

Errors are ``StatblockAPIError`` envelopes:
``{code, message, items:[{monster_id, code, message, source_path?}], retry_at?}``
with 401/403/404/409/410/413/422/429/504 statuses. Remote content and session
tokens never appear in an error.
"""
from __future__ import annotations

import copy
import hashlib
import hmac
import json
import secrets
import threading
import time

from .scrying_glass_statblock_applying import ApplyingMixin
from .scrying_glass_statblock_autoloading import AutoLoadingMixin
from .scrying_glass_statblock_collecting import CollectingMixin
from .scrying_glass_statblock_contract import (  # noqa: F401 - re-exported for routes and tests
    ADAPTERS, FAILURE_MESSAGES, SELECTION_ERRORS, Principal, PreparationFailure, StatblockAPIError, commit_callback,
)
from .scrying_glass_statblock_discovering import DiscoveringMixin
from .scrying_glass_statblock_discovery import default_transport, provider_config, source_fields
from .scrying_glass_statblock_fetching import SharedFetcher
from .scrying_glass_statblock_jobs import JobScheduler
from .scrying_glass_statblock_limits import StatblockLimits
from .scrying_glass_statblock_preparing import PreparingMixin
from .scrying_glass_statblock_selections import Scope, SelectionStore, session_key


class StatblockService(DiscoveringMixin, PreparingMixin, ApplyingMixin, AutoLoadingMixin, CollectingMixin):
    def __init__(self, context, *, limits=None, transport=None, runner=None, display=None,
                 clock=time.monotonic, wall=time.time):
        self.context = context
        self.limits = limits if limits is not None else StatblockLimits.from_config(getattr(context, 'CONFIG', {}))
        self.clock, self.wall = clock, wall
        self.shared = SharedFetcher(self.limits, clock=clock)
        self.store = SelectionStore(self.limits, clock=clock, wall=wall)
        self.scheduler = JobScheduler(active=self.limits.active_jobs, queued=self.limits.queued_jobs, clock=clock,
                                      on_finish=self._finished)
        self.transport = transport or default_transport(self.limits)
        self.runner = runner or self._run_isolated
        self._display = display
        self._jobs = {}
        self._jobs_lock = threading.Lock()
        self._key = secrets.token_bytes(32)

    # -- context -----------------------------------------------------------------
    def display(self):
        if self._display is not None:
            return self._display()
        from .scrying_glass_provider_settings import effective_display
        return effective_display(self.context)

    def config(self):
        return provider_config(self.display())

    def authorize(self, token, campaign_id=None):
        context = self.context
        session = context.auth_session(token) if type(token) is str and token else None
        if not session:
            raise StatblockAPIError(401, 'unauthenticated', 'Sign in required.')
        user = context.user(session['username'])
        if not user or user.get('role') != session.get('role'):
            raise StatblockAPIError(401, 'unauthenticated', 'Sign in required.')
        if user['role'] != 'admin':
            raise StatblockAPIError(403, 'regular_admin_required',
                                    'Statblocks require a regular admin account assigned to the campaign.')
        from .scrying_glass_campaign_ownership import ownership
        try:
            active = str(context.active_campaign())
        except Exception:
            raise StatblockAPIError(409, 'no_active_campaign', 'No campaign is active.') from None
        owners = ownership(context)
        if not owners.allowed(active, user):
            raise StatblockAPIError(403, 'campaign_forbidden', 'This campaign is not assigned to your admin account.')
        if campaign_id is not None and str(campaign_id) != active:
            if type(campaign_id) is str and campaign_id.isdecimal() and owners.allowed(campaign_id, user):
                raise StatblockAPIError(409, 'campaign_changed', 'The active campaign changed; reload.')
            raise StatblockAPIError(403, 'campaign_forbidden', 'This campaign is not assigned to your admin account.')
        return Principal(token, session_key(token), str(user['id']), user['username'], active)

    def encounter_token(self, campaign):
        reference = self.context.active_setup_reference()
        material = json.dumps([str(campaign), [reference.get('campaign_id'), reference.get('name')] if reference else None])
        return hmac.new(self._key, material.encode(), hashlib.sha256).hexdigest()[:40]

    def _check_campaign(self, principal, value):
        if value is None or str(value) != principal.campaign:
            raise StatblockAPIError(409, 'campaign_changed', 'The active campaign changed; reload.')

    def _check_encounter(self, principal, value):
        if value != self.encounter_token(principal.campaign):
            raise StatblockAPIError(409, 'encounter_changed', 'The encounter changed; reload before importing.')

    def _monsters(self):
        return {item['id']: item for item in self.context.STATE.get('monsters', []) if isinstance(item, dict)}

    def _private(self):
        from .scrying_glass_statblock_loading import PrivateEncounterState
        state = self.context.STATE
        return state._statblocks if isinstance(state, PrivateEncounterState) else {}

    def revision(self, monster_id):
        value = self._private().get(monster_id)
        return value.get('revision', 0) if value else 0

    def _ensure_private(self):
        """Attach stored private metadata to a plain trusted state before a write."""
        from .scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
        from .scrying_glass_statblock_loading import PrivateEncounterState
        state = self.context.STATE
        if isinstance(state, PrivateEncounterState):
            return state._statblocks
        storage = self.context.STORAGE
        reference = self.context.active_setup_reference()
        if reference is not None:
            row = storage.connection.execute('SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',
                                             (reference['campaign_id'], reference['name'])).fetchone()
        else:
            row = storage.connection.execute('SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()
        stored = {}
        if row is not None and row[0] is not None:
            stored = PrivateEncounterStorage(storage).load(row[0])[PRIVATE_KEY]
        self.context.STATE = PrivateEncounterState(state, stored)
        return self.context.STATE._statblocks

    def _target(self, monster_id, monsters=None):
        monster = (monsters or self._monsters()).get(monster_id) if type(monster_id) is str else None
        if monster is None:
            raise StatblockAPIError(404, 'monster_not_found', 'Monster not found in this encounter.',
                                    items=[{'monster_id': monster_id if type(monster_id) is str else None,
                                            'code': 'monster_not_found', 'message': 'Monster not found.'}])
        return monster

    def _scope(self, principal, token, monster):
        return Scope(principal.session, principal.user_id, principal.campaign, token, monster['id'],
                     str(monster.get('monster_species') or ''), source_fields(monster))

    # -- reads ----------------------------------------------------------------------
    @staticmethod
    def _status(snapshot):
        return snapshot['completeness'] if snapshot else 'missing'

    def state_projection(self, principal):
        features = getattr(self.context, 'features', None)
        try:
            projection = features.store.revision() if features is not None else 0
        except Exception:
            projection = 0
        private, config = self._private(), self.config()
        tiles, monsters = [], []
        for item in self.context.STATE.get('monsters', []):
            snapshot = private.get(item['id'])
            summary = {'monster_id': item['id'], 'statblock_revision': snapshot.get('revision', 0) if snapshot else 0,
                       'status': self._status(snapshot), 'warnings': len(snapshot['warnings']) if snapshot else 0}
            if snapshot is None:
                summary['status'], detail = self.original_status(item, principal.campaign, config)
                if detail:
                    summary['status_detail'] = detail
            monsters.append(summary)
            member = item.get('active') and (item.get('alive') or item.get('life_state') in ('down', 'stable'))
            if member:
                tiles.append({**summary, 'name': item.get('name'), 'species': item.get('monster_species'),
                              'color': item.get('color'), 'ac': item.get('ac'), 'hp': item.get('hp'),
                              'max_hp': item.get('max_hp'), 'initiative_bonus': item.get('initiative_bonus')})
        return {'campaign_id': principal.campaign, 'encounter_token': self.encounter_token(principal.campaign),
                'projection_revision': projection, 'tiles': tiles, 'monsters': monsters}

    def monster_projection(self, principal, monster_id, known_revision=None):
        monster = self._target(monster_id)
        snapshot = copy.deepcopy(self._private().get(monster_id))
        revision = snapshot.get('revision', 0) if snapshot else 0
        live = {'name': monster.get('name'), 'species': monster.get('monster_species'), 'ac': monster.get('ac'),
                'hp': monster.get('hp'), 'max_hp': monster.get('max_hp'),
                'initiative_bonus': monster.get('initiative_bonus')}
        result = {'monster_id': monster_id, 'encounter_token': self.encounter_token(principal.campaign),
                  'live': live, 'statblock_revision': revision, 'status': self._status(snapshot)}
        if snapshot is None:
            result['status'], detail = self.original_status(monster, principal.campaign)
            if detail:
                result['status_detail'] = detail
        if snapshot and known_revision == revision:
            result['unchanged'] = True
        elif snapshot:
            result['statblock'] = snapshot
            result['source'] = self._source(snapshot)
        return result

    @staticmethod
    def _source(snapshot):
        selected = next((row for row in snapshot.get('provenance', []) if row.get('role') == 'selected'),
                        (snapshot.get('provenance') or [{}])[0])
        keys = ('provider', 'entity_id', 'source_code', 'edition', 'source_url', 'file_name', 'adapter_version')
        source = {key: selected.get(key) for key in keys if selected.get(key) is not None}
        source['credits'] = [{k: v for k, v in credit.items() if k != 'position' and v is not None}
                             for credit in selected.get('credits', [])]
        return source



def statblock_service(context):
    """The application's single service, created on first use from context.CONFIG."""
    service = getattr(context, 'statblocks', None)
    if service is None:
        service = context.statblocks = StatblockService(context)
    return service
