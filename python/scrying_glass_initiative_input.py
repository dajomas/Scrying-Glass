"""Strict signed initiative-bonus input for creation and .monster import."""
import re

MISSING_BONUS = object()
MIN_INTEGER = -(2 ** 63)
MAX_INTEGER = 2 ** 63 - 1
ORIGINS = {"manual", "import", "source", "default"}


def creation_bonus_fields(value=MISSING_BONUS, *, origin="manual"):
    """Default only absent/blank values; reject malformed explicit input."""
    if not isinstance(origin, str) or origin not in ORIGINS:
        raise ValueError("Invalid initiative bonus origin")
    if value is MISSING_BONUS or (isinstance(value, str) and not value.strip()):
        return {"initiative_bonus": 0, "initiative_bonus_origin": "default"}
    if isinstance(value, str):
        text = value.strip()
        if re.fullmatch(r"[+-]?[0-9]+", text) is None:
            raise ValueError("Initiative bonus must be a whole number")
        digits = text.lstrip("+-").lstrip("0") or "0"
        if len(digits) > 19:
            raise ValueError("Initiative bonus exceeds the signed 64-bit storage range")
        bonus = int(digits) * (-1 if text.startswith("-") else 1)
    elif type(value) is int:
        bonus = value
    else:
        raise ValueError("Initiative bonus must be a whole number")
    if not MIN_INTEGER <= bonus <= MAX_INTEGER:
        raise ValueError("Initiative bonus exceeds the signed 64-bit storage range")
    if origin == "default" and bonus != 0:
        raise ValueError("A defaulted initiative bonus must be zero")
    return {"initiative_bonus": bonus, "initiative_bonus_origin": origin}
