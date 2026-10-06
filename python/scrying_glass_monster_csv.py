import csv
import json
import re
import uuid

from typing import Any

from fastapi import HTTPException

def parse_monster(raw: bytes) -> dict[str, Any]:
    """Parse monster."""
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
    """Csv text."""
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
    """Csv int."""
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
    """Csv bool."""
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
    """Csv rows."""
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
    """Csv monster."""
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
    """Csv character."""
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
