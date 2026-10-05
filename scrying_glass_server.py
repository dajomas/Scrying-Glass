"""Scrying Glass v4.16 (Python 3.14+), formerly "Monster Display".

Dependencies:
  python3.14 -m pip install 'fastapi>=0.115' 'uvicorn[standard]>=0.30' 'PyYAML>=6.0' python-multipart

Run:
  python3.14 scrying_glass_server.py --config config.yaml
"""
from __future__ import annotations
import argparse, asyncio, copy, csv, hashlib, hmac, io, json, random, re, secrets, shutil, sys, uuid, uvicorn, yaml
from pathlib import Path
from typing import Any, Callable, Literal
from urllib.parse import quote
from urllib.request import Request, urlopen
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request as FastAPIRequest, UploadFile, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from login_html import LOGIN
from admin_html import ADMIN_HTML
from client_html import CLIENT_HTML
from datetime import datetime, timezone

# Default storage directory before the rename. Used as a fallback when the new
# default directory does not exist yet but the old one does.
DEFAULT_STORAGE_DIR = './scrying-glass-data'
LEGACY_STORAGE_DIR = './monster-display-data'
DEFAULT_CONFIG = {'network': {'bind': '0.0.0.0', 'admin_port': 3000, 'client_port': 4000}, 'storage_dir': DEFAULT_STORAGE_DIR, 'security': {'users': [{'username': 'admin', 'role': 'admin', 'password': 'CHANGE-ME'}, {'username': 'client', 'role': 'client', 'password': 'CHANGE-ME'}]}, 'display': {'background': '#080b14', 'entry_direction': 'from_bottom', 'exit_direction': 'to_bottom', 'monster_width_percent': 45, 'dndbeyond_image_lookup': True}}
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

DEFAULT_SETUP_NAME = 'default'
DEFAULT_CAMPAIGN_SLUG = 'default'
DEFAULT_CAMPAIGN_NAME = 'Default'
DEFAULT_VIEW_BACKGROUND = '#080b14'

ADMIN_SESSION_COOKIE = "scrying_glass_admin_session"
CLIENT_SESSION_COOKIE = "scrying_glass_client_session"
# Cookies used before the rename to Scrying Glass; removed on successful login.
LEGACY_SESSION_COOKIES = ("monster_session", "monster_admin_session", "monster_client_session")

