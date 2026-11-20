"""Shared statblock API contract: error envelope, constants and helpers (SG-TODO-022.08)."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from .scrying_glass_statblock_discovery import DNDBEYOND, FILE, FIVETOOLS, OPEN5E

OPERATION_ID = re.compile(r'[A-Za-z0-9_-]{1,128}\Z')
REFERENCE_ID = re.compile(r'[A-Za-z0-9_-]{1,128}\Z')
ADAPTERS = {FIVETOOLS: '5etools-04f-1', OPEN5E: 'open5e-v2-05-1', DNDBEYOND: 'dndbeyond-06-2', FILE: 'tetracube-07-1'}
LIVE_FIELDS = ('name', 'monster_species', 'ac', 'hp', 'max_hp', 'initiative_bonus')
EDITABLE_EXPECTED = frozenset(('name', 'monster_species', 'ac', 'hp', 'max_hp', 'original_hp', 'color',
                               'initiative', 'initiative_bonus', 'ally'))
SELECTION_ERRORS = {
    'candidate_expired': (410, 'The candidate expired; repeat discovery.'),
    'candidate_capacity': (429, 'Too many discovered candidates are held; try again later.'),
    'selection_expired': (410, 'The prepared statblock expired or was already used; prepare it again.'),
    'selection_forbidden': (403, 'The prepared statblock belongs to another session.'),
    'session_selection_capacity': (429, 'This session holds the maximum number of prepared statblocks.'),
    'selection_capacity': (429, 'The server holds the maximum number of prepared statblocks.'),
    'prepared_capacity': (429, 'Prepared statblock storage is full; try again later.'),
}
FAILURE_MESSAGES = {
    'deadline': 'The preparation deadline passed.',
    'cancelled': 'Preparation cancelled.',
    'cooldown': 'The source failed recently; retry later.',
    'not_found': 'The source record was not found.',
    'provider_unavailable': 'The source could not be reached.',
    'provider_error': 'The source returned an error.',
    'malformed_response': 'The source returned malformed data.',
    'malformed_file': 'The file is not a valid .monster file.',
    'file_too_large': 'The file is larger than 5 MiB.',
    'statblock_unavailable': 'The page has no public statblock.',
    'worker_enforcement_unavailable': 'Isolated preparation is not available on this platform.',
    'worker_memory_limit': 'The preparation exceeded its memory limit.',
    'worker_start_failed': 'The preparation worker could not be started.',
    'worker_resource_or_start_failure': 'The preparation worker stopped unexpectedly (start failure or resource limit).',
    'worker_protocol_error': 'The preparation worker returned an invalid answer.',
    'worker_transport_limit': 'The preparation worker exceeded its transfer limit.',
    'worker_internal_error': 'The preparation worker failed internally.',
    'worker_input_invalid': 'The preparation worker rejected its input.',
    'snapshot_limit': 'The statblock exceeds the snapshot size limit.',
    'node_limit': 'The statblock exceeds the content node limit.',
    'depth_limit': 'The statblock exceeds the content depth limit.',
    'session_revoked': 'The session ended before preparation completed.',
    'reference_unavailable': 'A required source file was not available.',
    'selected_unavailable': 'The selected source record was not found.',
    'identity_mismatch': 'The source returned a different record.',
    'response_bytes_limit': 'A source response exceeded the size limit.',
    'unsafe_url': 'The source address is not allowed.',
    'unsafe_redirect': 'The source redirected to an address that is not allowed.',
}


class StatblockAPIError(Exception):
    def __init__(self, status, code, message, *, items=None, retry_at=None):
        self.status, self.code, self.message = status, code, message
        self.items, self.retry_at = list(items or []), retry_at
        super().__init__(code)

    def envelope(self):
        body = {'code': self.code, 'message': self.message, 'items': self.items}
        if self.retry_at is not None:
            body['retry_at'] = self.retry_at
        return body


def _iso(wall):
    return datetime.fromtimestamp(wall, timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class Principal:
    token: str
    session: str
    user_id: str
    username: str
    campaign: str


@dataclass
class DiscoveryPlan:
    principal: Principal
    encounter_token: str
    targets: list  # [(monster_id, species, source_fields, original)]
    config: object
    deadline: float


def commit_callback(context, callback):
    """Run callback after the surrounding transactional handler commits."""
    callbacks = getattr(context, '_commit_callbacks', None)
    if callbacks is None:
        raise RuntimeError('Statblock writes require a transactional handler')
    callbacks.append(callback)




class PreparationFailure(Exception):
    def __init__(self, code, retry_at=None):
        self.code, self.retry_at = code, retry_at
        self.message = FAILURE_MESSAGES.get(code, f'Preparation failed ({code}).')
        super().__init__(code)


