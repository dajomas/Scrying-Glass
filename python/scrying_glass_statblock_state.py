"""Opt-in private-state normalization; production callers are not wired yet."""
import json
from .scrying_glass_statblock_model import canonical_bytes, content_digest, validate_snapshot
from .scrying_glass_statblock_encounters import PRIVATE_KEY, public_payload


def prepare_private_state(requested, monster_ids, limits=None):
    """Validate a separate map with caller-controlled preparation limits."""
    if type(requested) is not dict or any(type(key) is not str or not key.strip() for key in requested):
        raise ValueError("Invalid private statblock map")
    if set(requested) - set(monster_ids):
        raise ValueError("Statblock target is not a normalized monster")
    prepared = {}
    for combatant_id, raw in requested.items():
        canonical = json.loads(canonical_bytes(raw, limits))
        canonical["content_digest"] = content_digest(canonical, limits)
        prepared[combatant_id] = validate_snapshot(canonical, limits)
    return prepared


def normalize_state(context, raw, *, private_snapshots=None, limits=None):
    """Normalize ordinary input and attach separately supplied internal snapshots.

    Not an authorization boundary. New untrusted preparations must receive
    validated server limits; trusted stored-state read policy is not selected here.
    """
    if not isinstance(raw, dict):
        raise ValueError("State must contain a JSON object")
    if PRIVATE_KEY in raw:
        raise ValueError("Reserved private statblock field is not accepted in ordinary state")
    normalized = context.normalize_state(raw)
    normalized[PRIVATE_KEY] = prepare_private_state(
        {} if private_snapshots is None else private_snapshots,
        {item["id"] for item in normalized["monsters"]}, limits,
    )
    return normalized


def response_payload(value):
    """Copy ordinary payloads without reserved private keys at any depth."""
    return public_payload(value)
