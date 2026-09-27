"""Monster Display v4.14 (Python 3.14+).

Dependencies:
  python3.14 -m pip install 'fastapi>=0.115' 'uvicorn[standard]>=0.30' 'PyYAML>=6.0' python-multipart

Run:
  python3.14 monster_display_server.py --config config.yaml
"""
from __future__ import annotations
import argparse, asyncio, copy, csv, hashlib, hmac, io, json, random, re, secrets, shutil, sys, uuid, uvicorn, yaml
from pathlib import Path
from typing import Any, Literal
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

DEFAULT_CONFIG = {'network': {'bind': '0.0.0.0', 'admin_port': 3000, 'client_port': 4000}, 'storage_dir': './monster-display-data', 'security': {'users': [{'username': 'admin', 'role': 'admin', 'password': 'CHANGE-ME'}, {'username': 'client', 'role': 'client', 'password': 'CHANGE-ME'}]}, 'display': {'background': '#080b14', 'entry_direction': 'from_bottom', 'exit_direction': 'to_bottom', 'monster_width_percent': 45, 'dndbeyond_image_lookup': True}}
CONFIG: dict[str, Any] = {}
STATE: dict[str, Any] = {'monsters': [], 'characters': [], 'battle_order': [], "activity_log": []}
LOCK = asyncio.Lock()
SESSIONS: dict[str, dict[str, str]] = {}
SOCKETS: set[WebSocket] = set()
DATA_DIR: Path
STATE_FILE: Path
UPLOAD_DIR: Path
SETUPS_DIR: Path

ADMIN_SESSION_COOKIE = "monster_admin_session"
CLIENT_SESSION_COOKIE = "monster_client_session"

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

