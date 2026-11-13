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
    from .scrying_glass_monster_source_snapshot import issue_selection
    return issue_selection(candidate, _KEY, now=time.time())


def selected_snapshot(token, species):
    from .scrying_glass_monster_source_snapshot import read_selection
    return read_selection(token, species, _KEY, now=time.time(), max_age=TOKEN_AGE,
                          image_validator=ft.https_url)


def selected_image(token, species):
    """Keep the existing image-only interface; never fetch a browser-supplied URL."""
    return selected_snapshot(token, species)[0]

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
                if ft.https_url(src):
                    self.url = url

def dnd_candidates(context, species):
    from .scrying_glass_dnd_initiative_offer import dnd_initiative_offer
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
                            "source": dnd_source_book(html) or "Source book unavailable",
                            "source_url": "https://www.dndbeyond.com" + href,
                            "ac": ac, "hp": hp, "hp_source": hp_source, "image_url": image.url,
                            **({"attribution": credit} if (credit := dnd_source_attribution(html)) else {}),
                            **dnd_initiative_offer(html)})
        return results
    except ProviderError:
        raise
    except Exception as exc:
        LOG.warning("D&D Beyond candidate lookup failed", exc_info=True)
        raise ProviderError("D&D Beyond lookup failed; enter stats manually or retry.") from exc

class MonsterSourceText(HTMLParser):
    """Collect the text of D&D Beyond's <p class="source monster-source"> element."""
    def __init__(self):
        super().__init__()
        self.depth, self.parts, self.done = 0, [], False

    def handle_starttag(self, tag, attrs):
        if self.depth:
            self.depth += 1
        elif not self.done and tag == "p" and "monster-source" in (dict(attrs).get("class") or "").split():
            self.depth = 1

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1
            self.done = self.done or self.depth == 0

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)


def dnd_source_text(html):
    """The page's source line, e.g. 'Basic Rules (2014), pg. 138'; None when absent."""
    parser = MonsterSourceText()
    parser.feed(html)
    text = " ".join(" ".join(parser.parts).split()).replace(" ,", ",")
    return text if 0 < len(text) <= 200 else None


def dnd_source_book(html):
    """Book name from the source line without the page; None when absent."""
    text = dnd_source_text(html)
    book = re.split(r",\s*pg\.", text, maxsplit=1)[0].strip() if text else ""
    return book if 0 < len(book) <= 100 else None


def dnd_source_attribution(html):
    """'<book>, pg. N via D&D Beyond' when the page names its source; otherwise None."""
    text = dnd_source_text(html)
    return f"{text} via D&D Beyond" if text else None


def fivetools_source_attribution(source_name, monster):
    """'<code>, page N via 5e.tools' when the entry has a positive integer page."""
    page = monster.get("page")
    if type(page) is int and 0 < page < 100000:
        return f"{source_name}, page {page} via 5e.tools"
    return None


def fivetools_candidates(species, display):
    from .scrying_glass_fivetools_initiative import fivetools_initiative_offer
    try:
        root = display.get("fivetools_data_base_url", "https://5e.tools/data/bestiary").rstrip("/")
        sources = ft.configured_sources(display)
        if not sources:
            return []
        index = ft.load_json(root + "/index.json")
        if not isinstance(index, dict):
            raise ValueError("Invalid index")
        results, seen = [], set()
        for source in dict.fromkeys(sources):
            filename = index.get(source)
            if filename is None:
                raise ValueError("Configured source is missing from the provider index")
            if not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+\.json", filename):
                raise ValueError("Invalid source filename")
            data = ft.load_json(root + "/" + filename)
            if not isinstance(data, dict) or not isinstance(data.get("monster"), list):
                raise ValueError("Invalid source data")
            for monster in data["monster"]:
                if not isinstance(monster, dict):
                    raise ValueError("Invalid monster entry")
                if ft.normalized(monster.get("name", "")) != ft.normalized(species):
                    continue
                ac, hp, hp_source = ft.stats(monster)
                if ac is None and hp is None:
                    continue
                source_name = str(monster.get("source", source))
                if source_name not in sources:
                    continue
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
                                "ac": ac, "hp": hp, "hp_source": hp_source, "image_url": image,
                                **({"attribution": credit} if (credit := fivetools_source_attribution(
                                    source_name, monster)) else {}),
                                **fivetools_initiative_offer(monster)})
                if len(results) > MAX_CANDIDATES:
                    raise ProviderError("5e.tools returned too many candidates; refine the configured sources.")
        return results
    except ProviderError:
        raise
    except Exception as exc:
        LOG.warning("5e.tools candidate lookup failed", exc_info=True)
        raise ProviderError("5e.tools lookup failed; enter stats manually or retry.") from exc

def open5e_candidates(species, display):
    from . import scrying_glass_open5e as open5e
    try:
        return open5e.candidates(species, display, max_candidates=MAX_CANDIDATES)
    except Exception as exc:
        LOG.warning("Open5e candidate lookup failed", exc_info=True)
        raise ProviderError("Open5e lookup failed; enter stats manually or retry.") from exc

