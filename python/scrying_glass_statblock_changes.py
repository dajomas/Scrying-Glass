"""Private-aware recovery fingerprints; no persistence or public projection writes."""
import copy
import hashlib
import json
from .scrying_glass_statblock_loading import PrivateEncounterState
from .scrying_glass_statblock_recovery import prepare_capture


def private_signature(state):
    """Return independently validated canonical stored metadata for comparisons."""
    return prepare_capture(state)


def state_changed(before, after):
    """Full state comparison for later save integration, including private metadata."""
    return private_signature(before) != private_signature(after) or dict(before) != dict(after)


def recovery_fingerprint(state):
    """Keep legacy no-content hashes while including canonical private snapshots."""
    from .scrying_glass_feature_rules import normalize_features
    payload = copy.deepcopy(dict(state))
    payload.pop('activity_log', None)
    payload.pop('active_turn_id', None)
    for item in payload.get('monsters', []) + payload.get('characters', []):
        normalize_features(item)
    private = private_signature(state)
    if private:
        payload['_statblocks'] = private
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def prune_private(state):
    """Drop bindings for removed monsters during trusted feature reconciliation."""
    if not isinstance(state, PrivateEncounterState):
        return
    if type(state._statblocks) is not dict or any(
        type(key) is not str or not key.strip() for key in state._statblocks
    ):
        raise ValueError('Invalid internal private snapshot map')
    ids = {item['id'] for item in state.get('monsters', [])}
    state._statblocks = {ident:value for ident,value in state._statblocks.items() if ident in ids}
