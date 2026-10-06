"""Scrying Glass v4.16 (Python 3.14+), formerly "Monster Display".

Dependencies:
  python3.14 -m pip install 'fastapi>=0.115' 'uvicorn[standard]>=0.30' 'PyYAML>=6.0' python-multipart

Run:
  python3.14 scrying_glass_server.py --config config.yaml"""


# ============================================================================
# Imports
# ============================================================================


from __future__ import annotations
import argparse, asyncio, copy, csv, hashlib, hmac, io, json, random, re, secrets, shutil, sys, uuid, uvicorn, yaml
from pathlib import Path
from typing import Any, Callable, Literal
from urllib.parse import quote
from urllib.request import Request, urlopen
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request as FastAPIRequest, UploadFile, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel, Field
from login_html import LOGIN
from admin_html import ADMIN_HTML
from client_html import CLIENT_HTML
from typing import get_type_hints

from scrying_glass_api_admin import AdminAPI
from scrying_glass_api_client import ClientAPI

# ============================================================================
# Constants and default configuration
# ============================================================================


LEGACY_STORAGE_DIR = './monster-display-data'
DEFAULT_SETUP_NAME = 'default'
DEFAULT_CAMPAIGN_SLUG = 'default'
DEFAULT_CAMPAIGN_NAME = 'Default'
DEFAULT_VIEW_BACKGROUND = '#080b14'
ADMIN_SESSION_COOKIE = "scrying_glass_admin_session"
CLIENT_SESSION_COOKIE = "scrying_glass_client_session"
LEGACY_SESSION_COOKIES = ("monster_session", "monster_admin_session", "monster_client_session")

# Extraction boundary: these helpers do not read live server state.
# Copy their imports, constants and helper dependencies with them.
# login() also needs the LOGIN HTML template.

from scrying_glass_init import *
from scrying_glass_hp import *
from scrying_glass_combatant import *
from scrying_glass_tools import *
from scrying_glass_monster_csv import *
from scrying_glass_dndbeyond import *
from scrying_glass_classes import *

# ============================================================================
# Mutable runtime state and configured storage paths
# ============================================================================

CONFIG: dict[str, Any] = {}
STATE: dict[str, Any] = {
    "monsters": [],
    "characters": [],
    "battle_order": [],
    "activity_log": [],
    "display": {},
    "active_setup": None,
}
LOCK = asyncio.Lock()
SESSIONS: dict[str, dict[str, str]] = {}
SOCKETS: set[WebSocket] = set()
DATA_DIR: Path
STATE_FILE: Path
UPLOAD_DIR: Path
SETUPS_DIR: Path
CAMPAIGNS_FILE: Path
CHARACTERS_DIR: Path
STATIC_DIR: Path

# ============================================================================
# Authentication and session authorization
# ============================================================================

def user(name: str) -> dict[str, Any] | None:
    """Find a configured user by username."""
    return next((x for x in CONFIG['security']['users'] if x.get('username') == name), None)

def require(
    role: Literal["admin", "client"],
    cookie_name: str,
):
    """Build a cookie-based authorization dependency for the requested role."""
    async def dependency(request: FastAPIRequest) -> dict[str, str]:
        """Dependency."""
        session = SESSIONS.get(
            request.cookies.get(cookie_name, "")
        )

        if not session or (
            role == "admin" and session["role"] != "admin"
        ):
            raise HTTPException(401, "Sign in required")

        return session

    return dependency

# ============================================================================
# Encounter state normalization and lookup
# ============================================================================


def entities() -> list[dict[str, Any]]:
    """Return all monsters and campaign characters in the current encounter."""
    return [*STATE['monsters'], *STATE['characters']]

def entity(ident: str) -> dict[str, Any] | None:
    """Find a combatant by its unique identifier."""
    return next((x for x in entities() if x['id'] == ident), None)

def active_combatant() -> dict[str, Any] | None:
    """Active combatant."""
    return next(
        (combatant for combatant in entities() if combatant.get("in_turn")),
        None,
    )

def configured_background() -> str:
    """Configured background."""
    return str(
        CONFIG.get('display', {}).get('background', DEFAULT_VIEW_BACKGROUND)
    ).strip() or DEFAULT_VIEW_BACKGROUND

def normalize_display(raw: Any) -> dict[str, str]:
    """Normalize display."""
    display = raw if isinstance(raw, dict) else {}
    background = str(
        display.get('background', configured_background())
    ).strip()

    return {
        'background': background or configured_background(),
    }

