"""Signed selected-source snapshots; no fetching, entitlement or bonus inference."""
import base64
import hashlib
import hmac
import json
import re
from urllib.parse import unquote

PROVIDER = "monster_source_provider"
URL = "monster_source_url"
NAME = "monster_source_name"
BOOK = "monster_source_book"
LEGACY = "monster_source_legacy"
FIELDS = {PROVIDER, URL, NAME, BOOK, LEGACY}


def _text(value, limit):
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > limit:
        return False
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return not any(ord(char) < 32 or ord(char) == 127 for char in value)


def _source_url(provider, value):
    if not _text(value, 2048):
        return False
    if provider == "D&D Beyond":
        return re.fullmatch(r"https://(?:www\.)?dndbeyond\.com/monsters/[A-Za-z0-9][A-Za-z0-9_-]*", value) is not None
    if provider == "5e.tools":
        return (re.fullmatch(r"https://5e\.tools/bestiary\.html#[A-Za-z0-9_%~.\-]+", value) is not None
                and re.search(r"%(?![0-9A-Fa-f]{2})", value) is None
                and not any(ord(char) < 32 or ord(char) == 127 for char in unquote(value)))
    return False


def capture_source_fields(candidate):
    """Retain only supported exact provider identities; unknown formats stay manual."""
    if not isinstance(candidate, dict):
        return {}
    provider, url = candidate.get("provider"), candidate.get("source_url")
    if not _source_url(provider, url):
        return {}
    result = {PROVIDER: provider, URL: url}
    if _text(candidate.get("name"), 256):
        result[NAME] = candidate["name"]
    if provider == "5e.tools" and _text(candidate.get("source"), 100):
        result[BOOK] = candidate["source"]
    if type(candidate.get("legacy")) is bool:
        result[LEGACY] = candidate["legacy"]
    return result


def validate_source_fields(fields):
    if not isinstance(fields, dict) or set(fields) - FIELDS:
        raise ValueError("Invalid selected source fields")
    if not fields:
        return {}
    candidate = {"provider": fields.get(PROVIDER), "source_url": fields.get(URL)}
    for field, key in ((NAME, "name"), (BOOK, "source"), (LEGACY, "legacy")):
        if field in fields:
            candidate[key] = fields[field]
    result = capture_source_fields(candidate)
    if result != fields:
        raise ValueError("Invalid selected source identity")
    return result


def issue_selection(candidate, key, *, now):
    payload = json.dumps({"species": candidate["species"],
        "image_url": candidate.get("image_url"), "issued": int(now),
        "source_fields": capture_source_fields(candidate)}, separators=(",", ":")).encode()
    data = base64.urlsafe_b64encode(payload).decode()
    return data + "." + hmac.new(key, data.encode(), hashlib.sha256).hexdigest()


def read_selection(token, species, key, *, now, max_age, image_validator):
    if token == "manual":
        return None, {}
    try:
        if not isinstance(token, str) or len(token) > 8192:
            raise ValueError()
        data, signature = token.rsplit(".", 1)
        expected = hmac.new(key, data.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError()
        payload = json.loads(base64.urlsafe_b64decode(data))
        issued = payload["issued"]
        if type(issued) is not int:
            raise ValueError()
        age = now - issued
        if age < -60 or age > max_age or payload["species"] != species.strip():
            raise ValueError()
        image = payload.get("image_url")
        if image is not None and not image_validator(image):
            raise ValueError()
        return image, validate_source_fields(payload.get("source_fields", {}))
    except Exception as exc:
        raise ValueError("Monster selection expired or invalid; repeat lookup or use manual entry.") from exc
