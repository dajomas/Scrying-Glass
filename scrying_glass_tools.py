import re

from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException

def setup_slug(name: str) -> str:
    """Setup slug."""
    slug = re.sub('[^a-z0-9]+', '-', name.strip().lower()).strip('-')
    if not slug:
        raise HTTPException(400, 'Setup name must contain letters or numbers')
    return slug[:80]

def campaign_slug(name: str) -> str:
    """Campaign slug."""
    slug = re.sub('[^a-z0-9]+', '-', name.strip().lower()).strip('-')
    if not slug:
        raise HTTPException(400, 'Campaign name must contain letters or numbers')
    return slug[:80]

def now_iso() -> str:
    """Now iso."""
    return datetime.now(timezone.utc).isoformat()

def unique_setup_path(directory: Path, stem: str) -> Path:
    """Unique setup path."""
    dst = directory / f'{stem}.json'
    counter = 2
    while dst.exists():
        dst = directory / f'{stem}-{counter}.json'
        counter += 1
    return dst

def unique_ids(ids: list[str]) -> list[str]:
    """Unique ids."""
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