def normalize_state(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize state."""
    raw_active_setup = raw.get("active_setup")

    if isinstance(raw_active_setup, dict):
        raw_campaign = raw_active_setup.get("campaign")
        raw_name = raw_active_setup.get("name")

        if (
            isinstance(raw_campaign, str)
            and raw_campaign.strip()
            and isinstance(raw_name, str)
            and raw_name.strip()
        ):
            active_setup: dict[str, str] | None = {
                "campaign": raw_campaign.strip(),
                "name": raw_name.strip(),
            }
        else:
            active_setup = None
    else:
        active_setup = None

    state = {
        "monsters": raw.get("monsters", []),
        "characters": raw.get("characters", []),
        "battle_order": raw.get("battle_order", []),
        "activity_log": raw.get("activity_log", []),
        "display": normalize_display(raw.get("display")),
        "active_setup": active_setup,
    }

    if (
        not isinstance(state["monsters"], list)
        or not isinstance(state["characters"], list)
        or not isinstance(state["battle_order"], list)
        or not isinstance(state["activity_log"], list)
    ):
        raise ValueError('Setup has invalid monsters, characters, battle_order, or activity_log data')

    state["activity_log"] = [
        entry
        for entry in state["activity_log"]
        if isinstance(entry, dict)
    ]

    for m in state['monsters']:
        if not isinstance(m, dict):
            raise ValueError('Setup contains an invalid monster')
        m.setdefault('id', uuid.uuid4().hex)
        m.setdefault('name', 'Unnamed Monster')
        if 'monster_species' not in m:
            m['monster_species'] = m.pop('monster_type', 'unknown')
        else:
            m.pop('monster_type', None)

        m['monster_species'] = str(m['monster_species']).strip() or 'unknown'
        m.setdefault('ac', 0)
        m.setdefault('hp', 1)
        m.setdefault('original_hp', m.get('max_hp', m['hp']))
        m.setdefault('max_hp', m['original_hp'])
        m.setdefault('color', '#842029')
        m.setdefault('image_url', None)
        m.setdefault('alive', m['hp'] > 0)
        m.setdefault('active', False)
        m.setdefault('visible', False)
        m.setdefault('ally', False)
        m.setdefault('initiative', None)
        m.setdefault('original_initiative', m.get('initiative'))
        m.setdefault('show_ac', False)
        m.setdefault('show_hp', False)
        m.setdefault('show_initiative', False)
        m.setdefault('in_turn', False)
    for c in state['characters']:
        if not isinstance(c, dict):
            raise ValueError('Setup contains an invalid character')
        c.setdefault('id', uuid.uuid4().hex)
        c.setdefault('name', 'Unnamed Character')
        c.setdefault('color', '#1f4e79')
        c.setdefault('hp', 1)
        c.setdefault('max_hp', c['hp'])
        c.setdefault('original_hp', c['max_hp'])
        c.setdefault('original_initiative', c.get('initiative'))
        c.setdefault('alive', c['hp'] > 0)
        c.setdefault('active', False)
        c.setdefault('visible', False)
        c.setdefault('in_turn', False)
    known = {x['id'] for x in [*state['monsters'], *state['characters']]}
    state['battle_order'] = [x for x in state['battle_order'] if x in known]
    return state

def public_state() -> dict[str, Any]:
    """Build the state payload exposed to authenticated displays."""
    d = CONFIG['display']
    return {
        "monsters": STATE["monsters"],
        "characters": STATE["characters"],
        "battle_order": STATE["battle_order"],
        "activity_log": STATE["activity_log"],
        "active_setup": STATE.get("active_setup"),
        "display": {
            "background": STATE["display"]["background"],
            "entry_direction": d["entry_direction"],
            "exit_direction": d["exit_direction"],
            "monster_width_percent": d["monster_width_percent"],
        },
    }

# ============================================================================
# Campaign and setup path resolution
# ============================================================================


def setup_path(name: str, campaign: str | None = None) -> Path:
    """Setup path."""
    return campaign_dir(require_campaign(campaign)) / (setup_slug(name) + '.json')

def campaign_characters_path(slug: str) -> Path:
    """Campaign characters path."""
    return CHARACTERS_DIR / f"{slug}.json"

def list_setups(campaign: str | None = None) -> list[str]:
    """List setups."""
    return sorted((p.stem for p in campaign_dir(require_campaign(campaign)).glob('*.json')), key=str.casefold)

def campaign_dir(slug: str) -> Path:
    """Campaign dir."""
    return SETUPS_DIR / slug

def active_setup_reference() -> dict[str, str] | None:
    """Return the current saved battle setup reference, when valid."""
    value = STATE.get("active_setup")

    if not isinstance(value, dict):
        return None

    campaign = value.get("campaign")
    name = value.get("name")

    if not isinstance(campaign, str) or not campaign.strip():
        return None

    if not isinstance(name, str) or not name.strip():
        return None

    return {
        "campaign": campaign,
        "name": name,
    }

def set_active_setup(campaign: str, name: str) -> None:
    """Mark the named saved setup as the source of the working monsters."""
    STATE["active_setup"] = {
        "campaign": campaign,
        "name": name,
    }

def clear_active_setup() -> None:
    """Mark the current monster encounter as unsaved."""
    STATE["active_setup"] = None

def active_setup_path() -> Path | None:
    """Return the referenced setup path only when it still exists."""
    reference = active_setup_reference()

    if reference is None:
        return None

    try:
        campaign = require_campaign(reference["campaign"])
        name = setup_slug(reference["name"])
    except HTTPException:
        return None

    path = setup_path(name, campaign)

    return path if path.exists() else None

# ============================================================================
# Campaign metadata and setup lifecycle
# ============================================================================


def read_campaigns() -> dict[str, Any]:
    """Read campaigns."""
    data: dict[str, Any] = {'active': None, 'campaigns': {}}
    if CAMPAIGNS_FILE.exists():
        try:
            raw = json.loads(CAMPAIGNS_FILE.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            raw = {}
        if isinstance(raw, dict):
            if isinstance(raw.get('campaigns'), dict):
                data['campaigns'] = {
                    str(k): v for k, v in raw['campaigns'].items() if isinstance(v, dict)
                }
            if isinstance(raw.get('active'), str):
                data['active'] = raw['active']
    for slug, meta in data['campaigns'].items():
        meta.setdefault('name', slug)
        meta.setdefault('description', '')
        meta.setdefault('created', now_iso())
    return data

def write_campaigns(data: dict[str, Any]) -> None:
    """Write campaigns."""
    temp = CAMPAIGNS_FILE.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
    temp.replace(CAMPAIGNS_FILE)

def active_campaign() -> str:
    """Active campaign."""
    return read_campaigns()['active'] or DEFAULT_CAMPAIGN_SLUG

def require_campaign(campaign: str | None) -> str:
    """Resolve an optional campaign slug/name to an existing campaign slug."""
    if campaign is None or not str(campaign).strip():
        slug = active_campaign()
    else:
        slug = campaign_slug(str(campaign))
    if slug not in read_campaigns()['campaigns']:
        raise HTTPException(404, f'Campaign not found: {slug}')
    campaign_dir(slug).mkdir(parents=True, exist_ok=True)
    return slug

def create_default_setup(slug: str) -> str | None:
    """Create an empty battle setup called "Default" in a newly created campaign.

    Does nothing (returns None) if the campaign already has a setup with that name.
    """
    directory = campaign_dir(slug)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f'{DEFAULT_SETUP_NAME}.json'
    if path.exists():
        return None
    empty = normalize_state({'monsters': [], 'characters': [], 'battle_order': [], 'activity_log': [], 'display': {'background': configured_background(),}})
    temp = path.with_suffix('.tmp')
    temp.write_text(
        json.dumps(setup_snapshot(empty), indent=2),
        encoding="utf-8",
    )
    temp.replace(path)
    return DEFAULT_SETUP_NAME

def remember_setup(campaign: str, name: str) -> None:
    """Record the battle setup most recently worked on (saved/loaded) in a campaign."""
    data = read_campaigns()
    meta = data['campaigns'].get(campaign)
    if meta is None:
        return
    meta['last_setup'] = name
    meta['last_setup_at'] = now_iso()
    write_campaigns(data)

def pick_campaign_setup(campaign: str) -> str | None:
    """Setup to open when a campaign is activated.

    1. the most recently worked on setup recorded in campaigns.json (if it still exists);
    2. otherwise the setup file modified most recently;
    3. None when the campaign has no setups.
    """
    directory = campaign_dir(campaign)
    last = read_campaigns()['campaigns'].get(campaign, {}).get('last_setup')
    if isinstance(last, str) and (directory / f'{last}.json').exists():
        return last
    files = sorted(directory.glob('*.json'), key=lambda p: (-p.stat().st_mtime, p.stem.casefold()))
    return files[0].stem if files else None

async def open_campaign_setup(campaign: str) -> str | None:
    """Load the campaign's most recent (or first) setup into the live battle state."""
    global STATE
    name = pick_campaign_setup(campaign)
    if name is None:
        return None
    path = campaign_dir(campaign) / f'{name}.json'
    try:
        STATE = load_setup_state(name, campaign)
    except HTTPException as exc:
        raise HTTPException(
            exc.status_code,
            f"Campaign activated, but setup {name} could not be opened: {exc.detail}",
        ) from exc
    set_active_setup(campaign, name)
    remember_setup(campaign, name)
    await changed()
    return name

def campaigns_payload(moved: list[str] | None = None) -> dict[str, Any]:
    """Campaigns payload."""
    data = read_campaigns()
    items = []
    for slug, meta in data['campaigns'].items():
        setups = sorted((p.stem for p in campaign_dir(slug).glob('*.json')), key=str.casefold)
        items.append({
            'slug': slug,
            'name': meta.get('name', slug),
            'description': meta.get('description', ''),
            'created': meta.get('created'),
            'setups': setups,
            'last_setup': meta.get('last_setup') if meta.get('last_setup') in setups else None,
        })
    items.sort(key=lambda x: str(x['name']).casefold())
    return {'active': data['active'], 'campaigns': items, 'moved': moved or []}

# ============================================================================
# Storage migration
# ============================================================================


def migrate_unassigned_setups() -> list[str]:
    """Move battle setups that are not connected to a campaign into "Default".

    Also keeps the registry and the directories consistent:
      * campaign directories without a registry entry are registered;
      * registry entries without a directory get their directory recreated;
      * there is always at least one campaign and a valid active campaign.
    Returns the names of the setups that were moved.
    """
    data = read_campaigns()
    dirty = not CAMPAIGNS_FILE.exists()
    campaigns = data['campaigns']

    for directory in SETUPS_DIR.iterdir():
        if directory.is_dir() and directory.name not in campaigns:
            campaigns[directory.name] = {
                'name': directory.name.replace('-', ' ').title(),
                'description': '',
                'created': now_iso(),
            }
            dirty = True

    for slug in campaigns:
        campaign_dir(slug).mkdir(parents=True, exist_ok=True)

    moved: list[str] = []
    loose = sorted(SETUPS_DIR.glob('*.json'), key=lambda p: p.name.casefold())
    if loose or not campaigns:
        created_default = DEFAULT_CAMPAIGN_SLUG not in campaigns
        if created_default:
            campaigns[DEFAULT_CAMPAIGN_SLUG] = {
                'name': DEFAULT_CAMPAIGN_NAME,
                'description': 'Battle setups that were not connected to a campaign',
                'created': now_iso(),
            }
            dirty = True
        target = campaign_dir(DEFAULT_CAMPAIGN_SLUG)
        target.mkdir(parents=True, exist_ok=True)
        newest: tuple[float, str] | None = None
        for src in loose:
            mtime = src.stat().st_mtime
            dst = unique_setup_path(target, src.stem)
            src.replace(dst)
            moved.append(dst.stem)
            if newest is None or mtime > newest[0]:
                newest = (mtime, dst.stem)
        if created_default:
            # New campaign: add the empty "Default" battle setup (skipped if a
            # moved setup already uses that name).
            create_default_setup(DEFAULT_CAMPAIGN_SLUG)
            if newest is not None:
                # The most recently modified moved setup counts as "most recently
                # worked on", so activating Default opens it instead of the empty one.
                campaigns[DEFAULT_CAMPAIGN_SLUG]['last_setup'] = newest[1]

    if data['active'] not in campaigns:
        data['active'] = DEFAULT_CAMPAIGN_SLUG if DEFAULT_CAMPAIGN_SLUG in campaigns else sorted(campaigns, key=str.casefold)[0]
        dirty = True

    if dirty or moved:
        write_campaigns(data)
    if moved:
        print(f'Moved {len(moved)} unassigned battle setup(s) into campaign "{campaigns[DEFAULT_CAMPAIGN_SLUG]["name"]}": {", ".join(moved)}')
    return moved

def migrate_campaign_characters() -> None:
    """Create missing campaign character rosters from existing setup snapshots."""
    CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)

    data = read_campaigns()

    for slug, metadata in data["campaigns"].items():
        roster_path = campaign_characters_path(slug)

        if roster_path.exists():
            continue

        names = list_setups(slug)
        preferred = metadata.get("last_setup")

        if preferred in names:
            source_name = preferred
        elif names:
            source_name = max(
                names,
                key=lambda name: setup_path(name, slug).stat().st_mtime,
            )
        else:
            source_name = None

        characters: list[dict[str, Any]] = []

        if source_name is not None:
            try:
                raw = json.loads(
                    setup_path(source_name, slug).read_text(encoding="utf-8")
                )
                characters = normalize_state(raw)["characters"]
            except (OSError, json.JSONDecodeError, ValueError):
                characters = []

        save_campaign_characters(slug, characters)

