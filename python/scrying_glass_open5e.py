"""Optional Open5e v2 API provider (SG-TODO-017). No Open5e data is bundled.

The API silently ignores unsupported filters, so every returned creature is
validated (exact normalized name, document identity, numeric statistics)
instead of trusting the query. Candidates carry document, game-system,
publisher and licence attribution for display with each choice.
"""
from __future__ import annotations
import json
import re
import threading
import time
from collections import OrderedDict
from urllib.parse import quote, urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen
from .scrying_glass_initiative_input import creation_bonus_fields

DEFAULT_BASE_URL = "https://api.open5e.com/v2"
CANONICAL_BASE_URL = DEFAULT_BASE_URL
PROVIDER = "Open5e"
FIELDS = "key,name,document,armor_class,hit_points,hit_dice,initiative_bonus,illustration"
MAX_BYTES = 4_000_000
MAX_PAGES = 10
KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,199}")
DICE = re.compile(r"([1-9]\d{0,3})d([1-9]\d{0,3})(?:([+-])(\d{1,5}))?", re.I)
_CACHE = OrderedDict()
_LOCK = threading.RLock()


class Open5eError(ValueError):
    """Incomplete or unsupported Open5e response; never a zero-match result."""


def normalized(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).casefold()).strip()


def base_url(display):
    value = display.get("open5e_base_url", DEFAULT_BASE_URL)
    parts = urlsplit(value) if isinstance(value, str) else None
    if (parts is None or parts.scheme != "https" or not parts.hostname or parts.username
            or parts.password or parts.query or parts.fragment):
        raise Open5eError("open5e_base_url must be an HTTPS URL without credentials, query or fragment")
    return value.rstrip("/")


def load_json(url):
    """Fetch bounded JSON with a one-hour cache separate from 5e.tools files."""
    with _LOCK:
        cached = _CACHE.get(url)
        if cached and cached[0] > time.monotonic():
            _CACHE.move_to_end(url)
            return cached[1]
    request = Request(url, headers={"User-Agent": "ScryingGlass/1.0", "Accept": "application/json"})
    with urlopen(request, timeout=10) as response:
        if urlsplit(response.geturl()).hostname != urlsplit(url).hostname:
            raise Open5eError("Unexpected Open5e redirect")
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise Open5eError("Open5e response exceeds 4 MB")
    data = json.loads(raw)
    with _LOCK:
        _CACHE[url] = (time.monotonic() + 3600, data)
        _CACHE.move_to_end(url)
        while len(_CACHE) > 64:
            _CACHE.popitem(last=False)
    return data


def _pages(url, base, limit=None):
    """Follow `next` on the configured host until null; reject partial lists."""
    results, pages = [], 0
    while url is not None:
        pages += 1
        if pages > MAX_PAGES:
            raise Open5eError("Open5e listing exceeded the page limit")
        if urlsplit(url).scheme != "https" or urlsplit(url).hostname != urlsplit(base).hostname:
            raise Open5eError("Open5e pagination left the configured host")
        data = load_json(url)
        if (not isinstance(data, dict) or type(data.get("count")) is not int
                or not isinstance(data.get("results"), list)):
            raise Open5eError("Invalid Open5e listing")
        if limit is not None and data["count"] > limit:
            raise Open5eError("Open5e returned too many candidates; refine the species.")
        results.extend(data["results"])
        url = data.get("next")
        if url is not None and not isinstance(url, str):
            raise Open5eError("Invalid Open5e pagination")
    if len(results) != data["count"]:
        raise Open5eError("Incomplete Open5e listing")
    return results


def _text(value, limit=200):
    return value if isinstance(value, str) and value.strip() and len(value) <= limit else None


def documents(base):
    """Document key -> attribution, from the documents catalog."""
    catalog = {}
    for item in _pages(base + "/documents/?" + urlencode({"limit": 200, "format": "json"}), base):
        key = item.get("key") if isinstance(item, dict) else None
        if not isinstance(key, str) or not KEY.fullmatch(key):
            raise Open5eError("Invalid Open5e document")
        licenses = item.get("licenses") or []
        if not isinstance(licenses, list):
            raise Open5eError("Invalid Open5e document licences")
        publisher = item.get("publisher") if isinstance(item.get("publisher"), dict) else {}
        system = item.get("gamesystem") if isinstance(item.get("gamesystem"), dict) else {}
        catalog[key] = dict(
            name=_text(item.get("display_name"), 100) or key,
            legacy=system.get("key") == "5e-2014",
            licenses=[name for name in (_text(entry.get("name")) for entry in licenses
                                        if isinstance(entry, dict)) if name],
            publisher=_text(publisher.get("name")))
    return catalog


def creature_url(key):
    return f"{CANONICAL_BASE_URL}/creatures/{quote(key, safe='')}/"


def hit_points(creature):
    """Prefer a dice formula only when it reproduces the listed average."""
    hp = creature.get("hit_points")
    if type(hp) is not int or not 0 <= hp <= 99_999:
        return None, None
    formula = re.sub(r"\s+", "", creature.get("hit_dice") or "") if isinstance(
        creature.get("hit_dice"), str) else ""
    match = DICE.fullmatch(formula)
    if match:
        count, sides, sign, modifier = match.groups()
        average = int(count) * (int(sides) + 1) // 2 + (
            int(modifier or 0) * (-1 if sign == "-" else 1))
        if average == hp:
            return formula, "dice"
    return str(hp), "average"