def normalize_state(raw: dict[str, Any]) -> dict[str, Any]:
    state = {
        "monsters": raw.get("monsters", []),
        "characters": raw.get("characters", []),
        "battle_order": raw.get("battle_order", []),
        "activity_log": raw.get("activity_log", []),
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
        m.setdefault('monster_type', 'unknown')
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

def load_state() -> None:
    global STATE
    STATE = normalize_state(json.loads(STATE_FILE.read_text(encoding='utf-8'))) if STATE_FILE.exists() else normalize_state(STATE)

def save_state() -> None:
    temp = STATE_FILE.with_suffix('.tmp')
    temp.write_text(json.dumps(STATE, indent=2), encoding='utf-8')
    temp.replace(STATE_FILE)

def public_state() -> dict[str, Any]:
    d = CONFIG['display']
    return {
        "monsters": STATE["monsters"],
        "characters": STATE["characters"],
        "battle_order": STATE["battle_order"],
        "activity_log": STATE["activity_log"],
        "display": {
            "background": d["background"],
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

def setup_path(name: str) -> Path:
    return SETUPS_DIR / (setup_slug(name) + '.json')

def list_setups() -> list[str]:
    return sorted((p.stem for p in SETUPS_DIR.glob('*.json')), key=str.casefold)

def reset_imported_monster(source: dict[str, Any]) -> dict[str, Any]:
    item = copy.deepcopy(source)
    item['id'] = uuid.uuid4().hex
    item['hp'] = item['original_hp']
    item['max_hp'] = item['original_hp']
    item['initiative'] = item.get('original_initiative')
    item['active'] = False
    item['alive'] = True
    item['visible'] = False
    item['in_turn'] = False
    item['show_ac'] = False
    item['show_hp'] = False
    item['show_initiative'] = False
    return item

def reset_imported_character(source: dict[str, Any]) -> dict[str, Any]:
    item = copy.deepcopy(source)
    item['id'] = uuid.uuid4().hex
    item['hp'] = item['max_hp']
    item['initiative'] = item.get('original_initiative')
    item['active'] = False
    item['alive'] = True
    item['visible'] = False
    item['in_turn'] = False
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
    return {'name': name, 'monster_type': kind, 'ac': int(ac.group()), 'hp': int(hp.group())}

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
    monster_type = csv_text(row.get("monster_type") or row.get("type"))
    ac = csv_int(row, "ac", minimum=0, maximum=999, row_number=row_number)
    hp = csv_int(row, "hp", minimum=-99999, maximum=99999, row_number=row_number)

    if not name:
        raise HTTPException(400, f"CSV row {row_number}: name is required")

    if not monster_type:
        raise HTTPException(
            400,
            f"CSV row {row_number}: monster_type (or type) is required",
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
        "monster_type": monster_type,
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

def dnd_image(kind: str) -> str | None:
    if not CONFIG['display'].get('dndbeyond_image_lookup', True):
        return None
    try:
        q = Request('https://www.dndbeyond.com/monsters?filter-search=' + quote(kind), headers={'User-Agent': 'MonsterDisplay/1.0'})
        with urlopen(q, timeout=5) as r:
            html = r.read(1000000).decode('utf-8', 'replace')
        found = re.search('<meta[^>]+property=["\\\']og:image["\\\'][^>]+content=["\\\']([^"\\\']+)', html, re.I)
        return found.group(1) if found else None
    except Exception:
        return None

def make_monster(fields: dict[str, Any], color: str, upload: UploadFile | None, image_url: str | None=None) -> dict[str, Any]:
    hp = fields['hp']
    return {'id': uuid.uuid4().hex, **fields, 'max_hp': hp, 'original_hp': hp, 'color': color, 'image_url': image_url if image_url is not None else save_image(upload) if upload and upload.filename else dnd_image(fields['monster_type']), 'active': False, 'alive': True, 'visible': False, 'ally': False, 'initiative': None, 'original_initiative': None, 'show_ac': False, 'show_hp': False, 'show_initiative': False, 'in_turn': False}

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
    if 'monster_type' in x:
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

class MonsterUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    monster_type: str | None = Field(default=None, min_length=1, max_length=100)
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

class SetupImport(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    kind: Literal['characters', 'monsters', 'both']
admin = FastAPI(title='Monster Display Admin')
client = FastAPI(title='Monster Display Client')

class BattleActionRow(BaseModel):
    target_id: str = Field(min_length=1, max_length=100)
    action: Literal["damage", "heal", "buff", "debuff"]
    amount: int | None = Field(default=None, ge=1, le=99999)

class BattleActions(BaseModel):
    actor_id: str = Field(min_length=1, max_length=100)
    actions: list[BattleActionRow] = Field(min_length=1, max_length=100)

def login(error: str='') -> HTMLResponse:
    return HTMLResponse(LOGIN.replace('{error}', f'<p class="error">{error}</p>' if error else ''))

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
    r.delete_cookie("monster_session")
    return r

@admin.get('/')
def admin_home(request: FastAPIRequest):
    return HTMLResponse(ADMIN_HTML) if SESSIONS.get(request.cookies.get(ADMIN_SESSION_COOKIE, ''), {}).get('role') == 'admin' else RedirectResponse('/login', 303)

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
    r.delete_cookie("monster_session")
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
def get_setups(_: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    return {'names': list_setups()}

@admin.post('/api/setups/new')
async def new_setup(_: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    global STATE
    STATE = normalize_state({'monsters': [], 'characters': [], 'battle_order': [], 'activity_log': []})
    await changed()
    return public_state()

@admin.post('/api/setups/save')
async def save_setup(payload: SetupName, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    name = setup_slug(payload.name)
    path = setup_path(name)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(STATE, indent=2), encoding='utf-8')
    temp.replace(path)
    return {'name': name}

@admin.post('/api/setups/load')
async def load_setup(payload: SetupName, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    global STATE
    name = setup_slug(payload.name)
    path = setup_path(name)
    if not path.exists():
        raise HTTPException(404, 'Saved setup not found')
    try:
        STATE = normalize_state(json.loads(path.read_text(encoding='utf-8')))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(400, f'Unable to load setup: {exc}') from exc
    await changed()
    return {'name': name}

@admin.post('/api/setups/import')
async def import_setup(payload: SetupImport, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    name = setup_slug(payload.name)
    path = setup_path(name)
    if not path.exists():
        raise HTTPException(404, 'Saved setup not found')
    try:
        source = normalize_state(json.loads(path.read_text(encoding='utf-8')))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(400, f'Unable to read setup: {exc}') from exc
    imported_characters = []
    imported_monsters = []
    if payload.kind in {'characters', 'both'}:
        imported_characters = [reset_imported_character(item) for item in source['characters']]
    if payload.kind in {'monsters', 'both'}:
        imported_monsters = [reset_imported_monster(item) for item in source['monsters']]
    STATE['characters'].extend(imported_characters)
    STATE['monsters'].extend(imported_monsters)
    await changed()
    return {'name': name, 'characters': len(imported_characters), 'monsters': len(imported_monsters)}

@admin.post('/api/monsters/roll-initiative')
async def roll_monster_initiative(_: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    for monster in STATE['monsters']:
        monster['initiative'] = random.randint(1, 20)
    await changed()
    return {'count': len(STATE['monsters'])}

@admin.post('/api/monsters')
async def create_monster(name: str=Form(...), monster_type: str=Form(...), ac: int=Form(...), hp: int=Form(...), color: str=Form(...), quantity: int=Form(1, ge=1, le=50), image: UploadFile | None=File(None), _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    fields = {'name': name.strip(), 'monster_type': monster_type.strip(), 'ac': ac, 'hp': hp}
    image_url = save_image(image) if image and image.filename else dnd_image(fields['monster_type'])
    created = [make_monster(fields, color, None, image_url) for _ in range(quantity)]
    STATE['monsters'].extend(created)
    await changed()
    return created

@admin.post('/api/monsters/import')
async def import_monster(monster_file: UploadFile=File(...), color: str=Form(...), quantity: int=Form(1, ge=1, le=50), image: UploadFile | None=File(None), _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    if not (monster_file.filename or '').lower().endswith('.monster'):
        raise HTTPException(400, 'Upload a .monster file')
    fields = parse_monster(await monster_file.read())
    image_url = save_image(image) if image and image.filename else dnd_image(fields['monster_type'])
    created = [make_monster(fields, color, None, image_url) for _ in range(quantity)]
    STATE['monsters'].extend(created)
    await changed()
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
    await changed()

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
            "CSV ID already exists in the current setup: "
            + ", ".join(sorted(conflicting)[:5]),
        )

    STATE["characters"].extend(imported)
    await changed()

    return {"count": len(imported)}
    
@admin.post('/api/monsters/{ident}/edit')
async def edit_monster(ident: str, name: str=Form(...), monster_type: str=Form(...), ac: int=Form(...), hp: int=Form(...), max_hp: int=Form(...), original_hp: int=Form(...), color: str=Form(...), initiative: str=Form(''), ally: str=Form('false'), image: UploadFile | None=File(None), _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    m = next((x for x in STATE['monsters'] if x['id'] == ident), None)
    if not m:
        raise HTTPException(404, 'Monster not found')
    parsed_initiative = None if initiative.strip() == '' else int(initiative)
    if parsed_initiative is not None and (not -100 <= parsed_initiative <= 100):
        raise HTTPException(400, 'Initiative must be between -100 and 100')
    m.update({'name': name.strip(), 'monster_type': monster_type.strip(), 'ac': ac, 'hp': hp, 'max_hp': max_hp, 'original_hp': original_hp, 'color': color, 'initiative': parsed_initiative, 'ally': ally.lower() == 'true'})
    if image and image.filename:
        m['image_url'] = save_image(image)
    if m['hp'] <= 0:
        m['alive'] = False
        m['visible'] = True
        m['in_turn'] = False
    clean_order()
    await changed()
    return m

@admin.post("/api/monsters/bulk-toggle")
async def bulk_toggle_monsters(update: MonsterBulkUpdate, _: dict[str, str] = Depends(require("admin", ADMIN_SESSION_COOKIE))) -> dict[str, Any]:
    field = update.field
    monsters = STATE["monsters"]

    # Vacuously treating an empty group as disabled is harmless and provides a
    # stable response to the UI when no monsters exist.
    enable = not bool(monsters) or not all(bool(monster.get(field, False)) for monster in monsters)

    if field == "active":
        for monster in monsters:
            # Dead monsters cannot be activated. They are always off after a
            # bulk activation, which matches the existing single-monster rule.
            desired = enable and bool(monster.get("alive", True))
            was_active = bool(monster.get("active", False))
            monster["active"] = desired

            if desired and not was_active:
                insert_into_battle_order(monster)

            if not desired:
                monster["in_turn"] = False

        # If bulk deactivation removed the current turn, clear it. The existing
        # Next action will select the next eligible combatant as usual.
        current_turn = next((x for x in entities() if x.get("in_turn")), None)
        if current_turn is not None and not current_turn.get("active"):
            clear_turns()
    else:
        for monster in monsters:
            monster[field] = enable

    await changed()
    return {"field": field, "enabled": enable, "count": len(monsters)}

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

    await changed()
    return monster

@admin.post('/api/characters')
async def create_character(character: CharacterCreate, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    c = {'id': uuid.uuid4().hex, **character.model_dump(), 'max_hp': character.hp, 'original_hp': character.hp, 'original_initiative': character.initiative, 'active': False, 'alive': character.hp >= 0, 'visible': False, 'in_turn': False}
    STATE['characters'].append(c)
    await changed()
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

    await changed()
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

        if character_index is None:
            raise HTTPException(404, "Combatant not found")

        removed = STATE["characters"].pop(character_index)

    # The entity has already been removed from the lists, so ensure its ID no
    # longer appears in the persisted turn order. This also covers deleting a
    # current-turn combatant.
    STATE["battle_order"] = [
        combatant_id
        for combatant_id in STATE["battle_order"]
        if combatant_id != ident
    ]

    # Other combatants retain their state. If the deleted combatant had the
    # current turn, no combatant has in_turn=True; the existing Next action
    # will select an eligible combatant normally.
    await changed()

    return {
        "id": ident,
        "name": str(removed.get("name", "Combatant")),
    }

@admin.post('/api/combatants/{ident}/reset')
async def reset_one(ident: str, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    x = entity(ident)
    if not x:
        raise HTTPException(404, 'Combatant not found')
    reset_entity(x)
    clean_order()
    await changed()
    return x

@admin.post('/api/battle/reset-all')
async def reset_all(_: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    for x in entities():
        reset_entity(x)
    sort_admin_by_max_hp()
    STATE['battle_order'] = []
    await changed()
    return {'status': 'reset'}

@admin.post('/api/battle/start')
async def battle_start(payload: BattleStart, _: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    begin_battle(payload.order)
    sort_admin_by_initiative()
    await changed()
    return public_state()

@admin.post('/api/battle/next')
async def battle_next(_: dict[str, str]=Depends(require("admin", ADMIN_SESSION_COOKIE))):
    x = advance_turn()
    await changed()
    return {'current': x}

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
    await changed()

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
    UPLOAD_DIR = DATA_DIR / 'uploads'
    SETUPS_DIR = DATA_DIR / 'setups'
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    SETUPS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE = DATA_DIR / 'state.json'
    load_state()
    admin.mount('/media', StaticFiles(directory=str(UPLOAD_DIR)), name='admin-media')
    client.mount('/media', StaticFiles(directory=str(UPLOAD_DIR)), name='client-media')

    async def serve():
        common = {'host': CONFIG['network']['bind'], 'log_level': 'info', 'access_log': False}
        await asyncio.gather(uvicorn.Server(uvicorn.Config(admin, port=CONFIG['network']['admin_port'], **common)).serve(), uvicorn.Server(uvicorn.Config(client, port=CONFIG['network']['client_port'], **common)).serve())
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