DICE_HP_RE = re.compile(
    r"""
    ^\s*
    (?P<count>[1-9]\d*)
    d\s*
    (?P<sides>[2-9]\d*|1\d+)
    (?:
        \s*
        (?P<operator>[+-])
        \s*
        (?P<modifier>\d+)
    )?
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

MAX_HP_DICE_COUNT = 100
MAX_HP_DIE_SIDES = 1_000
MAX_HP_MODIFIER = 100_000

def parse_hp_dice_expression(value: str) -> tuple[int, int, int] | None:
    """Return (dice_count, die_sides, modifier), or None when not dice notation."""
    match = DICE_HP_RE.fullmatch(value)

    if match is None:
        return None

    count = int(match.group("count"))
    sides = int(match.group("sides"))
    modifier = int(match.group("modifier") or 0)

    if match.group("operator") == "-":
        modifier = -modifier

    if count > MAX_HP_DICE_COUNT:
        raise HTTPException(
            400,
            f"HP dice count must not exceed {MAX_HP_DICE_COUNT}",
        )

    if sides > MAX_HP_DIE_SIDES:
        raise HTTPException(
            400,
            f"HP die sides must not exceed {MAX_HP_DIE_SIDES}",
        )

    if abs(modifier) > MAX_HP_MODIFIER:
        raise HTTPException(
            400,
            f"HP dice modifier must be between "
            f"-{MAX_HP_MODIFIER} and {MAX_HP_MODIFIER}",
        )

    return count, sides, modifier


def roll_hp_dice(dice_count: int, die_sides: int, modifier: int) -> int:
    """Roll dice independently and return a non-negative HP total."""
    rolled = sum(random.randint(1, die_sides) for _ in range(dice_count))
    return max(0, rolled + modifier)


def hp_value_factory(
    hp_range_start_raw: str,
    hp_range_end_raw: str | None,
) -> Callable[[], int]:
    """Validate HP input and return a function that produces one monster's HP."""
    start = str(hp_range_start_raw or "").strip()
    end = str(hp_range_end_raw or "").strip()

    if not start:
        raise HTTPException(400, "HP Range start is required")

    dice = parse_hp_dice_expression(start)

    if dice is not None:
        if end:
            raise HTTPException(
                400,
                "HP Range end must be empty when HP Range start is a dice expression",
            )

        dice_count, die_sides, modifier = dice
        return lambda: roll_hp_dice(dice_count, die_sides, modifier)

    try:
        numeric_start = int(start)
    except ValueError as exc:
        raise HTTPException(
            400,
            "HP Range start must be a non-negative integer or a dice expression such as 3d8+9",
        ) from exc

    if numeric_start < 0 or str(numeric_start) != start:
        raise HTTPException(
            400,
            "HP Range start must be a non-negative whole number",
        )

    if not end:
        return lambda: numeric_start

    try:
        numeric_end = int(end)
    except ValueError as exc:
        raise HTTPException(
            400,
            "HP Range end must be a non-negative integer",
        ) from exc

    if numeric_end < 0 or str(numeric_end) != end:
        raise HTTPException(
            400,
            "HP Range end must be a non-negative whole number",
        )

    if numeric_start > numeric_end:
        raise HTTPException(400, "HP Range start cannot be higher than HP Range end")

    return lambda: random.randint(numeric_start, numeric_end)

def merge(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out

def load_config(p: Path | None) -> dict[str, Any]:
    if p is None:
        return DEFAULT_CONFIG
    raw = p.read_text(encoding='utf-8')
    x = json.loads(raw) if p.suffix.lower() == '.json' else yaml.safe_load(raw)
    if not isinstance(x, dict):
        raise ValueError('Configuration root must be a mapping/object')
    return merge(DEFAULT_CONFIG, x)

def password_hash(password: str, salt: bytes | None=None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1)
    return f'scrypt${salt.hex()}${digest.hex()}'

def password_ok(password: str, stored: str) -> bool:
    if stored.startswith('scrypt$'):
        _, salt, digest = stored.split('$', 2)
        return hmac.compare_digest(password_hash(password, bytes.fromhex(salt)).split('$', 2)[2], digest)
    return hmac.compare_digest(password, stored)

def user(name: str) -> dict[str, Any] | None:
    return next((x for x in CONFIG['security']['users'] if x.get('username') == name), None)

def entities() -> list[dict[str, Any]]:
    return [*STATE['monsters'], *STATE['characters']]

def entity(ident: str) -> dict[str, Any] | None:
    return next((x for x in entities() if x['id'] == ident), None)

def combatant_state(combatant: dict[str, Any] | None) -> str:
    if combatant is None:
        return "unknown"

    return "alive" if combatant.get("alive", True) else "dead"

def active_combatant() -> dict[str, Any] | None:
    return next(
        (combatant for combatant in entities() if combatant.get("in_turn")),
        None,
    )

def log_battle_action(
    actor: dict[str, Any],
    target: dict[str, Any],
    action: Literal["damage", "heal", "buff", "debuff"],
    amount: int | None,
) -> None:
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

def update_alive_state(combatant: dict[str, Any]) -> None:
    combatant["alive"] = combatant.get("hp", 0) > 0

    if not combatant["alive"]:
        combatant["visible"] = True
        combatant["in_turn"] = False

def log_hp_change(
    target: dict[str, Any],
    hp_delta: int,
) -> None:
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

def configured_background() -> str:
    return str(
        CONFIG.get('display', {}).get('background', DEFAULT_VIEW_BACKGROUND)
    ).strip() or DEFAULT_VIEW_BACKGROUND

def normalize_display(raw: Any) -> dict[str, str]:
    display = raw if isinstance(raw, dict) else {}
    background = str(
        display.get('background', configured_background())
    ).strip()

    return {
        'background': background or configured_background(),
    }

def normalize_state(raw: dict[str, Any]) -> dict[str, Any]:
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

def load_campaign_characters(slug: str) -> list[dict[str, Any]]:
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
    CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)

    path = campaign_characters_path(slug)
    temp = path.with_suffix(".tmp")

    temp.write_text(
        json.dumps({"characters": characters}, indent=2),
        encoding="utf-8",
    )
    temp.replace(path)

def save_active_campaign_characters() -> None:
    save_campaign_characters(
        require_campaign(None),
        STATE["characters"],
    )

def setup_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    snapshot = copy.deepcopy(state)
    snapshot["characters"] = []

    monster_ids = {
        monster["id"]
        for monster in snapshot["monsters"]
    }

    snapshot["battle_order"] = [
        combatant_id
        for combatant_id in snapshot["battle_order"]
        if combatant_id in monster_ids
    ]

    return snapshot

def load_setup_state(name: str, campaign: str) -> dict[str, Any]:
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

async def monster_changed() -> None:
    async with LOCK:
        save_active_setup_monsters()
        save_state()

    await broadcast()

async def character_changed() -> None:
    async with LOCK:
        save_active_campaign_characters()
        save_state()

    await broadcast()

async def combatants_changed(
    *,
    monsters: bool = False,
    characters: bool = False,
) -> None:
    async with LOCK:
        if monsters:
            save_active_setup_monsters()

        if characters:
            save_active_campaign_characters()

        save_state()

    await broadcast()

def public_state() -> dict[str, Any]:
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

def setup_slug(name: str) -> str:
    slug = re.sub('[^a-z0-9]+', '-', name.strip().lower()).strip('-')
    if not slug:
        raise HTTPException(400, 'Setup name must contain letters or numbers')
    return slug[:80]

def setup_path(name: str, campaign: str | None = None) -> Path:
    return campaign_dir(require_campaign(campaign)) / (setup_slug(name) + '.json')

def campaign_characters_path(slug: str) -> Path:
    return CHARACTERS_DIR / f"{slug}.json"

def list_setups(campaign: str | None = None) -> list[str]:
    return sorted((p.stem for p in campaign_dir(require_campaign(campaign)).glob('*.json')), key=str.casefold)

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

# ---------------------------------------------------------------------------
# Campaigns
#
# Layout on disk:
#   <storage_dir>/campaigns.json               registry: active campaign + metadata
#   <storage_dir>/setups/<campaign-slug>/*.json battle setups of that campaign
#
# Battle setups stored directly in <storage_dir>/setups/*.json (pre-campaign
# layout) are "not connected to a campaign" and are moved into the "Default"
# campaign by migrate_unassigned_setups().
# ---------------------------------------------------------------------------

def campaign_slug(name: str) -> str:
    slug = re.sub('[^a-z0-9]+', '-', name.strip().lower()).strip('-')
    if not slug:
        raise HTTPException(400, 'Campaign name must contain letters or numbers')
    return slug[:80]

def campaign_dir(slug: str) -> Path:
    return SETUPS_DIR / slug

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_campaigns() -> dict[str, Any]:
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
    temp = CAMPAIGNS_FILE.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
    temp.replace(CAMPAIGNS_FILE)

def unique_setup_path(directory: Path, stem: str) -> Path:
    dst = directory / f'{stem}.json'
    counter = 2
    while dst.exists():
        dst = directory / f'{stem}-{counter}.json'
        counter += 1
    return dst

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

def active_campaign() -> str:
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

def reset_imported_monster(source: dict[str, Any]) -> dict[str, Any]:
    item = copy.deepcopy(source)
    item['id'] = uuid.uuid4().hex

    # Keep the source setup's current HP and current Max HP.
    # Do not overwrite hp with original_hp during setup import.
    item['alive'] = item.get('hp', 0) > 0

    item['initiative'] = item.get('original_initiative')
    item['active'] = False
    item['visible'] = False
    item['in_turn'] = False
    item['show_ac'] = False
    item['show_hp'] = False
    item['show_initiative'] = False
    return item

async def broadcast() -> None:
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
    async with LOCK:
        save_state()
    await broadcast()

def require(
    role: Literal["admin", "client"],
    cookie_name: str,
):
    async def dependency(request: FastAPIRequest) -> dict[str, str]:
        session = SESSIONS.get(
            request.cookies.get(cookie_name, "")
        )

        if not session or (
            role == "admin" and session["role"] != "admin"
        ):
            raise HTTPException(401, "Sign in required")

        return session

    return dependency

def parse_monster(raw: bytes) -> dict[str, Any]:
    try:
        x = json.loads(raw.decode('utf-8'))
    except Exception as exc:
        raise HTTPException(400, '.monster must contain UTF-8 JSON') from exc
    name = str(x.get('name', '')).strip()
    kind = str(x.get('type', '')).strip()
    hp = re.search('-?\\d+', str(x.get('hpText', x.get('hp', ''))))
    acraw = x.get('ac') or x.get('armorClass') or x.get('otherArmorDesc') or x.get('natArmorBonus')
    ac = re.search('\\d+', str(acraw)) if acraw is not None else None
    if not name or not kind or (not hp) or (not ac):
        raise HTTPException(400, '.monster needs usable name, type, AC, and HP')
    return {'name': name, 'monster_species': kind, 'ac': int(ac.group()), 'hp': int(hp.group())}

def csv_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def csv_int(
    row: dict[str, Any],
    field: str,
    *,
    default: int | None = None,
    minimum: int | None = None,
    maximum: int | None = None,
    row_number: int,
) -> int | None:
    raw = csv_text(row.get(field))

    if not raw:
        return default

    try:
        value = int(raw)
    except ValueError as exc:
        raise HTTPException(
            400,
            f"CSV row {row_number}: {field} must be a whole number",
        ) from exc

    if minimum is not None and value < minimum:
        raise HTTPException(
            400,
            f"CSV row {row_number}: {field} must be at least {minimum}",
        )

    if maximum is not None and value > maximum:
        raise HTTPException(
            400,
            f"CSV row {row_number}: {field} must be at most {maximum}",
        )

    return value


def csv_bool(
    row: dict[str, Any],
    field: str,
    *,
    default: bool = False,
    row_number: int,
) -> bool:
    raw = csv_text(row.get(field)).casefold()

    if not raw:
        return default

    if raw in {"1", "true", "yes", "y", "on"}:
        return True

    if raw in {"0", "false", "no", "n", "off"}:
        return False

    raise HTTPException(
        400,
        f"CSV row {row_number}: {field} must be true/false, yes/no, or 1/0",
    )


def csv_rows(raw: bytes) -> list[dict[str, str]]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(400, "CSV must be UTF-8 encoded") from exc

    try:
        reader = csv.DictReader(text.splitlines())
    except csv.Error as exc:
        raise HTTPException(400, "Could not read CSV file") from exc

    if not reader.fieldnames:
        raise HTTPException(400, "CSV must contain a header row")

    reader.fieldnames = [
        csv_text(name).casefold()
        for name in reader.fieldnames
        if name is not None
    ]

    rows: list[dict[str, str]] = []

    try:
        for row in reader:
            cleaned = {
                csv_text(key).casefold(): csv_text(value)
                for key, value in row.items()
                if key is not None
            }

            # Ignore fully blank spreadsheet rows.
            if any(cleaned.values()):
                rows.append(cleaned)
    except csv.Error as exc:
        raise HTTPException(400, "Could not read CSV file") from exc

    if not rows:
        raise HTTPException(400, "CSV contains no data rows")

    return rows

def csv_monster(row: dict[str, str], row_number: int) -> dict[str, Any]:
    name = csv_text(row.get("name"))
    monster_species = csv_text(row.get("monster_species") or row.get('monster_species') or row.get("type"))
    ac = csv_int(row, "ac", minimum=0, maximum=999, row_number=row_number)
    hp = csv_int(row, "hp", minimum=-99999, maximum=99999, row_number=row_number)

    if not name:
        raise HTTPException(400, f"CSV row {row_number}: name is required")

    if not monster_species:
        raise HTTPException(
            400,
            f"CSV row {row_number}: monster_species, monster_species or type is required",
        )

    if ac is None:
        raise HTTPException(400, f"CSV row {row_number}: ac is required")

    if hp is None:
        raise HTTPException(400, f"CSV row {row_number}: hp is required")

    maximum_hp = csv_int(
        row,
        "max_hp",
        default=hp,
        minimum=0,
        maximum=99999,
        row_number=row_number,
    )

    original_hp = csv_int(
        row,
        "original_hp",
        default=maximum_hp,
        minimum=0,
        maximum=99999,
        row_number=row_number,
    )

    initiative = csv_int(
        row,
        "initiative",
        default=None,
        minimum=-100,
        maximum=100,
        row_number=row_number,
    )

    ident = csv_text(row.get("id")) or uuid.uuid4().hex

    return {
        "id": ident,
        "name": name,
        "monster_species": monster_species,
        "ac": ac,
        "hp": hp,
        "max_hp": maximum_hp,
        "original_hp": original_hp,
        "color": csv_text(row.get("color"), "#842029"),
        "image_url": csv_text(row.get("image_url")) or None,
        "active": csv_bool(row, "active", default=False, row_number=row_number),
        "alive": csv_bool(
            row,
            "alive",
            default=hp >= 0,
            row_number=row_number,
        ),
        "visible": csv_bool(row, "visible", default=False, row_number=row_number),
        "ally": csv_bool(row, "ally", default=False, row_number=row_number),
        "initiative": initiative,
        "original_initiative": csv_int(
            row,
            "original_initiative",
            default=initiative,
            minimum=-100,
            maximum=100,
            row_number=row_number,
        ),
        "show_ac": csv_bool(row, "show_ac", default=False, row_number=row_number),
        "show_hp": csv_bool(row, "show_hp", default=False, row_number=row_number),
        "show_initiative": csv_bool(
            row,
            "show_initiative",
            default=False,
            row_number=row_number,
        ),
        "in_turn": False,
    }


def csv_character(row: dict[str, str], row_number: int) -> dict[str, Any]:
    name = csv_text(row.get("name"))

    if not name:
        raise HTTPException(400, f"CSV row {row_number}: name is required")

    hp = csv_int(
        row,
        "hp",
        default=1,
        minimum=-99999,
        maximum=99999,
        row_number=row_number,
    )

    maximum_hp = csv_int(
        row,
        "max_hp",
        default=max(hp, 0),
        minimum=0,
        maximum=99999,
        row_number=row_number,
    )

    initiative = csv_int(
        row,
        "initiative",
        default=None,
        minimum=-100,
        maximum=100,
        row_number=row_number,
    )

    ident = csv_text(row.get("id")) or uuid.uuid4().hex

    return {
        "id": ident,
        "name": name,
        "color": csv_text(row.get("color"), "#1f4e79"),
        "hp": hp,
        "max_hp": maximum_hp,
        "original_hp": csv_int(
            row,
            "original_hp",
            default=maximum_hp,
            minimum=0,
            maximum=99999,
            row_number=row_number,
        ),
        "initiative": initiative,
        "original_initiative": csv_int(
            row,
            "original_initiative",
            default=initiative,
            minimum=-100,
            maximum=100,
            row_number=row_number,
        ),
        "active": csv_bool(row, "active", default=False, row_number=row_number),
        "alive": csv_bool(
            row,
            "alive",
            default=hp >= 0,
            row_number=row_number,
        ),
        "visible": csv_bool(row, "visible", default=False, row_number=row_number),
        "in_turn": False,
    }

def save_image(upload: UploadFile) -> str:
    ext = Path(upload.filename or '').suffix.lower()
    if ext not in {'.png', '.jpg', '.jpeg', '.gif', '.webp'}:
        raise HTTPException(400, 'Image must be PNG, JPG, GIF, or WebP')
    dst = UPLOAD_DIR / f'{uuid.uuid4().hex}{ext}'
    with dst.open('wb') as f:
        shutil.copyfileobj(upload.file, f)
    return '/media/' + dst.name

def dnd_image(monster_name: str) -> str | None:
    if not CONFIG['display'].get('dndbeyond_image_lookup', True):
        return None

    requested_name = re.sub(
        r'[^a-z0-9]+',
        ' ',
        monster_name.casefold(),
    ).strip()

    if not requested_name:
        return None

    try:
        request = Request(
            'https://www.dndbeyond.com/monsters'
            '?filter-search=' + quote(monster_name),
            headers={
                'User-Agent': 'Mozilla/5.0 '
                '(compatible; ScryingGlass/1.0)',
                'Accept': 'text/html,application/xhtml+xml',
            },
        )

        with urlopen(request, timeout=5) as response:
            html = response.read(1_000_000).decode('utf-8', 'replace')

        # D&D Beyond result cards generally contain a monster page link and title.
        # Only accept an exact normalized result title.
        results = re.finditer(
            r'<a[^>]+href=["\'](?P<href>/monsters/[^"\']+)["\'][^>]*>'
            r'(?P<content>.*?)</a>',
            html,
            re.IGNORECASE | re.DOTALL,
        )

        for result in results:
            title = re.sub(r'<[^>]+>', ' ', result.group('content'))
            title = re.sub(r'\s+', ' ', title).strip()
            normalized_title = re.sub(
                r'[^a-z0-9]+',
                ' ',
                title.casefold(),
            ).strip()

            if normalized_title != requested_name:
                continue

            monster_url = (
                'https://www.dndbeyond.com' + result.group('href')
            )

            monster_request = Request(
                monster_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 '
                    '(compatible; ScryingGlass/1.0)',
                    'Accept': 'text/html,application/xhtml+xml',
                },
            )

            with urlopen(monster_request, timeout=5) as response:
                monster_html = response.read(1_000_000).decode(
                    'utf-8',
                    'replace',
                )

            image = re.search(
                r'<meta[^>]+property=["\']og:image["\'][^>]+'
                r'content=["\'](?P<url>[^"\']+)',
                monster_html,
                re.IGNORECASE,
            )

            if image:
                return image.group('url')

        return None
    except Exception:
        return None