def initiative_offer(creature):
    raw = creature.get("initiative_bonus")
    if raw is None:
        return dict(initiative_bonus=None, initiative_bonus_status="missing",
                    initiative_bonus_reason="No Open5e initiative bonus")
    try:
        if type(raw) is not int:
            raise ValueError("Open5e initiative bonus must be an integer")
        bonus = creation_bonus_fields(raw, origin="source")["initiative_bonus"]
    except ValueError as exc:
        return dict(initiative_bonus=None, initiative_bonus_status="invalid",
                    initiative_bonus_reason=str(exc))
    return dict(initiative_bonus=bonus, initiative_bonus_status="available",
                initiative_bonus_evidence="Open5e initiative_bonus field")


def image_url(creature, base):
    """Open5e illustrations are optional and usually absent."""
    illustration = creature.get("illustration")
    path = illustration.get("file_url") if isinstance(illustration, dict) else None
    if not isinstance(path, str) or not path or len(path) > 2048:
        return None
    url = urljoin(base + "/", path)
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname != urlsplit(base).hostname or parts.username:
        return None
    return url


def candidates(species, display, *, max_candidates=32):
    """Return every validated exact-name creature or raise Open5eError."""
    base = base_url(display)
    query = urlencode({"name__iexact": species.strip(), "fields": FIELDS,
                       "limit": max_candidates, "format": "json"})
    found = _pages(base + "/creatures/?" + query, base, limit=max_candidates)
    catalog = documents(base) if found else {}
    results, seen = [], set()
    for creature in found:
        if not isinstance(creature, dict):
            raise Open5eError("Invalid Open5e creature")
        key, name, document = creature.get("key"), creature.get("name"), creature.get("document")
        if not isinstance(name, str) or normalized(name) != normalized(species):
            continue  # Ignored or looser filters must not leak other monsters.
        if not isinstance(key, str) or not KEY.fullmatch(key) or key in seen:
            raise Open5eError("Invalid or duplicate Open5e creature key")
        if not isinstance(document, dict) or document.get("key") not in catalog:
            raise Open5eError("Open5e creature references an unknown document")
        seen.add(key)
        candidate = _candidate(creature, catalog, base, species)
        if candidate is not None:
            results.append(candidate)
    return results


def _candidate(creature, catalog, base, species):
    """Map one validated creature; None when it has neither AC nor HP."""
    key, name, document = creature.get("key"), creature.get("name"), creature.get("document")
    ac = creature.get("armor_class")
    ac = ac if type(ac) is int and 0 <= ac <= 999 else None
    hp, hp_source = hit_points(creature)
    if ac is None and hp is None:
        return None
    system = document.get("gamesystem") if isinstance(document.get("gamesystem"), dict) else {}
    attribution = catalog[document["key"]]
    source = _text(document.get("display_name"), 100) or document["key"]
    game_system = _text(system.get("name"), 100)
    credit = ", ".join(attribution["licenses"]) or "licence not listed"
    return {"found": True, "name": name, "species": species, "provider": PROVIDER,
            "source": source, "source_key": document["key"],
            "game_system": game_system, "publisher": attribution["publisher"],
            "licenses": attribution["licenses"],
            "attribution": (f"{source}" + (f" by {attribution['publisher']}"
                            if attribution["publisher"] else "") + f" ({credit}) via Open5e"),
            "legacy": system.get("key") == "5e-2014",
            "source_url": creature_url(key), "ac": ac, "hp": hp,
            "hp_source": hp_source, "image_url": image_url(creature, base),
            **initiative_offer(creature)}


def document_monsters(display, document_key):
    """Every monster name in one document; raises unless the list is complete."""
    base = base_url(display)
    catalog = documents(base)
    if document_key not in catalog:
        raise Open5eError("Unknown Open5e document")
    query = urlencode({"document__key": document_key, "fields": "key,name,document",
                       "limit": 500, "format": "json"})
    monsters, seen = [], set()
    for creature in _pages(base + "/creatures/?" + query, base):
        if not isinstance(creature, dict):
            raise Open5eError("Invalid Open5e creature")
        key, name, document = creature.get("key"), creature.get("name"), creature.get("document")
        if not isinstance(document, dict) or document.get("key") != document_key:
            raise Open5eError("Open5e returned monsters from another document")
        if not isinstance(key, str) or not KEY.fullmatch(key) or key in seen:
            raise Open5eError("Invalid or duplicate Open5e creature key")
        if not isinstance(name, str) or not name.strip() or len(name) > 256:
            raise Open5eError("Invalid Open5e creature name")
        seen.add(key)
        monsters.append({"id": key, "name": name})
    return monsters


def document_monster(display, document_key, key):
    """One monster from a document as a lookup candidate (species = its name)."""
    if not isinstance(key, str) or not KEY.fullmatch(key):
        raise Open5eError("Invalid Open5e creature key")
    base = base_url(display)
    catalog = documents(base)
    creature = load_json(f"{base}/creatures/{quote(key, safe='')}/?" +
                         urlencode({"fields": FIELDS, "format": "json"}))
    if not isinstance(creature, dict) or creature.get("key") != key:
        raise Open5eError("Invalid Open5e creature")
    document = creature.get("document")
    if not isinstance(document, dict) or document.get("key") != document_key or document_key not in catalog:
        raise Open5eError("Open5e creature is not in the chosen document")
    name = creature.get("name")
    if not isinstance(name, str) or not name.strip() or len(name) > 256:
        raise Open5eError("Invalid Open5e creature name")
    return _candidate(creature, catalog, base, name)