# ============================================================================
# Campaign rosters and encounter persistence
# ============================================================================


def load_campaign_characters(slug: str) -> list[dict[str, Any]]:
    """Load campaign characters."""
    path = campaign_characters_path(slug)

    if not path.exists():
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            400,
            f"Unable to load campaign characters: {exc}",
        ) from exc

    characters = raw.get("characters", raw) if isinstance(raw, dict) else raw

    if not isinstance(characters, list):
        raise HTTPException(400, "Campaign character roster is invalid")

    return normalize_state({"characters": characters})["characters"]

def save_campaign_characters(
    slug: str,
    characters: list[dict[str, Any]],
) -> None:
    """Save campaign characters."""
    CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)

    path = campaign_characters_path(slug)
    temp = path.with_suffix(".tmp")

    temp.write_text(
        json.dumps({"characters": characters}, indent=2),
        encoding="utf-8",
    )
    temp.replace(path)

def save_active_campaign_characters() -> None:
    """Save active campaign characters."""
    save_campaign_characters(
        require_campaign(None),
        STATE["characters"],
    )

def load_setup_state(name: str, campaign: str) -> dict[str, Any]:
    """Load setup state."""
    path = setup_path(name, campaign)

    if not path.exists():
        raise HTTPException(404, "Saved setup not found")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(400, f"Unable to load setup: {exc}") from exc

    if not isinstance(raw, dict):
        raise HTTPException(400, "Saved setup must contain a JSON object")

    raw["characters"] = load_campaign_characters(campaign)

    try:
        return normalize_state(raw)
    except ValueError as exc:
        raise HTTPException(400, f"Unable to load setup: {exc}") from exc

