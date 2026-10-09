import csv
import json
import re
import uuid
import io

from typing import Any

from fastapi import HTTPException

def parse_monster(raw: bytes) -> dict[str, Any]:
    """Parse a UTF-8 JSON monster file, preserving numeric zero values."""
    try:
        data = json.loads(raw.decode("utf-8"))
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

    name = str(data.get("name") or "").strip()
    monster_species = str(data.get("type") or "").strip()

    hp_raw = data.get("hpText")
    if hp_raw is None or str(hp_raw).strip() == "":
        hp_raw = data.get("hp")

    hp_match = (
        re.search(r"-?\d+", str(hp_raw))
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
            and str(data[field]).strip() != ""
        ),
        None,
    )

    ac_match = (
        re.search(r"\d+", str(ac_raw))
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

    def storage_integer(match, field):
        digits = match.group()
        significant = digits.lstrip("-").lstrip("0") or "0"
        if len(significant) > 19:
            raise HTTPException(400, f".monster {field} exceeds the supported integer range")
        try:
            value = int(digits)
        except ValueError as exc:
            raise HTTPException(400, f".monster {field} is not a usable integer") from exc
        if not -(2 ** 63) <= value <= 2 ** 63 - 1:
            raise HTTPException(400, f".monster {field} exceeds the supported integer range")
        return value

    return {
        "name": name,
        "monster_species": monster_species,
        "ac": storage_integer(ac_match, "AC"),
        "hp": storage_integer(hp_match, "HP"),
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
    hp = csv_int(row, "hp", minimum=-99999, maximum=99999, row_number=row_number)

    if not name:
        raise HTTPException(400, f"CSV row {row_number}: name is required")

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

    ident = csv_combatant_id(row, row_number)

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

    ident = csv_combatant_id(row, row_number)

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
            default=hp > 0,
            row_number=row_number,
        ),
        "visible": csv_bool(row, "visible", default=False, row_number=row_number),
        "in_turn": False,
    }