def make_monster(fields: dict[str, Any], color: str, upload: UploadFile | None, image_url: str | None=None) -> dict[str, Any]:
    hp = fields['hp']
    return {'id': uuid.uuid4().hex, **fields, 'max_hp': hp, 'original_hp': hp, 'color': color, 'image_url': image_url if image_url is not None else save_image(upload) if upload and upload.filename else dnd_image(fields['monster_species']), 'active': False, 'alive': True, 'visible': False, 'ally': False, 'initiative': None, 'original_initiative': None, 'show_ac': False, 'show_hp': False, 'show_initiative': False, 'in_turn': False}

def make_monsters(
    fields: dict[str, Any],
    color: str,
    quantity: int,
    image_url: str | None,
) -> list[dict[str, Any]]:
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

def clear_turns() -> None:
    for x in entities():
        x['in_turn'] = False

def clean_order() -> None:
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

def reset_entity(x: dict[str, Any]) -> None:
    x['active'] = False
    x['alive'] = True
    x['visible'] = False
    x['in_turn'] = False
    x['initiative'] = x.get('original_initiative')
    if 'monster_species' in x:
        x['hp'] = x['original_hp']
        x['max_hp'] = x['original_hp']
        x['show_ac'] = False
        x['show_hp'] = False
        x['show_initiative'] = False
    else:
        x['hp'] = x['max_hp']

