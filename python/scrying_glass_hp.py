import random
import re

from typing import Any, Callable

from fastapi import HTTPException

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
