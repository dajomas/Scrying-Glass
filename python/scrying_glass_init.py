import hashlib
import hmac
import json
import re
import secrets

import yaml

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi.responses import HTMLResponse, RedirectResponse, Response

from web_html.login_html import LOGIN

DEFAULT_STORAGE_DIR = './scrying-glass-data'

DEFAULT_CONFIG = {'network': {'bind': '0.0.0.0', 'admin_port': 3000, 'client_port': 4000}, 'storage_dir': DEFAULT_STORAGE_DIR, 'security': {}, 'display': {'background': '#080b14', 'entry_direction': 'from_bottom', 'exit_direction': 'to_bottom', 'monster_width_percent': 45, 'dndbeyond_image_lookup': True}}

def merge(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge configuration mappings without modifying either input."""
    out = dict(a)
    for k, v in b.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out

def load_config(p: Path | None) -> dict[str, Any]:
    """Load JSON or YAML configuration and merge it with the defaults."""
    if p is None:
        return DEFAULT_CONFIG
    raw = p.read_text(encoding='utf-8')
    x = json.loads(raw) if p.suffix.lower() == '.json' else yaml.safe_load(raw)
    if not isinstance(x, dict):
        raise ValueError('Configuration root must be a mapping/object')
    return merge(DEFAULT_CONFIG, x)

def password_hash(password: str, salt: bytes | None=None) -> str:
    """Password hash."""
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1)
    return f'scrypt${salt.hex()}${digest.hex()}'

def password_ok(password: str, stored: str) -> bool:
    """Verify a password, rejecting malformed stored hashes safely."""
    if not isinstance(password, str) or not isinstance(stored, str):
        return False

    if not stored.startswith("scrypt$"):
        return hmac.compare_digest(
            password.encode("utf-8"),
            stored.encode("utf-8"),
        )

    parts = stored.split("$")
    if len(parts) != 3:
        return False

    _, salt_hex, digest_hex = parts

    if (
        not salt_hex
        or len(salt_hex) % 2 != 0
        or re.fullmatch(r"[0-9a-fA-F]+", salt_hex) is None
        or re.fullmatch(r"[0-9a-fA-F]{128}", digest_hex) is None
    ):
        return False

    try:
        salt = bytes.fromhex(salt_hex)
        expected_digest = bytes.fromhex(digest_hex)

        actual_digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=2 ** 14,
            r=8,
            p=1,
            dklen=64,
        )
    except ValueError:
        return False

    return hmac.compare_digest(
        actual_digest,
        expected_digest,
    )

def login(error: str='') -> HTMLResponse:
    """Render the login page with an optional error message."""
    return HTMLResponse(LOGIN.replace('{error}', f'<p class="error">{error}</p>' if error else ''))
