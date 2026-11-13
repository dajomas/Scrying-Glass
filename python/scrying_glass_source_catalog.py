"""Source and monster dropdowns for Add monster (SG-TODO-016).

Lists the configured 5e.tools sources and every Open5e document (D&D Beyond is
name-search only by agreement), the complete monster list of one source, and a
signed candidate for one picked monster. Disabled providers are not offered.
"""
from __future__ import annotations
import asyncio
import logging
from fastapi import Depends, HTTPException

LOG = logging.getLogger(__name__)
FIVETOOLS, OPEN5E = "5e.tools", "Open5e"


def _enabled(display):
    return {FIVETOOLS: display.get("fivetools_fallback", True) is True,
            OPEN5E: display.get("open5e_lookup", False) is True}


def sources(display):
    """Ordered source options plus the providers whose sources could not load."""
    from . import scrying_glass_fivetools as ft
    from . import scrying_glass_open5e as open5e
    enabled, options, errors = _enabled(display), [], []
    if enabled[FIVETOOLS]:
        options += [{"provider": FIVETOOLS, "source": code, "legacy": code == "MM"}
                    for code in dict.fromkeys(ft.configured_sources(display))]
    if enabled[OPEN5E]:
        try:
            catalog = open5e.documents(open5e.base_url(display))
            options += [{"provider": OPEN5E, "source": key, "label": item["name"], "legacy": item["legacy"]}
                        for key, item in sorted(catalog.items(), key=lambda pair: pair[1]["name"].casefold())]
        except Exception:
            LOG.warning("Open5e document list failed", exc_info=True)
            errors.append(OPEN5E)
    return {"status": "ok", "sources": options, "unavailable": errors}


def monsters(display, provider, source):
    """Complete, name-sorted monster list for one source; raises when incomplete."""
    from . import scrying_glass_monster_selection as ms
    from . import scrying_glass_open5e as open5e
    if not _enabled(display).get(provider):
        raise LookupError("Provider disabled")
    if provider == FIVETOOLS:
        items = [{"id": name, "name": name} for name, _ in ms.fivetools_source_entries(display, source)]
    else:
        items = sorted(open5e.document_monsters(display, source), key=lambda item: item["name"].casefold())
    return {"status": "ok", "complete": True, "monsters": items}


def monster(display, provider, source, ident):
    """Signed lookup candidate for one monster of one source."""
    from . import scrying_glass_monster_selection as ms
    from . import scrying_glass_open5e as open5e
    if not _enabled(display).get(provider):
        raise LookupError("Provider disabled")
    if provider == FIVETOOLS:
        matches = [candidate for name, candidate in ms.fivetools_source_entries(display, source) if name == ident]
        candidate = matches[0] if matches else None
    else:
        candidate = open5e.document_monster(display, source, ident)
    if candidate is None:
        raise KeyError("Monster has no usable statistics in this source")
    return {"status": "ok", "candidate": ms.sign_candidate(candidate)}


def install_source_catalog_routes(context, app):
    from .scrying_glass_provider_settings import effective_display
    guard = [Depends(context.require("admin", context.ADMIN_SESSION_COOKIE))]

    def check(provider, source):
        if provider not in (FIVETOOLS, OPEN5E):
            raise HTTPException(400, "Unknown monster source provider")
        if not isinstance(source, str) or not 1 <= len(source) <= 200:
            raise HTTPException(400, "Invalid monster source")

    async def run(function, *args):
        try:
            return await asyncio.to_thread(function, effective_display(context), *args)
        except LookupError as exc:
            if isinstance(exc, KeyError):
                raise HTTPException(404, str(exc.args[0])) from exc
            raise HTTPException(409, str(exc)) from exc
        except Exception as exc:
            LOG.warning("Monster source catalog failed", exc_info=True)
            return {"status": "error", "reason": "The monster list could not be loaded completely; retry."}

    @app.get("/api/monsters/catalog/sources", dependencies=guard)
    async def monster_catalog_sources():
        return await asyncio.to_thread(sources, effective_display(context))

    @app.get("/api/monsters/catalog/monsters", dependencies=guard)
    async def monster_catalog_monsters(provider: str, source: str):
        check(provider, source)
        return await run(monsters, provider, source)

    @app.get("/api/monsters/catalog/monster", dependencies=guard)
    async def monster_catalog_monster(provider: str, source: str, id: str):
        check(provider, source)
        if not 1 <= len(id) <= 256:
            raise HTTPException(400, "Invalid monster")
        return await run(monster, provider, source, id)
