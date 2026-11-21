"""Default monster colors (SG-TODO-029).

The default for a new monster is the first palette color that no monster in the
current battle setup uses; when all are in use, the palette color used by the
fewest monsters (palette order breaks ties). Characters do not count. The same
palette and rule live in ``static/monster-default-color.js`` for the Admin forms.
"""
from __future__ import annotations

from typing import Iterable

# Readable with white text (contrast 4.9:1 or better) and clearly different hues.
PALETTE = (
    "#842029", "#1d5fa8", "#2b7a34", "#7a3fa8",
    "#a8540f", "#127a84", "#a3195b", "#6b5a1a",
    "#4250b8", "#5f7a12", "#b0331f", "#4f5f6e",
)


def _key(color: object) -> str:
    return str(color or "").strip().lower()


def next_monster_color(used: Iterable[object]) -> str:
    """Return the default color given the colors the monsters already use."""
    counts = {color: 0 for color in PALETTE}
    for color in used:
        key = _key(color)
        if key in counts:
            counts[key] += 1
    return min(PALETTE, key=lambda color: (counts[color], PALETTE.index(color)))


def fill_missing_colors(rows: list[dict], monsters: Iterable[dict]) -> None:
    """Give each row without a color the next default, counting earlier rows too."""
    used = [monster.get("color") for monster in monsters]
    for row in rows:
        if not row.get("color"):
            row["color"] = next_monster_color(used)
        used.append(row["color"])
