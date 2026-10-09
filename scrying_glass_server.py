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
from web_html.admin_html import ADMIN_HTML
from web_html.client_html import CLIENT_HTML
from web_html.login_html import LOGIN
from typing import get_type_hints
from datetime import datetime, timezone

from python.scrying_glass_api_admin import AdminAPI
from python.scrying_glass_api_client import ClientAPI

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

from python.scrying_glass_init import (
    DEFAULT_CONFIG,
    DEFAULT_STORAGE_DIR,
    load_config,
    login,
    merge,
    password_hash,
    password_ok,
)

from python.scrying_glass_hp import hp_value_factory

from python.scrying_glass_combatant import (
    admin_initiative_key,
    admin_max_hp_key,
    combatant_state,
    numeric_initiative,
    reset_entity,
    reset_imported_monster,
    setup_snapshot,
    update_alive_state,
)

from python.scrying_glass_tools import (
    campaign_slug,
    now_iso,
    setup_slug,
    unique_ids,
)

from python.scrying_glass_monster_csv import (
    csv_character,
    csv_monster,
    csv_rows,
    parse_monster,
)

from python.scrying_glass_dndbeyond import (
    dnd_monster_candidates,
    dnd_monster_detail_html,
    dnd_monster_stats_from_html,
)

from python.scrying_glass_classes import (
    BattleOrderFontAdjust,
    BattleActions,
    BattleStart,
    BulkCombatantAction,
    CampaignCreate,
    CampaignSetupAdd,
    CampaignUpdate,
    CharacterCreate,
    CharacterUpdate,
    DisplayBackgroundUpdate,
    MonsterUpdate,
    SetupImport,
    SetupName,
    SetupRename,
)

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
from python.scrying_glass_storage import SQLiteStorage

STORAGE: SQLiteStorage
DATA_DIR: Path
UPLOAD_DIR: Path
STATIC_DIR: Path

# ============================================================================
# Authentication and session authorization
# ============================================================================


# Bind domain services to the live context before route registration.
from python.scrying_glass_services import install_services
_services = install_services(sys.modules[__name__])



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

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


    try:
        STORAGE = SQLiteStorage(DATA_DIR / "scrying-glass.sqlite3")
        initialize_users()
        with STORAGE.transaction():
            imported = import_legacy_storage()
            load_state()
            clean_order()
            save_state()
    except Exception as exc:
        if "STORAGE" in globals():
            STORAGE.close()
        sys.exit(f"Unable to initialize database: {exc}")
    if STORAGE.migration_backup is not None:
        print(f"Normalized database upgrade complete; backup: {STORAGE.migration_backup}")
    if imported["campaigns"]:
        print(f"Imported legacy storage into SQLite: {imported}")

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
    finally:
        STORAGE.close()