def load_state() -> None:
    """Load state."""
    global STATE

    if not STATE_FILE.exists():
        STATE = normalize_state(STATE)
        return

    try:
        saved = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Unable to load state.json: {exc}") from exc

    saved_state = normalize_state(saved)
    reference = saved_state.get("active_setup")

    if isinstance(reference, dict):
        campaign = reference.get("campaign")
        name = reference.get("name")

        if isinstance(campaign, str) and isinstance(name, str):
            try:
                # This obtains the saved setup's monster list, then restores
                # campaign characters through the canonical setup loader.
                restored = load_setup_state(name, campaign)

                # Runtime working-state fields still come from state.json.
                restored["battle_order"] = saved_state["battle_order"]
                restored["activity_log"] = saved_state["activity_log"]
                restored["display"] = saved_state["display"]
                restored["active_setup"] = {
                    "campaign": campaign,
                    "name": name,
                }

                # If state.json is intentionally not storing monsters, use the
                # monsters from the saved setup. If a transitional/older file
                # does contain monsters, its data wins as working runtime data.
                if saved_state["monsters"]:
                    restored["monsters"] = saved_state["monsters"]

                STATE = normalize_state(restored)
                return
            except HTTPException:
                # The referenced campaign/setup no longer exists or is unreadable.
                # Continue below and preserve state.json as an unsaved encounter.
                pass

    # No valid setup association: state.json owns the working monsters.
    saved_state["active_setup"] = None
    STATE = normalize_state(saved_state)

