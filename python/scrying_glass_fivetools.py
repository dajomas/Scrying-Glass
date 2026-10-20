"""Optional 5etools JSON provider. No third-party data is bundled."""
from __future__ import annotations
import json
import logging
import re
import threading
import time
from collections import OrderedDict
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

LOG = logging.getLogger(__name__)
_CACHE = OrderedDict()
_LOCK = threading.RLock()

def normalized(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).casefold()).strip()

def https_url(value):
    parts = urlsplit(str(value))
    return str(value) if parts.scheme == "https" and parts.hostname and not parts.username and not parts.password else None

def load_json(url):
    if not https_url(url):
        raise ValueError("5etools data URL must use HTTPS")
    with _LOCK:
        cached = _CACHE.get(url)
        if cached and cached[0] > time.monotonic():
            _CACHE.move_to_end(url)
            return cached[1]
        request = Request(url, headers={"User-Agent": "ScryingGlass/1.0", "Accept": "application/json"})
        with urlopen(request, timeout=5) as response:
            if urlsplit(response.geturl()).hostname != urlsplit(url).hostname:
                raise ValueError("Unexpected 5etools data redirect")
            raw = response.read(16_000_001)
        if len(raw) > 16_000_000:
            raise ValueError("5etools JSON exceeds 16 MB")
        data = json.loads(raw)
        _CACHE[url] = (time.monotonic() + 3600, data)
        _CACHE.move_to_end(url)
        while len(_CACHE) > 32:
            _CACHE.popitem(last=False)
        return data

def stats(monster):
    ac = monster.get("ac", [])
    ac = ac if isinstance(ac, list) else [ac]
    ac = next((value if type(value) is int else value.get("ac")
               for value in ac if type(value) is int or isinstance(value, dict)), None)
    ac = ac if type(ac) is int and 0 <= ac <= 999 else None
    hp = monster.get("hp", {})
    hp = hp if isinstance(hp, dict) else {}
    formula = re.sub(r"\s+", "", str(hp.get("formula", "")))
    if re.fullmatch(r"[1-9]\d*d(?:[2-9]\d*|1\d+)(?:[+-]\d+)?", formula, re.I):
        return ac, formula, "dice"
    average = hp.get("average")
    return ac, str(average) if type(average) is int and average >= 0 else None, "average" if type(average) is int and average >= 0 else None

def image_url(monster, display):
    explicit = monster.get("tokenUrl")
    if explicit and https_url(explicit):
        return explicit
    if not monster.get("hasToken"):
        return None
    source = str(monster.get("tokenSource") or monster.get("source", ""))
    name = str(monster.get("tokenName") or monster.get("name", ""))
    root = display.get("fivetools_image_base_url", "https://5e.tools/img").rstrip("/")
    if not https_url(root) or not source or not name:
        return None
    return f"{root}/bestiary/tokens/{quote(source, safe='')}/{quote(name, safe='')}.webp"

def lookup(species, display, *, want_image=False):
    """Return the first exact usable match in configured source order."""
    if not display.get("fivetools_fallback", True) or not normalized(species):
        return None
    root = display.get("fivetools_data_base_url", "https://5e.tools/data/bestiary").rstrip("/")
    sources = display.get("fivetools_sources", ["MM", "XMM"])
    if not isinstance(sources, list) or not all(isinstance(s, str) for s in sources):
        raise ValueError("fivetools_sources must be a list of source identifiers")
    index = load_json(root + "/index.json")
    if not isinstance(index, dict):
        raise ValueError("Invalid 5etools bestiary index")
    for source in sources:
        filename = index.get(source)
        if not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+\.json", filename):
            continue
        try:
            data = load_json(root + "/" + filename)
            for monster in data.get("monster", []):
                if not isinstance(monster, dict) or normalized(monster.get("name", "")) != normalized(species):
                    continue
                # Unresolved copy entries must not silently borrow another edition's stats.
                ac, hp, hp_source = stats(monster)
                image = image_url(monster, display)
                if (want_image and not image) or (not want_image and ac is None and hp is None):
                    continue
                return {
                    "found": True, "species": species, "ac": ac, "hp": hp,
                    "hp_source": hp_source, "provider": "5e.tools",
                    "source": monster.get("source", source),
                    "legacy": source == "MM", "image_url": image,
                    "source_url": "https://5e.tools/bestiary.html#" + quote(
                        str(monster.get("name", "")).lower() + "_" + str(monster.get("source", source)).lower(), safe=""),
                }
        except Exception:
            LOG.warning("Optional 5etools source failed: %s", source, exc_info=True)
    return None