def lookup_candidates(context, species, *, include_open5e=True):
    """Ordered D&D Beyond, 5e.tools, Open5e lookup with saved provider toggles.

    Monster refresh includes Open5e when its provider switch is enabled.
    """
    from .scrying_glass_combined_lookup import combined_candidates
    from .scrying_glass_provider_settings import effective_display
    from .scrying_glass_source_bonus_offer import issue_bonus_offer
    display = effective_display(context)
    open5e_enabled = include_open5e and display.get("open5e_lookup", False) is True
    result = combined_candidates(
        lambda: dnd_candidates(context, species),
        lambda: fivetools_candidates(species, display),
        dnd_enabled=display.get("dndbeyond_image_lookup", True),
        fivetools_enabled=display.get("fivetools_fallback", True),
        max_candidates=MAX_CANDIDATES,
        extra=(("Open5e", open5e_enabled, lambda: open5e_candidates(species, display)),))
    if result["status"] != "ok":
        return result
    for candidate in result["candidates"]:
        candidate["selection_token"] = issue_token(candidate)
        offer = issue_bonus_offer(candidate, _KEY, now=time.time())
        if offer is not None:
            candidate["initiative_bonus_offer_token"] = offer
    return result

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
                             image: UploadFile | None = File(None), selection_token: str = Form(''),
                             initiative_bonus: str = Form(''),
                             initiative_bonus_offer_token: str = Form(''),
                             image_selection_token: str = Form('')):
        from fastapi.params import Form as FormParameter
        from .scrying_glass_initiative_input import creation_bonus_fields
        from .scrying_glass_source_bonus_offer import read_bonus_offer
        from .scrying_glass_monster_source_snapshot import FIELDS as SOURCE_FIELDS
        if isinstance(initiative_bonus, FormParameter):
            initiative_bonus = initiative_bonus.default
        if isinstance(initiative_bonus_offer_token, FormParameter):
            initiative_bonus_offer_token = initiative_bonus_offer_token.default
        if isinstance(image_selection_token, FormParameter):
            image_selection_token = image_selection_token.default
        try:
            bonus_fields = creation_bonus_fields(initiative_bonus)
            if initiative_bonus_offer_token:
                offered = read_bonus_offer(initiative_bonus_offer_token, monster_species, _KEY,
                                          now=time.time(), max_age=TOKEN_AGE)
                _, identity = selected_snapshot(selection_token, monster_species)
                offered_identity = {key: value for key, value in offered.items() if key in SOURCE_FIELDS}
                if not identity or identity != offered_identity:
                    raise ValueError("Initiative offer does not match the selected source; repeat lookup.")
                if (bonus_fields["initiative_bonus_origin"] == "default"
                        or bonus_fields["initiative_bonus"] != offered["initiative_bonus"]):
                    raise ValueError("Initiative bonus changed; use manual entry or repeat offer review.")
                bonus_fields = {"initiative_bonus": offered["initiative_bonus"],
                                "initiative_bonus_origin": "source"}
        except ValueError as exc:
            raise self.context.HTTPException(422, str(exc)) from exc
        next_hp = self.context.hp_value_factory(hprangestart, hprangeend)
        fields = {"name": name.strip(), "monster_species": monster_species.strip(), "ac": ac,
                  "initiative_roll": None, **bonus_fields}
        from .scrying_glass_monster_names import numbered_monster_name
        try:
            names = [numbered_monster_name(fields["name"], quantity, number) for number in range(1, quantity + 1)]
        except ValueError as exc:
            raise self.context.HTTPException(422, str(exc)) from exc
        working_state = self.context.STATE
        source_fields = {}
        if image is not None and image.filename:
            image_url = self.context.save_image(image)
            if selection_token:
                try:
                    _, source_fields = selected_snapshot(selection_token, fields["monster_species"])
                except ValueError:
                    pass  # Preserve upload precedence; invalid tokens cannot supply identity.
        elif selection_token:
            try:
                image_url, source_fields = selected_snapshot(selection_token, fields["monster_species"])
                if image_selection_token:
                    # Image picked from another found candidate: only its signed image is used.
                    image_url = selected_snapshot(image_selection_token, fields["monster_species"])[0]
                    if not image_url:
                        raise ValueError("Chosen image is unavailable; repeat lookup.")
            except ValueError as exc:
                raise self.context.HTTPException(422, str(exc)) from exc
        else:
            image_url = await asyncio.to_thread(self.context.dnd_image, fields["monster_species"])
        if self.context.STATE is not working_state:
            raise self.context.HTTPException(409, "The encounter changed while this request was running. Retry.")
        fields.update(source_fields)
        created = [self.context.make_monster({**fields, "name": item, "hp": next_hp()}, color, None, image_url) for item in names]
        working_state["monsters"].extend(created)
        await self.context.combatants_changed(monsters=True, characters=False)
        return created