def save_state() -> None:
    """Persist the current encounter and active setup reference."""
    persisted = copy.deepcopy(STATE)

    # Characters are campaign-owned and must not be duplicated in state.json.
    persisted["characters"] = []

    # When the working monsters come from a valid saved battle setup, the setup
    # file is authoritative. state.json stores only the setup reference.
    if active_setup_path() is not None:
        persisted["monsters"] = []
    else:
        # If the referenced setup disappeared, was renamed, or was deleted,
        # preserve the working monsters as an unsaved encounter.
        persisted["active_setup"] = None

    temp = STATE_FILE.with_suffix(".tmp")
    temp.write_text(
        json.dumps(persisted, indent=2),
        encoding="utf-8",
    )
    temp.replace(STATE_FILE)

def save_active_setup_monsters() -> bool:
    """
    Persist the working monster encounter into the currently active saved setup.

    Returns True when a saved setup was updated. Returns False when the current
    encounter is intentionally unsaved and therefore exists only in state.json.
    """
    reference = active_setup_reference()

    if reference is None:
        return False

    campaign = require_campaign(reference["campaign"])
    name = setup_slug(reference["name"])
    path = setup_path(name, campaign)

    if not path.exists():
        # The setup reference is stale. Preserve the current encounter as
        # unsaved runtime state rather than recreating an unexpected file.
        clear_active_setup()
        return False

    snapshot = setup_snapshot(STATE)
    temp = path.with_suffix(".tmp")

    temp.write_text(
        json.dumps(snapshot, indent=2),
        encoding="utf-8",
    )
    temp.replace(path)

    remember_setup(campaign, name)
    return True

# ============================================================================
# Activity logging
# ============================================================================


def log_battle_action(
    actor: dict[str, Any],
    target: dict[str, Any],
    action: Literal["damage", "heal", "buff", "debuff"],
    amount: int | None,
) -> None:
    """Log battle action."""
    STATE["activity_log"].append({
        "id": uuid.uuid4().hex,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_combatant_id": actor["id"],
        "active_combatant": actor["name"],
        "active_combatant_state": combatant_state(actor),
        "target_combatant_id": target["id"],
        "target_combatant": target["name"],
        "target_combatant_state": combatant_state(target),
        "action": action,
        "amount": amount,
    })

