"""Purpose-bound source initiative offers; not user authorization or replay protection."""
import base64
import hashlib
import hmac
import json
import math
from .scrying_glass_initiative_input import creation_bonus_fields
from .scrying_glass_monster_source_snapshot import capture_source_fields, validate_source_fields

PURPOSE = "monster-creation-initiative-v1"


def issue_bonus_offer(candidate, key, *, now):
    """Return no offer for unavailable, untrusted-identity or malformed candidates."""
    if not isinstance(candidate, dict):
        return None
    source = capture_source_fields(candidate)
    species = candidate.get("species")
    bonus = candidate.get("initiative_bonus")
    if (not source or not isinstance(species, str) or not species.strip()
            or len(species) > 100 or candidate.get("initiative_bonus_status") != "available"
            or type(bonus) is not int):
        return None
    try:
        fields = creation_bonus_fields(bonus, origin="source")
    except ValueError:
        return None
    if not math.isfinite(now):
        raise ValueError("Invalid offer clock")
    payload = {"purpose": PURPOSE, "species": species.strip(), "issued": int(now),
               "source_fields": source, "initiative_bonus": fields["initiative_bonus"]}
    data = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
    signature = hmac.new(key, data.encode(), hashlib.sha256).hexdigest()
    return data + "." + signature


def read_bonus_offer(token, species, key, *, now, max_age):
    """Verify before returning source-origin fields; no fetching or state mutation."""
    try:
        if (not isinstance(token, str) or len(token) > 8192
                or not isinstance(species, str) or not math.isfinite(now)
                or not math.isfinite(max_age) or max_age < 0):
            raise ValueError()
        data, signature = token.rsplit(".", 1)
        expected = hmac.new(key, data.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError()
        payload = json.loads(base64.b64decode(data, altchars=b"-_", validate=True))
        if (not isinstance(payload, dict) or set(payload) != {
                "purpose", "species", "issued", "source_fields", "initiative_bonus"}
                or payload["purpose"] != PURPOSE or type(payload["issued"]) is not int
                or payload["species"] != species.strip()
                or not -60 <= now - payload["issued"] <= max_age
                or type(payload["initiative_bonus"]) is not int):
            raise ValueError()
        source = validate_source_fields(payload["source_fields"])
        if not source:
            raise ValueError()
        return {**source, **creation_bonus_fields(payload["initiative_bonus"], origin="source")}
    except Exception as exc:
        raise ValueError("Initiative offer expired or invalid; repeat lookup or use manual entry.") from exc
