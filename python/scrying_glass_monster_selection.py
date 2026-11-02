"""Public-provider candidate selection; no account credentials or entitlements."""
from __future__ import annotations
import asyncio
import base64
import hashlib
import hmac
import json
import logging
import re
import secrets
import time
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from fastapi import File, Form, UploadFile
from .scrying_glass_admin_monsters import AdminMonstersMixin
from . import scrying_glass_fivetools as ft

LOG = logging.getLogger(__name__)
_KEY = secrets.token_bytes(32)
MAX_CANDIDATES = 32
TOKEN_AGE = 1800

class ProviderError(Exception):
    """Failed or incomplete lookup, not a successful zero-match search."""

def issue_token(candidate):
    payload = json.dumps({"species": candidate["species"],
                          "image_url": candidate.get("image_url"),
                          "issued": int(time.time())}, separators=(",", ":")).encode()
    data = base64.urlsafe_b64encode(payload).decode()
    return data + "." + hmac.new(_KEY, data.encode(), hashlib.sha256).hexdigest()

def selected_image(token, species):
    """Validate a snapshot without fetching any browser-supplied URL."""
    if token == "manual":
        return None
    try:
        if not isinstance(token, str) or len(token) > 8192:
            raise ValueError()
        data, signature = token.rsplit(".", 1)
        expected = hmac.new(_KEY, data.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError()
        payload = json.loads(base64.urlsafe_b64decode(data))
        age = time.time() - payload["issued"]
        if age < -60 or age > TOKEN_AGE or payload["species"] != species.strip():
            raise ValueError()
        image = payload.get("image_url")
        if image is not None and not ft.https_url(image):
            raise ValueError()
        return image
    except Exception as exc:
        raise ValueError("Monster selection expired or invalid; repeat lookup or use manual entry.") from exc

class MonsterImage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.url = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img" and "monster-image" in attrs.get("class", "").split():
            src = attrs.get("src")
            if src:
                url = urljoin("https://www.dndbeyond.com", src)
                if ft.https_url(url):
                    self.url = url

def dnd_candidates(context, species):
    results, seen = [], set()
    try:
        hits = context.dnd_monster_candidates(species)
        if len(hits) > MAX_CANDIDATES:
            raise ProviderError("D&D Beyond returned too many candidates; refine the species.")
        for legacy, href in hits:
            url = urlsplit(href)
            if url.scheme or url.netloc or not url.path.startswith("/monsters/") or href.startswith("//"):
                raise ProviderError("D&D Beyond returned an invalid candidate link.")
            if href in seen:
                continue
            seen.add(href)
            try:
                html = context.dnd_monster_detail_html(href)
            except HTTPError as exc:
                if exc.code == 404:
                    continue
                raise
            ac, hp, hp_source = context.dnd_monster_stats_from_html(html)
            if ac is None and hp is None:
                continue
            image = MonsterImage()
            image.feed(html)
            results.append({"found": True, "name": species, "species": species,
                            "provider": "D&D Beyond", "legacy": legacy,
                            "source": "Source book unavailable",
                            "source_url": "https://www.dndbeyond.com" + href,
                            "ac": ac, "hp": hp, "hp_source": hp_source, "image_url": image.url})
        return results
    except ProviderError:
        raise
    except Exception as exc:
        LOG.warning("D&D Beyond candidate lookup failed", exc_info=True)
        raise ProviderError("D&D Beyond lookup failed; no fallback was attempted. Enter stats manually or retry.") from exc

def fivetools_candidates(species, display):
    try:
        root = display.get("fivetools_data_base_url", "https://5e.tools/data/bestiary").rstrip("/")
        sources = display.get("fivetools_sources", ["MM", "XMM"])
        if not isinstance(sources, list) or len(sources) > 32 or not all(isinstance(s, str) for s in sources):
            raise ValueError("Invalid sources")
        index = ft.load_json(root + "/index.json")
        if not isinstance(index, dict):
            raise ValueError("Invalid index")
        results, seen = [], set()
        for source in dict.fromkeys(sources):
            filename = index.get(source)
            if filename is None:
                continue
            if not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+\.json", filename):
                raise ValueError("Invalid source filename")
            data = ft.load_json(root + "/" + filename)
            if not isinstance(data, dict) or not isinstance(data.get("monster"), list):
                raise ValueError("Invalid source data")
            for monster in data["monster"]:
                if not isinstance(monster, dict) or ft.normalized(monster.get("name", "")) != ft.normalized(species):
                    continue
                ac, hp, hp_source = ft.stats(monster)
                if ac is None and hp is None:
                    continue
                source_name = str(monster.get("source", source))
                url = "https://5e.tools/bestiary.html#" + ft.quote(
                    str(monster.get("name", "")).lower() + "_" + source_name.lower(), safe="")
                image = ft.image_url(monster, display)
                identity = (url, ac, hp, image)
                if identity in seen:
                    continue
                seen.add(identity)
                results.append({"found": True, "name": str(monster["name"]), "species": species,
                                "provider": "5e.tools", "source": source_name,
                                "legacy": source_name == "MM", "source_url": url,
                                "ac": ac, "hp": hp, "hp_source": hp_source, "image_url": image})
                if len(results) > MAX_CANDIDATES:
                    raise ProviderError("5e.tools returned too many candidates; refine the configured sources.")
        return results
    except ProviderError:
        raise
    except Exception as exc:
        LOG.warning("5e.tools candidate lookup failed", exc_info=True)
        raise ProviderError("5e.tools lookup failed; enter stats manually or retry.") from exc

def lookup_candidates(context, species):
    display = context.CONFIG["display"]
    try:
        results = dnd_candidates(context, species) if display.get("dndbeyond_image_lookup", True) else []
        if not results and display.get("fivetools_fallback", True):
            results = fivetools_candidates(species, display)
        for candidate in results:
            candidate["selection_token"] = issue_token(candidate)
        return {"status": "ok", "candidates": results}
    except ProviderError as exc:
        return {"status": "error", "candidates": [], "reason": str(exc)}

class CandidateMonstersMixin(AdminMonstersMixin):
    """Extend creation with an optional signed image snapshot."""

    async def monster_lookup_candidates(self, species: str):
        species = species.strip()
        if not 1 <= len(species) <= 100:
            raise self.context.HTTPException(400, "Monster species must contain 1-100 characters")
        return await asyncio.to_thread(lookup_candidates, self.context, species)

    async def create_monster(self, name: str = Form(...), monster_species: str = Form(...),
                             ac: int = Form(...), hprangestart: str = Form(...),
                             hprangeend: str = Form(''), color: str = Form(...),
                             quantity: int = Form(1, ge=1, le=50),
                             image: UploadFile | None = File(None), selection_token: str = Form('')):
        next_hp = self.context.hp_value_factory(hprangestart, hprangeend)
        fields = {"name": name.strip(), "monster_species": monster_species.strip(), "ac": ac}
        from .scrying_glass_monster_names import numbered_monster_name
        try:
            names = [numbered_monster_name(fields["name"], quantity, number) for number in range(1, quantity + 1)]
        except ValueError as exc:
            raise self.context.HTTPException(422, str(exc)) from exc
        working_state = self.context.STATE
        if image is not None and image.filename:
            image_url = self.context.save_image(image)
        elif selection_token:
            try:
                image_url = selected_image(selection_token, fields["monster_species"])
            except ValueError as exc:
                raise self.context.HTTPException(422, str(exc)) from exc
        else:
            image_url = await asyncio.to_thread(self.context.dnd_image, fields["monster_species"])
        if self.context.STATE is not working_state:
            raise self.context.HTTPException(409, "The encounter changed while this request was running. Retry.")
        created = [self.context.make_monster({**fields, "name": item, "hp": next_hp()}, color, None, image_url) for item in names]
        working_state["monsters"].extend(created)
        await self.context.combatants_changed(monsters=True, characters=False)
        return created