def log_hp_change(
    target: dict[str, Any],
    hp_delta: int,
) -> None:
    """Log hp change."""
    if hp_delta == 0:
        return

    actor = active_combatant()
    action = "heal" if hp_delta > 0 else "damage"

    STATE["activity_log"].append({
        "id": uuid.uuid4().hex,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_combatant_id": actor["id"] if actor else None,
        "active_combatant": actor["name"] if actor else "System",
        "active_combatant_state": combatant_state(actor),
        "target_combatant_id": target["id"],
        "target_combatant": target["name"],
        "target_combatant_state": combatant_state(target),
        "action": action,
        "amount": abs(hp_delta),
    })

# ============================================================================
# Image storage and monster creation
# ============================================================================


def save_image(upload: UploadFile) -> str:
    """Save image."""
    ext = Path(upload.filename or '').suffix.lower()
    if ext not in {'.png', '.jpg', '.jpeg', '.gif', '.webp'}:
        raise HTTPException(400, 'Image must be PNG, JPG, GIF, or WebP')
    dst = UPLOAD_DIR / f'{uuid.uuid4().hex}{ext}'
    with dst.open('wb') as f:
        shutil.copyfileobj(upload.file, f)
    return '/media/' + dst.name

def dnd_image(monster_species: str) -> str | None:
    """
    Find the dedicated D&D Beyond monster image for monster_species.

    Exact normalized name matches are collected from D&D Beyond search results.
    A match whose complete result HTML contains 'legacy' is preferred. The
    dedicated <img class="monster-image"> URL from that monster page is used,
    not a generic Open Graph image.
    """
    if not CONFIG["display"].get("dndbeyond_image_lookup", True):
        return None

    requested_name = re.sub(
        r"[^a-z0-9]+",
        " ",
        monster_species.casefold(),
    ).strip()

    if not requested_name:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 compatible; ScryingGlass/1.0",
        "Accept": "text/html,application/xhtml+xml",
    }

    try:
        search_url = (
            "https://www.dndbeyond.com/monsters"
            f"?filter-search={quote(monster_species)}"
        )

        request = Request(search_url, headers=headers)

        with urlopen(request, timeout=5) as response:
            search_html = response.read(1_000_000).decode(
                "utf-8",
                "replace",
            )

        candidates: list[tuple[bool, str]] = []

        for result in re.finditer(
            r'<a\b[^>]*href="(?P<href>/monsters/[^"]+)"[^>]*>'
            r"(?P<content>.*?)</a>",
            search_html,
            re.IGNORECASE | re.DOTALL,
        ):
            title = re.sub(r"<[^>]+>", "", result.group("content"))
            title = re.sub(r"\s+", " ", title).strip()

            normalized_title = re.sub(
                r"[^a-z0-9]+",
                " ",
                title.casefold(),
            ).strip()

            if normalized_title != requested_name:
                continue

            href = result.group("href")

            # Prefer an older / legacy monster page where D&D Beyond labels it
            # that way. Current exact-name matches remain fallback candidates.
            is_legacy = "legacy" in result.group(0).casefold()

            candidates.append((is_legacy, href))
        # True first: older/legacy exact matches are tried before current ones.
        candidates.sort(key=lambda candidate: not candidate[0])

        for _, href in candidates:
            monster_url = f"https://www.dndbeyond.com{href}"

            monster_request = Request(monster_url, headers=headers)
            with urlopen(monster_request, timeout=5) as response:
                monster_html = response.read(1_000_000).decode(
                    "utf-8",
                    "replace",
                )

            # Extract the actual monster illustration, not Open Graph metadata.
            image = re.search(
                r"""
                <img\b
                    [^>]*\bclass=["'][^"']*\bmonster-image\b[^"']*["']
                    [^>]*\bsrc=["'](?P<url>[^"']+)["']
                    [^>]*>
                """,
                monster_html,
                re.IGNORECASE | re.DOTALL | re.VERBOSE,
            )

            # Attributes are not guaranteed to remain in a fixed order. Retry
            # with src before class for pages that render it that way.
            if image is None:
                image = re.search(
                    r"""
                    <img\b
                        [^>]*\bsrc=["'](?P<url>[^"']+)["']
                        [^>]*\bclass=["'][^"']*\bmonster-image\b[^"']*["']
                        [^>]*>
                    """,
                    monster_html,
                    re.IGNORECASE | re.DOTALL | re.VERBOSE,
                )

            if image is not None:
                image_url = image.group("url").strip()

                if image_url.startswith("//"):
                    image_url = f"https:{image_url}"
                elif image_url.startswith("/"):
                    image_url = (
                        "https://www.dndbeyond.com"
                        f"{image_url}"
                    )

                return image_url

        return None

    except Exception:
        # Image lookup is optional and must not block monster creation.
        return None

