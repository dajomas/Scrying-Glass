"""Validated explicit 5e.tools initiative offers; no absent-field Dex fallback."""
from .scrying_glass_initiative_input import creation_bonus_fields


def _unavailable(status, reason):
    return dict(initiative_bonus=None, initiative_bonus_status=status,
                initiative_bonus_reason=reason)


def _proficiency_bonus(raw):
    if isinstance(raw, dict):
        raw = raw.get("cr")
    if isinstance(raw, str):
        if raw in {"0", "1/8", "1/4", "1/2"}:
            return 2
        if raw not in {str(value) for value in range(1, 31)}:
            raise ValueError("Unsupported challenge rating")
        raw = int(raw)
    if type(raw) is not int or not 0 <= raw <= 30:
        raise ValueError("Unsupported challenge rating")
    return max(2, (raw + 7) // 4)


def fivetools_initiative_offer(monster):
    """Interpret explicit totals or explicit proficiency multipliers (0/1/2).

    This deliberately does not reproduce the renderer's missing-initiative
    Dexterity fallback. Advantage changes passive initiative, not this bonus.
    Unresolved copies and unknown shapes cannot become source-backed zeroes.
    """
    if not isinstance(monster, dict):
        return _unavailable("invalid", "Invalid monster data")
    if "_copy" in monster:
        return _unavailable("missing", "Unresolved copied monster initiative")
    if "initiative" not in monster:
        return _unavailable("missing", "No explicit initiative data")
    raw = monster["initiative"]
    try:
        if type(raw) is int:
            bonus, evidence = raw, "5e.tools explicit initiative total"
        elif isinstance(raw, dict):
            if set(raw) - {"initiative", "proficiency", "advantageMode"}:
                raise ValueError("Unsupported initiative object fields")
            if "advantageMode" in raw and raw["advantageMode"] not in ("adv", "dis"):
                raise ValueError("Invalid initiative advantage mode")
            if "initiative" in raw:
                if type(raw["initiative"]) is not int:
                    raise ValueError("Explicit initiative total must be an integer")
                bonus = raw["initiative"]
                evidence = "5e.tools explicit initiative.initiative total"
            else:
                multiplier = raw.get("proficiency")
                if type(multiplier) is not int or multiplier not in (0, 1, 2):
                    raise ValueError("Expected explicit initiative proficiency multiplier 0, 1 or 2")
                dex = monster.get("dex")
                if type(dex) is not int or not 0 <= dex <= 2**63 - 1:
                    raise ValueError("Numeric Dexterity required for structured initiative")
                pb = _proficiency_bonus(monster.get("cr")) if multiplier else 0
                bonus = (dex - 10) // 2 + multiplier * pb
                evidence = (f"5e.tools initiative.proficiency={multiplier}; "
                            f"Dexterity={dex}; proficiency bonus={pb}")
        else:
            raise ValueError("Unsupported explicit initiative format")
        bonus = creation_bonus_fields(bonus, origin="source")["initiative_bonus"]
    except ValueError as exc:
        return _unavailable("invalid", str(exc))
    return dict(initiative_bonus=bonus, initiative_bonus_status="available",
                initiative_bonus_evidence=evidence)