def admin_initiative_key(x: dict[str, Any]) -> tuple[int, str]:
    value = x.get('initiative')
    initiative = value if isinstance(value, int) and (not isinstance(value, bool)) else -999
    return (-initiative, str(x.get('name', '')).casefold())

def admin_max_hp_key(x: dict[str, Any]) -> tuple[int, str]:
    return (-int(x.get('max_hp', 0)), str(x.get('name', '')).casefold())

def sort_admin_by_initiative() -> None:
    STATE['monsters'].sort(key=admin_initiative_key)
    STATE['characters'].sort(key=admin_initiative_key)

def sort_admin_by_max_hp() -> None:
    STATE['monsters'].sort(key=admin_max_hp_key)
    STATE['characters'].sort(key=admin_max_hp_key)

def set_turn(x: dict[str, Any], requested: bool | None) -> None:
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

def numeric_initiative(x: dict[str, Any]) -> int:
    v = x.get('initiative')
    return v if isinstance(v, int) and (not isinstance(v, bool)) else -999

def eligible() -> list[dict[str, Any]]:
    return [x for x in entities() if x.get('active') and x.get('alive', True)]

def begin_battle(order: list[str]) -> None:
    wanted = {x['id'] for x in eligible()}
    if len(order) != len(wanted) or set(order) != wanted:
        raise HTTPException(400, 'Battle order must include every active living combatant exactly once')
    STATE['battle_order'] = order
    clear_turns()
    if order:
        entity(order[0])['in_turn'] = True
        entity(order[0])['visible'] = True

def advance_turn() -> dict[str, Any] | None:
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

def unique_ids(ids: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()

    for ident in ids:
        if not isinstance(ident, str) or not ident.strip():
            raise HTTPException(400, "Bulk action contains an invalid combatant ID")
        if ident not in seen:
            seen.add(ident)
            unique.append(ident)

    if not unique:
        raise HTTPException(400, "Bulk action requires at least one combatant ID")

    return unique


def selected_entities(
    kind: Literal["characters", "monsters"],
    ids: list[str],
) -> list[dict[str, Any]]:
    selected_ids = unique_ids(ids)
    items = STATE[kind]
    by_id = {item["id"]: item for item in items}
    missing = [ident for ident in selected_ids if ident not in by_id]

    if missing:
        raise HTTPException(404, f"Selected {kind[:-1]} no longer exists")

    return [by_id[ident] for ident in selected_ids]

class DisplayBackgroundUpdate(BaseModel):
    background: str = Field(min_length=1, max_length=4096)

class BulkCombatantAction(BaseModel):
    action: str
    ids: list[str] = Field(min_length=1, max_length=500)

class MonsterUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    monster_species: str | None = Field(default=None, min_length=1, max_length=100)
    ac: int | None = Field(default=None, ge=0, le=999)
    max_hp: int | None = Field(default=None, ge=0, le=99999)
    original_hp: int | None = Field(default=None, ge=0, le=99999)
    color: str | None = Field(default=None, min_length=1, max_length=40)
    active: bool | None = None
    ally: bool | None = None
    visible: bool | None = None
    initiative: int | None = Field(default=None, ge=-100, le=100)
    hp: int | None = Field(default=None, ge=-99999, le=99999)
    hp_delta: int | None = Field(default=None, ge=-99999, le=99999)
    show_ac: bool | None = None
    show_hp: bool | None = None
    show_initiative: bool | None = None
    in_turn: bool | None = None

class MonsterBulkUpdate(BaseModel):
    field: Literal["active", "ally", "show_ac", "show_hp", "show_initiative"]

class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str = Field(min_length=1, max_length=40)
    hp: int = Field(default=1, ge=0, le=99999)
    initiative: int | None = Field(default=None, ge=-100, le=100)

class CharacterUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, min_length=1, max_length=40)
    active: bool | None = None
    alive: bool | None = None
    visible: bool | None = None
    initiative: int | None = Field(default=None, ge=-100, le=100)
    hp: int | None = Field(default=None, ge=-99999, le=99999)
    max_hp: int | None = Field(default=None, ge=0, le=99999)
    hp_delta: int | None = Field(default=None, ge=-99999, le=99999)
    in_turn: bool | None = None

class BattleStart(BaseModel):
    order: list[str]