def make_monster(fields: dict[str, Any], color: str, upload: UploadFile | None, image_url: str | None=None) -> dict[str, Any]:
    """Make monster."""
    hp = fields['hp']
    return {'id': uuid.uuid4().hex, **fields, 'max_hp': hp, 'original_hp': hp, 'color': color, 'image_url': image_url if image_url is not None else save_image(upload) if upload and upload.filename else dnd_image(fields['monster_species']), 'active': False, 'alive': True, 'visible': False, 'ally': False, 'initiative': None, 'original_initiative': None, 'show_ac': False, 'show_hp': False, 'show_initiative': False, 'in_turn': False}

def make_monsters(
    fields: dict[str, Any],
    color: str,
    quantity: int,
    image_url: str | None,
) -> list[dict[str, Any]]:
    """Make monsters."""
    return [
        make_monster(
            {
                **fields,
                'name': (
                    fields['name']
                    if quantity == 1
                    else f"{fields['name']} - {number}"
                ),
            },
            color,
            None,
            image_url,
        )
        for number in range(1, quantity + 1)
    ]

# ============================================================================
# Battle order and turn management
# ============================================================================


def clear_turns() -> None:
    """Clear turns."""
    for x in entities():
        x['in_turn'] = False

def clean_order() -> None:
    """Remove combatants that are no longer eligible from battle order."""
    known = {x['id'] for x in entities()}
    STATE['battle_order'] = [x for x in STATE['battle_order'] if x in known]

def insert_into_battle_order(combatant: dict[str, Any]) -> None:
    """Insert a newly activated living combatant into an existing battle order.

    Higher numeric initiative acts first. On equal initiative, the newly added
    combatant is placed after all existing combatants with that same initiative.
    Combatants without initiative are placed after numeric initiatives.
    """
    if not STATE['battle_order']:
        return
    if not combatant.get('active') or not combatant.get('alive', True):
        return
    combatant_id = combatant['id']
    if combatant_id in STATE['battle_order']:
        return
    combatant_initiative = combatant.get('initiative')
    has_numeric_initiative = isinstance(combatant_initiative, int) and (not isinstance(combatant_initiative, bool))
    insert_at = len(STATE['battle_order'])
    for index, existing_id in enumerate(STATE['battle_order']):
        existing = entity(existing_id)
        if existing is None:
            continue
        existing_initiative = existing.get('initiative')
        existing_has_numeric_initiative = isinstance(existing_initiative, int) and (not isinstance(existing_initiative, bool))
        if not has_numeric_initiative:
            continue
        if not existing_has_numeric_initiative:
            insert_at = index
            break
        if existing_initiative < combatant_initiative:
            insert_at = index
            break
    STATE['battle_order'].insert(insert_at, combatant_id)

def sort_admin_by_initiative() -> None:
    """Sort admin by initiative."""
    STATE['monsters'].sort(key=admin_initiative_key)
    STATE['characters'].sort(key=admin_initiative_key)

def sort_admin_by_max_hp() -> None:
    """Sort admin by max hp."""
    STATE['monsters'].sort(key=admin_max_hp_key)
    STATE['characters'].sort(key=admin_max_hp_key)

def set_turn(x: dict[str, Any], requested: bool | None) -> None:
    """Set turn."""
    if requested is False:
        x['in_turn'] = False
        return
    if requested is not True:
        return
    if not x.get('active') or not x.get('alive', True):
        raise HTTPException(400, 'Only an active living combatant may have the battle turn')
    clear_turns()
    x['in_turn'] = True
    x['visible'] = True

def eligible() -> list[dict[str, Any]]:
    """Eligible."""
    return [x for x in entities() if x.get('active') and x.get('alive', True)]

def begin_battle(order: list[str]) -> None:
    """Begin battle."""
    wanted = {x['id'] for x in eligible()}
    if len(order) != len(wanted) or set(order) != wanted:
        raise HTTPException(400, 'Battle order must include every active living combatant exactly once')
    STATE['battle_order'] = order
    clear_turns()
    if order:
        entity(order[0])['in_turn'] = True
        entity(order[0])['visible'] = True

def advance_turn() -> dict[str, Any] | None:
    """Advance turn."""
    ids = {x['id'] for x in eligible()}
    if not ids:
        clear_turns()
        STATE['battle_order'] = []
        return None
    order = [i for i in STATE['battle_order'] if i in ids]
    order += [x['id'] for x in sorted(eligible(), key=lambda z: (-numeric_initiative(z), z['name'].lower())) if x['id'] not in order]
    STATE['battle_order'] = order
    pos = next((n for n, i in enumerate(order) if entity(i).get('in_turn')), -1)
    clear_turns()
    target = entity(order[(pos + 1) % len(order)])
    target['in_turn'] = True
    target['visible'] = True
    return target

