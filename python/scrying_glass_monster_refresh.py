"""Pure source-refresh planning; no networking or live-state writes.

Preview must be server-owned or authenticated before calling this module.
Callers must apply returned candidates inside their existing transaction and
run normal health/statistics/order reconciliation before committing.
"""
from copy import deepcopy
from .scrying_glass_monster_initiative import initiative_patch

FIELDS = frozenset({"initiative_bonus", "ac", "max_hp", "hp"})
MAX_HP = 2 ** 63 - 1


class StaleRefreshError(ValueError):
    pass


def capture_review(scope, monsters, offers):
    """Capture only selected monsters and their server-derived offers."""
    if not monsters:
        raise ValueError("Select at least one monster")
    rows = {}
    for monster in monsters:
        ident = monster["id"]
        if not isinstance(ident, str) or not ident or ident in rows:
            raise ValueError("Invalid or duplicate selected monster ID")
        offer = offers.get(ident, {})
        if not isinstance(offer, dict) or set(offer) - FIELDS:
            raise ValueError("Invalid refresh offer")
        rows[ident] = {"before": deepcopy(monster), "offer": deepcopy(offer)}
    return {"scope": deepcopy(scope), "rows": rows}


def prepare_refresh(review, scope, live_monsters, selections, hp_factory):
    """Return replacement candidates after validating the whole selection.

    hp_factory(spec) must validate without rolling and return a callable.
    A selected HP/Max HP pair uses one generated value per monster.
    """
    if scope != review["scope"]:
        raise StaleRefreshError("Campaign or encounter changed; repeat refresh")
    if not isinstance(selections, dict) or not selections:
        raise ValueError("Select at least one field")
    live = {m["id"]: m for m in live_monsters}
    pending = []
    for ident, selected in selections.items():
        if ident not in review["rows"]:
            raise ValueError("Monster was not selected for this review")
        if not isinstance(selected, list) or not selected:
            raise ValueError("Selected fields must be a nonempty list")
        if not all(isinstance(f, str) for f in selected):
            raise ValueError("Invalid selected field")
        fields = set(selected)
        if len(fields) != len(selected) or fields - FIELDS:
            raise ValueError("Duplicate or unsupported selected fields")
        row = review["rows"][ident]
        if ident not in live or live[ident] != row["before"]:
            raise StaleRefreshError("Monster changed; repeat refresh")
        offer = row["offer"]
        if fields - set(offer) or any(offer[f] is None for f in fields):
            raise ValueError("Selected source field is unavailable")
        candidate = deepcopy(live[ident])
        if "ac" in fields:
            ac = offer["ac"]
            if type(ac) is not int or not 0 <= ac <= 999:
                raise ValueError("Source AC is invalid")
            candidate["ac"] = ac
        if "initiative_bonus" in fields:
            candidate.update(initiative_patch(candidate, bonus=offer["initiative_bonus"], origin="source"))
        hp_fields = fields & {"hp", "max_hp"}
        roller = None
        if hp_fields:
            specs = [offer[f] for f in sorted(hp_fields)]
            if len(specs) == 2 and specs[0] != specs[1]:
                raise ValueError("Source HP and Max HP must share a single HP specification")
            roller = hp_factory(specs[0])
            if not callable(roller):
                raise ValueError("Invalid HP factory")
        pending.append((ident, candidate, hp_fields, roller))
    result = {}
    for ident, candidate, hp_fields, roller in pending:
        if roller is not None:
            hp = roller()
            if type(hp) is not int or not 0 <= hp <= MAX_HP:
                raise ValueError("Generated HP is outside the storage range")
            for field in hp_fields:
                candidate[field] = hp
        result[ident] = candidate
    return result
