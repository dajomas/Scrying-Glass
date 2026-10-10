import csv
import json
import re
import uuid
import io
from decimal import Decimal, InvalidOperation

from typing import Any
from .scrying_glass_json_import import DuplicateJsonKeyError, load_import_json

from fastapi import HTTPException

def parse_monster(raw: bytes) -> dict[str, Any]:
    """Parse a UTF-8 JSON monster file, preserving numeric zero values."""
    try:
        data = load_import_json(raw.decode("utf-8"))
    except DuplicateJsonKeyError as exc:
        raise HTTPException(400, str(exc)) from exc
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise HTTPException(
            400,
            ".monster must contain UTF-8 JSON",
        ) from exc

    if not isinstance(data, dict):
        raise HTTPException(
            400,
            ".monster must contain a JSON object",
        )

    def required_text(field):
        value = data.get(field)
        if not isinstance(value, str):
            raise HTTPException(400, f".monster {field} must be text")
        value = value.strip()
        if not 1 <= len(value) <= 100:
            raise HTTPException(400, f".monster {field} must contain 1-100 characters after trimming")
        return value

    name = required_text("name")
    monster_species = required_text("type")

    number_pattern = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"

    hp_raw = data.get("hpText")
    if hp_raw is None or (isinstance(hp_raw, str) and not hp_raw.strip()):
        hp_raw = data.get("hp")
    if hp_raw is not None and type(hp_raw) not in (str, int, float):
        raise HTTPException(400, ".monster HP must be numeric or text, not a container or boolean")

    hp_match = (
        re.search(number_pattern, str(hp_raw))
        if hp_raw is not None
        else None
    )

    ac_raw = next(
        (
            data[field]
            for field in (
                "ac",
                "armorClass",
                "otherArmorDesc",
                "natArmorBonus",
            )
            if data.get(field) is not None
            and (not isinstance(data[field], str) or data[field].strip())
        ),
        None,
    )

    if ac_raw is not None and type(ac_raw) not in (str, int, float):
        raise HTTPException(400, ".monster AC must be numeric or text, not a container or boolean")

    ac_match = (
        re.search(number_pattern, str(ac_raw))
        if ac_raw is not None
        else None
    )

    if (
        not name
        or not monster_species
        or hp_match is None
        or ac_match is None
    ):
        raise HTTPException(
            400,
            ".monster needs usable name, type, AC, and HP",
        )

    def bounded_integer(match, field, minimum, maximum):
        try:
            value = Decimal(match.group())
        except (InvalidOperation, ValueError) as exc:
            raise HTTPException(400, f".monster {field} is not a usable number") from exc
        if not value.is_finite() or value < minimum or value > maximum:
            raise HTTPException(400, f".monster {field} must be between {minimum} and {maximum}")
        if value != value.to_integral_value():
            raise HTTPException(400, f".monster {field} must be a whole number")
        return int(value)

    return {
        "name": name,
        "monster_species": monster_species,
        "ac": bounded_integer(ac_match, "AC", 0, 999),
        "hp": bounded_integer(hp_match, "HP", -(2 ** 63), 2 ** 63 - 1),
    }
 
def csv_text(value: Any, default: str = "") -> str:
    """Csv text."""
    if value is None:
        return default
    return str(value).strip()

COMBATANT_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,100}")

def csv_combatant_id(
    row: dict[str, str],
    row_number: int,
) -> str:
    """Validate a supplied combatant ID or generate one when blank."""
    ident = csv_text(row.get("id"))

    if not ident:
        return uuid.uuid4().hex

    if COMBATANT_ID_RE.fullmatch(ident) is None:
        raise HTTPException(
            400,
            f"CSV row {row_number}: id must contain 1–100 characters "
            "using only ASCII letters, digits, underscores, or hyphens",
        )

    return ident

def csv_int(
    row: dict[str, Any],
    field: str,
    *,
    default: int | None = None,
    minimum: int | None = None,
    maximum: int | None = None,
    row_number: int,
) -> int | None:
    """Parse a CSV integer and validate supplied values and defaults."""
    raw = csv_text(row.get(field))

    if raw:
        try:
            value = int(raw)
        except ValueError as exc:
            raise HTTPException(
                400,
                f"CSV row {row_number}: {field} must be a whole number",
            ) from exc
    else:
        value = default

    if value is None:
        return None

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
    """Read CSV without silently overwriting headers or dropping surplus cells."""
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(400, "CSV must be UTF-8 encoded") from exc
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        headers = reader.fieldnames
        if not headers:
            raise HTTPException(400, "CSV must contain a header row")
        normalized = [csv_text(name).casefold() for name in headers]
        if any(not name for name in normalized):
            raise HTTPException(400, "CSV column names must not be blank")
        if len(normalized) != len(set(normalized)):
            raise HTTPException(400, "CSV contains duplicate column names")
        reader.fieldnames = normalized
        rows: list[dict[str, str]] = []
        for row in reader:
            if None in row:
                raise HTTPException(400, f"CSV record ending at line {reader.line_num} has more cells than the header")
            cleaned = {key: csv_text(value) for key, value in row.items()}
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
    monster_species = csv_text(row.get("monster_species") or row.get('monster_type') or row.get("type"))
    ac = csv_int(row, "ac", minimum=0, maximum=999, row_number=row_number)
    hp = csv_int(row, "hp", minimum=0, maximum=99999, row_number=row_number)

    if not 1 <= len(name) <= 100:
        raise HTTPException(400, f"CSV row {row_number}: name must contain 1-100 characters")

    if not monster_species:
        raise HTTPException(
            400,
            f"CSV row {row_number}: monster_species, monster_type or type is required",
        )

    if ac is None:
        raise HTTPException(400, f"CSV row {row_number}: ac is required")

    if hp is None:
        raise HTTPException(400, f"CSV row {row_number}: hp is required")

    maximum_hp = csv_int(
        row,
        "max_hp",
        default=max(hp, 0),
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

    if len(monster_species) > 100:
        raise HTTPException(400, f"CSV row {row_number}: monster_species must not exceed 100 characters")

    color = csv_text(row.get("color")) or "#842029"
    if len(color) > 40:
        raise HTTPException(400, f"CSV row {row_number}: color must not exceed 40 characters")

    ident = csv_combatant_id(row, row_number)

    return {
        "id": ident,
        "name": name,
        "monster_species": monster_species,
        "ac": ac,
        "hp": hp,
        "max_hp": maximum_hp,
        "original_hp": original_hp,
        "color": color,
        "image_url": csv_text(row.get("image_url")) or None,
        "active": csv_bool(row, "active", default=False, row_number=row_number),
        "alive": csv_bool(
            row,
            "alive",
            default=hp > 0,
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

    if not 1 <= len(name) <= 100:
        raise HTTPException(400, f"CSV row {row_number}: name must contain 1-100 characters")

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

    color = csv_text(row.get("color")) or "#1f4e79"
    if len(color) > 40:
        raise HTTPException(400, f"CSV row {row_number}: color must not exceed 40 characters")

    ident = csv_combatant_id(row, row_number)

    return {
        "id": ident,
        "name": name,
        "color": color,
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
            default=hp > 0,
            row_number=row_number,
        ),
        "visible": csv_bool(row, "visible", default=False, row_number=row_number),
        "in_turn": False,
    }