def selected_entities(
    kind: Literal["characters", "monsters"],
    ids: list[str],
) -> list[dict[str, Any]]:
    """Selected entities."""
    selected_ids = unique_ids(ids)
    items = STATE[kind]
    by_id = {item["id"]: item for item in items}
    missing = [ident for ident in selected_ids if ident not in by_id]

    if missing:
        raise HTTPException(404, f"Selected {kind[:-1]} no longer exists")

    return [by_id[ident] for ident in selected_ids]

# ============================================================================
# Change notifications and WebSocket broadcasting
# ============================================================================


async def broadcast() -> None:
    """Broadcast."""
    message = json.dumps({'type': 'state', 'state': public_state()})
    stale = []
    for ws in SOCKETS:
        try:
            await ws.send_text(message)
        except Exception:
            stale.append(ws)
    for ws in stale:
        SOCKETS.discard(ws)

async def changed() -> None:
    """Persist shared state and broadcast the updated public state under the lock."""
    async with LOCK:
        save_state()
    await broadcast()

async def monster_changed() -> None:
    """Monster changed."""
    async with LOCK:
        save_active_setup_monsters()
        save_state()

    await broadcast()

async def character_changed() -> None:
    """Character changed."""
    async with LOCK:
        save_active_campaign_characters()
        save_state()

    await broadcast()

async def combatants_changed(
    *,
    monsters: bool = False,
    characters: bool = False,
) -> None:
    """Combatants changed."""
    async with LOCK:
        if monsters:
            save_active_setup_monsters()

        if characters:
            save_active_campaign_characters()

        save_state()

    await broadcast()


# ============================================================================
# FastAPI application construction and route registration
# ============================================================================


admin = FastAPI(title='Scrying Glass Admin')
client = FastAPI(title='Scrying Glass Client')
_server_context = sys.modules[__name__]
admin_api = AdminAPI(_server_context, admin)
client_api = ClientAPI(_server_context, client)

# ============================================================================
# Command-line configuration, storage initialization and servers
# ============================================================================


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GM-controlled real-time battle display')
    parser.add_argument('--config', type=Path)
    parser.add_argument('--bind')
    parser.add_argument('--admin-port', type=int)
    parser.add_argument('--client-port', type=int)
    parser.add_argument('--storage-dir', type=Path)
    args = parser.parse_args()
    try:
        CONFIG = load_config(args.config)
    except Exception as exc:
        sys.exit(f'Invalid configuration: {exc}')
    if args.bind:
        CONFIG['network']['bind'] = args.bind
    if args.admin_port:
        CONFIG['network']['admin_port'] = args.admin_port
    if args.client_port:
        CONFIG['network']['client_port'] = args.client_port
    if args.storage_dir:
        CONFIG['storage_dir'] = str(args.storage_dir)
    DATA_DIR = Path(CONFIG['storage_dir']).expanduser().resolve()
    legacy_dir = Path(LEGACY_STORAGE_DIR).expanduser().resolve()
    if DATA_DIR == Path(DEFAULT_STORAGE_DIR).expanduser().resolve() and not DATA_DIR.exists() and legacy_dir.is_dir():
        # Installation from before the rename that relies on the default storage_dir.
        print(f'Using existing data directory {legacy_dir} (from before the rename to Scrying Glass). '
              f'Rename it to {DATA_DIR} or set storage_dir in the configuration to silence this message.')
        DATA_DIR = legacy_dir

    STATIC_DIR = Path(__file__).resolve().parent / "static"
    if not STATIC_DIR.is_dir():
        sys.exit(f"Static asset directory does not exist: {STATIC_DIR}")

    UPLOAD_DIR = DATA_DIR / "uploads"
    SETUPS_DIR = DATA_DIR / "setups"
    CHARACTERS_DIR = DATA_DIR / "characters"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    SETUPS_DIR.mkdir(parents=True, exist_ok=True)
    CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)

    STATE_FILE = DATA_DIR / "state.json"
    CAMPAIGNS_FILE = DATA_DIR / "campaigns.json"

    migrate_unassigned_setups()
    migrate_campaign_characters()
    load_state()

    # The active campaign roster is authoritative after restart.
    STATE["characters"] = load_campaign_characters(active_campaign())
    clean_order()
    save_state()
    admin.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="admin-static")   
    admin.mount('/media', StaticFiles(directory=str(UPLOAD_DIR)), name='admin-media')
    client.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="client-static")   
    client.mount('/media', StaticFiles(directory=str(UPLOAD_DIR)), name='client-media')

    async def serve():
        """Run the admin and client servers concurrently with shared runtime state."""
        common = {'host': CONFIG['network']['bind'], 'log_level': 'info', 'access_log': False}
        await asyncio.gather(uvicorn.Server(uvicorn.Config(admin, port=CONFIG['network']['admin_port'], **common)).serve(), uvicorn.Server(uvicorn.Config(client, port=CONFIG['network']['client_port'], **common)).serve())
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