class SetupName(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    campaign: str | None = Field(default=None, max_length=100)

class SetupRename(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    new_name: str = Field(min_length=1, max_length=100)
    campaign: str | None = Field(default=None, max_length=100)

class SetupImport(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    kind: Literal["monsters"]
    campaign: str | None = Field(default=None, max_length=100)

class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default='', max_length=2000)
    activate: bool = True

class CampaignUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)

class CampaignSetupAdd(BaseModel):
    setup: str = Field(min_length=1, max_length=100)
    from_campaign: str = Field(min_length=1, max_length=100)
    mode: Literal['move', 'copy'] = 'move'

class BattleActionRow(BaseModel):
    target_id: str = Field(min_length=1, max_length=100)
    action: Literal["damage", "heal", "buff", "debuff"]
    amount: int | None = Field(default=None, ge=1, le=99999)

class BattleActions(BaseModel):
    actor_id: str = Field(min_length=1, max_length=100)
    actions: list[BattleActionRow] = Field(min_length=1, max_length=100)

def login(error: str='') -> HTMLResponse:
    return HTMLResponse(LOGIN.replace('{error}', f'<p class="error">{error}</p>' if error else ''))

admin = FastAPI(title='Scrying Glass Admin')
client = FastAPI(title='Scrying Glass Client')

@admin.get('/login')
def admin_login_get():
    return login()

@admin.post('/login')
def admin_login_post(username: str=Form(...), password: str=Form(...)):
    u = user(username)
    if not u or u.get('role') != 'admin' or (not password_ok(password, str(u.get('password', '')))):
        return login('Invalid admin credentials')
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = {'username': username, 'role': 'admin'}
    r = RedirectResponse('/', 303)
    r.set_cookie(ADMIN_SESSION_COOKIE, token, httponly=True, samesite='lax', secure=False)
    for legacy in LEGACY_SESSION_COOKIES:
        r.delete_cookie(legacy)
    return r

@admin.get('/')
def admin_home(request: FastAPIRequest):
    return HTMLResponse(ADMIN_HTML) if SESSIONS.get(request.cookies.get(ADMIN_SESSION_COOKIE, ''), {}).get('role') == 'admin' else RedirectResponse('/login', 303)

@client.get("/", include_in_schema=False)
def client_root(request: FastAPIRequest):
    session = SESSIONS.get(request.cookies.get(CLIENT_SESSION_COOKIE, ""))

    if not session:
        return RedirectResponse("/login", status_code=303)

    return RedirectResponse("/display", status_code=303)

@client.get('/login')
def client_login_get():
    return login()

@client.post('/login')
def client_login_post(username: str=Form(...), password: str=Form(...)):
    u = user(username)
    if not u or u.get('role') not in {'admin', 'client'} or (not password_ok(password, str(u.get('password', '')))):
        return login('Invalid credentials')
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = {'username': username, 'role': u['role']}
    r = RedirectResponse('/display', 303)
    r.set_cookie(CLIENT_SESSION_COOKIE, token, httponly=True, samesite='lax', secure=False)
    for legacy in LEGACY_SESSION_COOKIES:
        r.delete_cookie(legacy)
    return r

@client.get('/display')
def client_home(request: FastAPIRequest):
    return HTMLResponse(CLIENT_HTML) if SESSIONS.get(request.cookies.get(CLIENT_SESSION_COOKIE, '')) else RedirectResponse('/login', 303)

@admin.get("/api/state")
def admin_get_state(
    _: dict[str, str] = Depends(
        require("admin", ADMIN_SESSION_COOKIE)
    ),
):
    return public_state()

@admin.patch('/api/display/background')
async def update_display_background(
    payload: DisplayBackgroundUpdate,
    _: dict[str, str] = Depends(require('admin', ADMIN_SESSION_COOKIE)),
) -> dict[str, Any]:
    background = payload.background.strip()

    if not background:
        raise HTTPException(400, 'Background is required')

    STATE['display']['background'] = background
    await changed()
    return public_state()

@admin.post('/api/display/background-image')
async def upload_display_background_image(
    image: UploadFile = File(...),
    _: dict[str, str] = Depends(require('admin', ADMIN_SESSION_COOKIE)),
) -> dict[str, Any]:
    image_url = save_image(image)
    STATE['display']['background'] = f'url("{image_url}")'
    await changed()

    return {
        'background': STATE['display']['background'],
        'image_url': image_url,
    }

@client.get("/api/state")
def client_get_state(
    _: dict[str, str] = Depends(
        require("client", CLIENT_SESSION_COOKIE)
    ),
):
    return public_state()

@client.websocket("/ws")
async def ws(websocket: WebSocket):
    token = websocket.cookies.get(CLIENT_SESSION_COOKIE, "")
    session = SESSIONS.get(token)

    if not session:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    SOCKETS.add(websocket)

    await websocket.send_text(
        json.dumps({"type": "state", "state": public_state()})
    )

    try:
        while True:
            await websocket.receive_text()
    except Exception:
        SOCKETS.discard(websocket)

@admin.get('/api/setups')
async def get_setups(campaign: str | None = None, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    migrate_unassigned_setups()
    slug = require_campaign(campaign)
    return {'campaign': slug, 'names': list_setups(slug)}

@admin.get('/api/campaigns')
async def get_campaigns(_: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    moved = migrate_unassigned_setups()
    return campaigns_payload(moved)

@admin.post('/api/campaigns')
async def create_campaign(payload: CampaignCreate, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    migrate_unassigned_setups()
    slug = campaign_slug(payload.name)
    data = read_campaigns()
    if slug in data['campaigns'] or campaign_dir(slug).exists():
        raise HTTPException(409, f'Campaign already exists: {slug}')
    
    campaign_dir(slug).mkdir(parents=True, exist_ok=False)
    create_default_setup(slug)
    save_campaign_characters(slug, [])

    data["campaigns"][slug] = {
        'name': payload.name.strip(),
        'description': payload.description.strip(),
        'created': now_iso(),
    }
    if payload.activate:
        data['active'] = slug
    write_campaigns(data)
    opened = await open_campaign_setup(slug) if payload.activate else None
    return {**campaigns_payload(), 'opened_setup': opened}

@admin.patch('/api/campaigns/{slug}')
async def update_campaign(slug: str, payload: CampaignUpdate, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    migrate_unassigned_setups()
    slug = require_campaign(slug)
    data = read_campaigns()
    meta = data['campaigns'][slug]
    if payload.description is not None:
        meta['description'] = payload.description.strip()
    if payload.name is not None:
        new_slug = campaign_slug(payload.name)
        if new_slug != slug:
            if new_slug in data['campaigns'] or campaign_dir(new_slug).exists():
                raise HTTPException(409, f'Campaign already exists: {new_slug}')
            campaign_dir(slug).rename(campaign_dir(new_slug))
            old_characters_path = campaign_characters_path(slug)
            new_characters_path = campaign_characters_path(new_slug)
            if old_characters_path.exists():
                old_characters_path.rename(new_characters_path)
            else:
                save_campaign_characters(new_slug, [])
            data["campaigns"][new_slug] = data["campaigns"].pop(slug)
            if data['active'] == slug:
                data['active'] = new_slug
            meta = data['campaigns'][new_slug]
        meta['name'] = payload.name.strip()
    write_campaigns(data)
    return campaigns_payload()

@admin.delete('/api/campaigns/{slug}')
async def delete_campaign(slug: str, move_to: str | None = None, delete_setups: bool = False, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    migrate_unassigned_setups()
    slug = require_campaign(slug)
    data = read_campaigns()
    if len(data['campaigns']) <= 1:
        raise HTTPException(400, 'The last remaining campaign cannot be deleted')
    source = campaign_dir(slug)
    setups = sorted(source.glob('*.json'))
    target_slug = None
    if move_to and delete_setups:
        raise HTTPException(400, 'Choose either move_to or delete_setups, not both')
    if move_to:
        target_slug = require_campaign(move_to)
        if target_slug == slug:
            raise HTTPException(400, 'Cannot move setups into the campaign being deleted')
    if setups and target_slug is None and not delete_setups:
        raise HTTPException(409, f'Campaign still contains {len(setups)} setup(s); choose a campaign to move them to, or delete them')
    deleted_setups = [src.stem for src in setups] if delete_setups else []
    moved = []
    if target_slug is not None:
        for src in setups:
            dst = unique_setup_path(campaign_dir(target_slug), src.stem)
            src.replace(dst)
            moved.append(dst.stem)
    reference = active_setup_reference()

    if reference is not None and reference["campaign"] == slug:
        clear_active_setup()

    shutil.rmtree(source, ignore_errors=True)
    campaign_characters_path(slug).unlink(missing_ok=True)

    del data["campaigns"][slug]
    reactivated = data['active'] == slug
    if reactivated:
        data['active'] = target_slug or sorted(data['campaigns'], key=str.casefold)[0]
    write_campaigns(data)
    opened = await open_campaign_setup(data['active']) if reactivated else None
    return {**campaigns_payload(), 'moved': moved, 'deleted_setups': deleted_setups, 'opened_setup': opened}

@admin.post('/api/campaigns/{slug}/activate')
async def activate_campaign(slug: str, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    migrate_unassigned_setups()
    slug = require_campaign(slug)
    data = read_campaigns()
    data['active'] = slug
    write_campaigns(data)
    opened = await open_campaign_setup(slug)
    return {**campaigns_payload(), 'opened_setup': opened}

@admin.post('/api/campaigns/{slug}/setups')
async def add_setup_to_campaign(slug: str, payload: CampaignSetupAdd, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    migrate_unassigned_setups()
    target_slug = require_campaign(slug)
    source_slug = require_campaign(payload.from_campaign)
    src = setup_path(payload.setup, source_slug)
    if not src.exists():
        raise HTTPException(404, 'Saved setup not found')
    if source_slug == target_slug:
        raise HTTPException(400, 'Setup is already in this campaign')
    dst = unique_setup_path(campaign_dir(target_slug), src.stem)
    if payload.mode == 'copy':
        shutil.copy2(src, dst)
    else:
        src.replace(dst)
    return {**campaigns_payload(), 'setup': dst.stem, 'campaign': target_slug, 'mode': payload.mode}

@admin.post("/api/setups/new")
async def new_setup(
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
):
    global STATE

    campaign = require_campaign(None)

    STATE = normalize_state({
        "monsters": [],
        "characters": load_campaign_characters(campaign),
        "battle_order": [],
        "activity_log": [],
        "display": {
            "background": configured_background(),
        },
    })

    clear_active_setup()

    await changed()

    return public_state()

@admin.post("/api/setups/save")
async def save_setup(
    payload: SetupName,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
):
    name = setup_slug(payload.name)
    campaign = require_campaign(payload.campaign)
    path = setup_path(name, campaign)

    temp = path.with_suffix(".tmp")
    temp.write_text(
        json.dumps(setup_snapshot(STATE), indent=2),
        encoding="utf-8",
    )
    temp.replace(path)

    # Characters are campaign-owned, so save their current state separately.
    save_campaign_characters(campaign, STATE["characters"])

    set_active_setup(campaign, name)
    remember_setup(campaign, name)

    await changed()

    return {
        "name": name,
        "campaign": campaign,
    }

@admin.post('/api/setups/load')
async def load_setup(payload: SetupName, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    global STATE
    name = setup_slug(payload.name)
    campaign = require_campaign(payload.campaign)
    STATE = load_setup_state(name, campaign)
    set_active_setup(campaign, name)
    remember_setup(campaign, name)
    await changed()
    return {'name': name, 'campaign': campaign}

@admin.post("/api/setups/rename")
async def rename_setup(
    payload: SetupRename,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
):
    campaign = require_campaign(payload.campaign)
    old = setup_slug(payload.name)
    new = setup_slug(payload.new_name)

    src = setup_path(old, campaign)

    if not src.exists():
        raise HTTPException(404, "Saved setup not found")

    if new == old:
        return {
            "name": new,
            "old_name": old,
            "campaign": campaign,
        }

    dst = setup_path(new, campaign)

    if dst.exists():
        raise HTTPException(
            409,
            f"A battle setup called {new} already exists in this campaign",
        )

    src.rename(dst)

    data = read_campaigns()
    meta = data["campaigns"].get(campaign)

    if meta is not None and meta.get("last_setup") == old:
        meta["last_setup"] = new

    write_campaigns(data)

    reference = active_setup_reference()

    if (
        reference is not None
        and reference["campaign"] == campaign
        and reference["name"] == old
    ):
        set_active_setup(campaign, new)
        await changed()

    return {
        "name": new,
        "old_name": old,
        "campaign": campaign,
    }

@admin.delete('/api/setups/{name}')
async def delete_setup(name: str, campaign: str | None = None, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    """Delete a battle setup, then open the next one in the campaign.

    "Next" is the setup that follows the deleted one alphabetically (wrapping
    around to the first). When the campaign has no setups left, an empty
    "Default" setup is created and opened.
    """
    global STATE
    campaign = require_campaign(campaign)
    name = setup_slug(name)
    path = setup_path(name, campaign)
    if not path.exists():
        raise HTTPException(404, 'Saved setup not found')
    reference = active_setup_reference()

    if (
        reference is not None
        and reference["campaign"] == campaign
        and reference["name"] == name
    ):
        clear_active_setup()

    path.unlink()
    remaining = list_setups(campaign)
    created_default = False
    if remaining:
        following = [x for x in remaining if x.casefold() > name.casefold()]
        next_name = following[0] if following else remaining[0]
    else:
        create_default_setup(campaign)
        next_name = DEFAULT_SETUP_NAME
        created_default = True
    try:
        STATE = load_setup_state(next_name, campaign)
    except HTTPException as exc:
        raise HTTPException(
            exc.status_code,
            f"Setup {name} was deleted, but {next_name} could not be opened: "
            f"{exc.detail}",
        ) from exc
    set_active_setup(campaign, name)
    remember_setup(campaign, next_name)
    await changed()
    return {'deleted': name, 'opened_setup': next_name, 'created_default': created_default, 'campaign': campaign}

@admin.post("/api/setups/import")
async def import_setup(
    payload: SetupImport,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
):
    name = setup_slug(payload.name)
    campaign = require_campaign(payload.campaign)

    if payload.kind != "monsters":
        raise HTTPException(
            400,
            "Characters belong to campaigns and cannot be imported "
            "from a battle setup",
        )

    source = load_setup_state(name, campaign)

    imported_monsters = [
        reset_imported_monster(item)
        for item in source["monsters"]
    ]

    STATE["monsters"].extend(imported_monsters)

    await combatants_changed(monsters=True, characters=False)

    return {
        "name": name,
        "campaign": campaign,
        "monsters": len(imported_monsters),
    }

@admin.post('/api/monsters/roll-initiative')
async def roll_monster_initiative(_: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    for monster in STATE['monsters']:
        monster['initiative'] = random.randint(1, 20)
    await combatants_changed(monsters=True, characters=False)
    return {'count': len(STATE['monsters'])}

@admin.post('/api/monsters')
async def create_monster(
    name: str = Form(...),
    monster_species: str = Form(...),
    ac: int = Form(...),
    hprangestart: str = Form(...),
    hprangeend: str = Form(""),
    color: str = Form(...),
    quantity: int = Form(1, ge=1, le=50),
    image: UploadFile | None = File(None),
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> list[dict[str, Any]]:

    next_hp = hp_value_factory(hprangestart, hprangeend)

    fields = {
        "name": name.strip(),
        "monster_species": monster_species.strip(),
        "ac": ac,
    }
    image_url = (
        save_image(image)
        if image is not None and image.filename
        else dnd_image(fields["monster_species"])
    )

    created = []

    for number in range(1, quantity + 1):
        generated_name = (
            fields["name"]
            if quantity == 1
            else f"{fields['name']} - {number}"
        )
        rolled_hp = next_hp()

        created.append(
            make_monster(
                {
                    **fields,
                    "name": generated_name,
                    "hp": rolled_hp,
                },
                color,
                None,
                image_url,
            )
        )

    STATE["monsters"].extend(created)
    await combatants_changed(monsters=True, characters=False)
    return created


@admin.post('/api/monsters/import')
async def import_monster(monster_file: UploadFile=File(...), color: str=Form(...), quantity: int=Form(1, ge=1, le=50), image: UploadFile | None=File(None), _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    if not (monster_file.filename or '').lower().endswith('.monster'):
        raise HTTPException(400, 'Upload a .monster file')
    fields = parse_monster(await monster_file.read())
    image_url = (
        save_image(image)
        if image and image.filename
        else dnd_image(fields['monster_species'])
    )

    created = make_monsters(fields, color, quantity, image_url)

    STATE['monsters'].extend(created)
    await combatants_changed(monsters=True, characters=False)
    return created

@admin.post("/api/monsters/import-csv")
async def import_monsters_csv(
    csv_file: UploadFile = File(...),
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, int]:
    if not (csv_file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Upload a .csv file")

    rows = csv_rows(await csv_file.read())
    imported = [
        csv_monster(row, row_number)
        for row_number, row in enumerate(rows, start=2)
    ]

    ids = [monster["id"] for monster in imported]
    existing_ids = {monster["id"] for monster in STATE["monsters"]}
    existing_ids.update(character["id"] for character in STATE["characters"])

    if len(ids) != len(set(ids)):
        raise HTTPException(400, "CSV contains duplicate IDs")

    conflicting = set(ids) & existing_ids
    if conflicting:
        raise HTTPException(
            400,
            "CSV ID already exists in the current setup: "
            + ", ".join(sorted(conflicting)[:5]),
        )

    STATE["monsters"].extend(imported)
    await combatants_changed(monsters=True, characters=False)

    return {"count": len(imported)}

@admin.post("/api/characters/import-csv")
async def import_characters_csv(
    csv_file: UploadFile = File(...),
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, int]:
    if not (csv_file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Upload a .csv file")

    rows = csv_rows(await csv_file.read())
    imported = [
        csv_character(row, row_number)
        for row_number, row in enumerate(rows, start=2)
    ]

    ids = [character["id"] for character in imported]
    existing_ids = {monster["id"] for monster in STATE["monsters"]}
    existing_ids.update(character["id"] for character in STATE["characters"])

    if len(ids) != len(set(ids)):
        raise HTTPException(400, "CSV contains duplicate IDs")

    conflicting = set(ids) & existing_ids
    if conflicting:
        raise HTTPException(
            400,
            "CSV ID already exists in the active campaign encounter: "
            + ", ".join(sorted(conflicting)[:5]),
        )

    STATE["characters"].extend(imported)
    save_active_campaign_characters()
    await combatants_changed(monsters=False, characters=True)

    return {"count": len(imported)}
    
@admin.post('/api/monsters/{ident}/edit')
async def edit_monster(ident: str, name: str=Form(...), monster_species: str=Form(...), ac: int=Form(...), hp: int=Form(...), max_hp: int=Form(...), original_hp: int=Form(...), color: str=Form(...), initiative: str=Form(''), ally: str=Form('false'), image: UploadFile | None=File(None), _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    m = next((x for x in STATE['monsters'] if x['id'] == ident), None)
    if not m:
        raise HTTPException(404, 'Monster not found')
    parsed_initiative = None if initiative.strip() == '' else int(initiative)
    if parsed_initiative is not None and (not -100 <= parsed_initiative <= 100):
        raise HTTPException(400, 'Initiative must be between -100 and 100')
    m.update({'name': name.strip(), 'monster_species': monster_species.strip(), 'ac': ac, 'hp': hp, 'max_hp': max_hp, 'original_hp': original_hp, 'color': color, 'initiative': parsed_initiative, 'ally': ally.lower() == 'true'})
    if image and image.filename:
        m['image_url'] = save_image(image)
    if m['hp'] <= 0:
        m['alive'] = False
        m['visible'] = True
        m['in_turn'] = False
    clean_order()
    await combatants_changed(monsters=True, characters=False)
    return m

@admin.patch("/api/monsters/{ident}")
async def update_monster(
    ident: str,
    update: MonsterUpdate,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, Any]:
    monster = next(
        (item for item in STATE["monsters"] if item["id"] == ident),
        None,
    )

    if not monster:
        raise HTTPException(404, "Monster not found")

    values = update.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    hp_delta = values.pop("hp_delta", None)

    for key, value in values.items():
        if key != "in_turn":
            monster[key] = value

    if hp_delta is not None:
        monster["hp"] += hp_delta

    if monster["hp"] <= 0:
        monster["alive"] = False
        monster["visible"] = True
        monster["in_turn"] = False
    else:
        monster["alive"] = True

    if hp_delta is not None:
        log_hp_change(monster, hp_delta)

    if values.get("active") is True:
        insert_into_battle_order(monster)

    if values.get("active") is False:
        monster["in_turn"] = False

    set_turn(monster, values.get("in_turn"))
    clean_order()

    await combatants_changed(monsters=True, characters=False)
    return monster

@admin.post("/api/monsters/bulk")
async def bulk_monsters(
    body: BulkCombatantAction,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, int]:
    fields = {
        "join-battle": ("active", True),
        "leave-battle": ("active", False),
        "set-ally": ("ally", True),
        "unset-ally": ("ally", False),
        "show-ac": ("show_ac", True),
        "hide-ac": ("show_ac", False),
        "show-hp": ("show_hp", True),
        "hide-hp": ("show_hp", False),
        "show-initiative": ("show_initiative", True),
        "hide-initiative": ("show_initiative", False),
    }
    allowed = {*fields, "reset", "remove"}

    if body.action not in allowed:
        raise HTTPException(400, "Unsupported bulk monster action")

    targets = selected_entities("monsters", body.ids)

    if body.action in fields:
        field, value = fields[body.action]

        if body.action == "join-battle":
            for monster in targets:
                # Prefer the existing activation helper where available.
                monster[field] = value
        elif body.action == "leave-battle":
            removed_ids = {monster["id"] for monster in targets}
            for monster in targets:
                monster[field] = value
                monster["in_turn"] = False
            STATE["battle_order"] = [
                ident for ident in STATE["battle_order"]
                if ident not in removed_ids
            ]
        else:
            for monster in targets:
                monster[field] = value

    elif body.action == "reset":
        reset_ids = {monster["id"] for monster in targets}
        for monster in targets:
            reset_one_combatant(monster)
        STATE["battle_order"] = [
            ident for ident in STATE["battle_order"]
            if ident not in reset_ids
        ]

    else:  # remove
        removed_ids = {monster["id"] for monster in targets}
        STATE["monsters"] = [
            monster for monster in STATE["monsters"]
            if monster["id"] not in removed_ids
        ]
        STATE["battle_order"] = [
            ident for ident in STATE["battle_order"]
            if ident not in removed_ids
        ]

    await combatants_changed(monsters=True, characters=False)
    return {"count": len(targets)}

@admin.post('/api/characters')
async def create_character(character: CharacterCreate, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    c = {'id': uuid.uuid4().hex, **character.model_dump(), 'max_hp': character.hp, 'original_hp': character.hp, 'original_initiative': character.initiative, 'active': False, 'alive': character.hp >= 0, 'visible': False, 'in_turn': False}
    STATE["characters"].append(c)
    save_active_campaign_characters()
    await combatants_changed(monsters=False, characters=True)

    return c

@admin.patch("/api/characters/{ident}")
async def update_character(
    ident: str,
    update: CharacterUpdate,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, Any]:
    character = next(
        (item for item in STATE["characters"] if item["id"] == ident),
        None,
    )

    if not character:
        raise HTTPException(404, "Character not found")

    values = update.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    hp_delta = values.pop("hp_delta", None)

    for key, value in values.items():
        if key != "in_turn":
            character[key] = value

    if hp_delta is not None:
        character["hp"] += hp_delta

    if "max_hp" in values:
        character["original_hp"] = values["max_hp"]

    if character["hp"] <= 0:
        character["alive"] = False
        character["visible"] = True
        character["in_turn"] = False
    else:
        character["alive"] = True

    if hp_delta is not None:
        log_hp_change(character, hp_delta)

    if values.get("active") is True:
        insert_into_battle_order(character)

    if values.get("alive") is False:
        character["visible"] = True
        character["in_turn"] = False

    if values.get("active") is False:
        character["in_turn"] = False

    set_turn(character, values.get("in_turn"))
    clean_order()
    save_active_campaign_characters()
    await combatants_changed(monsters=False, characters=True)

    return character

@admin.delete("/api/combatants/{ident}")
async def delete_combatant(
    ident: str,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, str]:
    monster_index = next(
        (
            index
            for index, monster in enumerate(STATE["monsters"])
            if monster["id"] == ident
        ),
        None,
    )

    removed_character = False
    is_monster = monster_index is None
    is_character = not is_monster

    if monster_index is not None:
        removed = STATE["monsters"].pop(monster_index)
    else:
        character_index = next(
            (
                index
                for index, character in enumerate(STATE["characters"])
                if character["id"] == ident
            ),
            None,
        )

        is_character = character_index is not None
        if character_index is None:
            raise HTTPException(404, "Combatant not found")

        removed = STATE["characters"].pop(character_index)
        removed_character = True

    STATE["battle_order"] = [
        combatant_id
        for combatant_id in STATE["battle_order"]
        if combatant_id != ident
    ]

    if removed_character:
        save_active_campaign_characters()

    await combatants_changed(monsters=is_monster, characters=is_character)

    return {
        "id": ident,
        "name": str(removed.get("name", "Combatant")),
    }

@admin.post("/api/combatants/{ident}/reset")
async def reset_one_combatant(
    ident: str,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
):
    x = entity(ident)

    if not x:
        raise HTTPException(404, "Combatant not found")

    is_character = x in STATE["characters"]

    reset_entity(x)
    clean_order()

    if is_character:
        save_active_campaign_characters()

    await combatants_changed(monsters=not is_character, characters=is_character)


    return x
    
@admin.post("/api/characters/bulk")
async def bulk_characters(
    body: BulkCombatantAction,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, int]:
    allowed = {"join-battle", "leave-battle", "reset", "remove"}

    if body.action not in allowed:
        raise HTTPException(400, "Unsupported bulk character action")

    targets = selected_entities("characters", body.ids)

    if body.action == "join-battle":
        for character in targets:
            character["active"] = True

    elif body.action == "leave-battle":
        for character in targets:
            character["active"] = False
            character["in_turn"] = False
        STATE["battle_order"] = [
            ident for ident in STATE["battle_order"]
            if ident not in {character["id"] for character in targets}
        ]

    elif body.action == "reset":
        for character in targets:
            reset_entity(character)

        clean_order()

    else:  # remove
        removed_ids = {character["id"] for character in targets}
        STATE["characters"] = [
            character for character in STATE["characters"]
            if character["id"] not in removed_ids
        ]
        STATE["battle_order"] = [
            ident for ident in STATE["battle_order"]
            if ident not in removed_ids
        ]

    # Character records are owned by the active campaign.
    save_active_campaign_characters()
    await combatants_changed(monsters=False, characters=True)
    return {"count": len(targets)}

@admin.post("/api/monsters/bulk")
async def bulk_monsters(
    body: BulkCombatantAction,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, int]:
    fields = {
        "join-battle": ("active", True),
        "leave-battle": ("active", False),
        "set-ally": ("ally", True),
        "unset-ally": ("ally", False),
        "show-ac": ("show_ac", True),
        "hide-ac": ("show_ac", False),
        "show-hp": ("show_hp", True),
        "hide-hp": ("show_hp", False),
        "show-initiative": ("show_initiative", True),
        "hide-initiative": ("show_initiative", False),
    }
    allowed = {*fields, "reset", "remove"}

    if body.action not in allowed:
        raise HTTPException(400, "Unsupported bulk monster action")

    targets = selected_entities("monsters", body.ids)

    if body.action in fields:
        field, value = fields[body.action]

        if body.action == "join-battle":
            for monster in targets:
                # Prefer the existing activation helper where available.
                monster[field] = value
        elif body.action == "leave-battle":
            removed_ids = {monster["id"] for monster in targets}
            for monster in targets:
                monster[field] = value
                monster["in_turn"] = False
            STATE["battle_order"] = [
                ident for ident in STATE["battle_order"]
                if ident not in removed_ids
            ]
        else:
            for monster in targets:
                monster[field] = value

    elif body.action == "reset":
        for monster in targets:
            reset_entity(monster)

        clean_order()

    else:  # remove
        removed_ids = {monster["id"] for monster in targets}
        STATE["monsters"] = [
            monster for monster in STATE["monsters"]
            if monster["id"] not in removed_ids
        ]
        STATE["battle_order"] = [
            ident for ident in STATE["battle_order"]
            if ident not in removed_ids
        ]

    await combatants_changed(monsters=True, characters=False)
    return {"count": len(targets)}

@admin.post("/api/battle/end")
async def battle_end(
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, str]:
    clear_turns()
    STATE["battle_order"] = []

    save_active_campaign_characters()
    await combatants_changed(monsters=True, characters=True)

    return {"status": "ended"}

@admin.post("/api/battle/reset-all")
async def reset_all(
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
):
    for combatant in entities():
        reset_entity(combatant)

    sort_admin_by_max_hp()
    STATE["battle_order"] = []

    save_active_campaign_characters()
    await combatants_changed(monsters=True, characters=True)

    return {"status": "reset"}

@admin.post("/api/battle/start")
async def battle_start(
    payload: BattleStart,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
):
    begin_battle(payload.order)
    sort_admin_by_initiative()

    save_active_campaign_characters()
    await combatants_changed(monsters=True, characters=True)

    return public_state()

@admin.post("/api/battle/next")
async def battle_next(
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
):
    current = advance_turn()

    save_active_campaign_characters()
    await combatants_changed(monsters=True, characters=True)

    return {"current": current}

@admin.post("/api/battle/actions")
async def apply_battle_actions(
    payload: BattleActions,
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, Any]:
    actor = entity(payload.actor_id)

    if actor is None:
        raise HTTPException(404, "Active combatant was not found")

    if not actor.get("active") or not actor.get("alive", True):
        raise HTTPException(400, "The acting combatant must be active and alive")

    if not actor.get("in_turn"):
        raise HTTPException(
            400,
            "Only the current active combatant may apply battle actions",
        )

    valid_actions = {"damage", "heal", "buff", "debuff"}
    prepared: list[tuple[dict[str, Any], str, int | None]] = []

    # Validate all rows before changing state, so a malformed row cannot leave
    # prior rows partially applied.
    for row in payload.actions:
        if row.action not in valid_actions:
            raise HTTPException(400, "Unsupported battle action")

        target = entity(row.target_id)

        if target is None:
            raise HTTPException(404, "Target combatant was not found")

        if not target.get("active") or not target.get("alive", True):
            raise HTTPException(
                400,
                f"Target {target['name']} must be active and alive",
            )

        if row.action in {"damage", "heal"}:
            if row.amount is None or row.amount <= 0:
                raise HTTPException(
                    400,
                    f"{row.action.title()} requires an amount greater than zero",
                )
            amount: int | None = row.amount
        else:
            if row.amount is not None:
                raise HTTPException(
                    400,
                    f"{row.action.title()} must not include an amount",
                )
            amount = None

        prepared.append((target, row.action, amount))

    # Apply only after every row passed validation.
    for target, action, amount in prepared:
        if action == "damage":
            target["hp"] -= amount
            update_alive_state(target)
        elif action == "heal":
            target["hp"] += amount
            update_alive_state(target)

        log_battle_action(actor, target, action, amount)

    clean_order()
    save_active_campaign_characters()
    await combatants_changed(monsters=True, characters=True)

    return {
        "applied": len(prepared),
        "activity_log": STATE["activity_log"],
    }

@admin.get("/api/activity-log.json")
async def export_activity_log_json(
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> Response:
    content = json.dumps(
        STATE["activity_log"],
        indent=2,
        ensure_ascii=False,
    )

    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition":
                'attachment; filename="activity-log.json"',
        },
    )

@admin.get("/api/activity-log.csv")
async def export_activity_log_csv(
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> Response:
    fieldnames = [
        "id",
        "timestamp",
        "active_combatant_id",
        "active_combatant",
        "active_combatant_state",
        "target_combatant_id",
        "target_combatant",
        "target_combatant_state",
        "action",
        "amount",
    ]

    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
    )

    writer.writeheader()

    for entry in STATE["activity_log"]:
        writer.writerow(entry)

    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition":
                'attachment; filename="activity-log.csv"',
        },
    )

@admin.post("/api/activity-log/clear")
async def clear_activity_log(
    _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE)),
) -> dict[str, int]:
    cleared = len(STATE["activity_log"])
    STATE["activity_log"] = []

    await changed()

    return {"cleared": cleared}

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
        common = {'host': CONFIG['network']['bind'], 'log_level': 'info', 'access_log': False}
        await asyncio.gather(uvicorn.Server(uvicorn.Config(admin, port=CONFIG['network']['admin_port'], **common)).serve(), uvicorn.Server(uvicorn.Config(client, port=CONFIG['network']['client_port'], **common)).serve())
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
