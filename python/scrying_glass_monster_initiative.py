"""Monster initiative calculations. Callers own transactions and ordering."""
from collections.abc import Mapping

_MISSING = object()
_ORIGINS = {"default", "manual", "import", "source"}


def _integer(value, field, *, nullable=False):
    if nullable and value is None:
        return None
    if type(value) is not int:
        raise ValueError(f"{field} must be an integer" + (" or null" if nullable else ""))
    return value


def normalize_initiative(monster: Mapping) -> dict:
    total = _integer(monster.get("initiative"), "initiative", nullable=True)
    bonus = _integer(monster.get("initiative_bonus", 0), "initiative_bonus")
    origin = monster.get("initiative_bonus_origin", "default")
    if not isinstance(origin, str) or origin not in _ORIGINS:
        raise ValueError("Invalid initiative bonus origin")
    if origin == "default" and bonus != 0:
        raise ValueError("A defaulted initiative bonus must be zero")
    roll = _integer(monster.get("initiative_roll"), "initiative_roll", nullable=True)
    if roll is not None:
        total = roll + bonus
    return {"initiative": total, "initiative_roll": roll,
            "initiative_bonus": bonus, "initiative_bonus_origin": origin}


def initiative_patch(monster: Mapping, *, roll=_MISSING, bonus=_MISSING,
                     origin=_MISSING) -> dict:
    candidate = normalize_initiative(monster)
    if bonus is _MISSING and origin is not _MISSING:
        raise ValueError("Changing bonus origin requires an explicit bonus")
    if bonus is not _MISSING:
        candidate["initiative_bonus"] = _integer(bonus, "initiative_bonus")
        candidate["initiative_bonus_origin"] = "manual" if origin is _MISSING else origin
    if roll is not _MISSING:
        candidate["initiative_roll"] = _integer(roll, "initiative_roll", nullable=True)
        if roll is None:
            candidate["initiative"] = None
    return normalize_initiative(candidate)


def reset_initiative_patch(monster: Mapping) -> dict:
    """Restore the original total without retaining an unrelated current roll.

    Reset retains the assigned bonus. An original total has no historical raw
    roll, so it is retained as legacy until the next explicit roll. Old records
    without the new fields retain their existing representation.
    """
    original = _integer(monster.get("original_initiative"),
                        "original_initiative", nullable=True)
    fields = {"initiative_roll", "initiative_bonus", "initiative_bonus_origin"}
    if not fields.intersection(monster):
        return {"initiative": original}
    candidate = dict(monster, initiative=original, initiative_roll=None)
    return normalize_initiative(candidate)
