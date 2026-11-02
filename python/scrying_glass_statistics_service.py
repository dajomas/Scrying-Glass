"""Base editing and manual restoration, using the existing feature transaction."""
import copy
from .scrying_glass_statistics import STATS, integer, statistics_token, restore_stat
from .scrying_glass_feature_rules import normalize_features


async def edit_statistics(features, ident, body):
    c = features.context
    if not isinstance(body, dict) or set(body) - {'operation','stat','bases','token'}:
        raise c.HTTPException(422, 'Invalid statistics fields')
    if body.get('token') != statistics_token(c):
        raise c.HTTPException(409, 'Encounter changed; reopen Restore statistics')
    target = features.target(ident)
    candidate = copy.deepcopy(target)
    try:
        operation = body.get('operation')
        if operation == 'restore' and set(body) <= {'operation','stat','token'}:
            count = restore_stat(candidate, body.get('stat'))
            note = f"Restored {body.get('stat')}: removed {count} reductions; no healing"
        elif operation == 'bases' and set(body) <= {'operation','bases','token'}:
            bases = body.get('bases')
            if not isinstance(bases, dict) or not bases or set(bases) - set(STATS):
                raise ValueError('Expected supported base statistics')
            candidate.setdefault('base_max_hp', candidate['max_hp'])
            for stat, value in bases.items():
                if stat == 'max_hp' or value is not None:
                    integer(value, stat, maximum=2**63-1 if stat == 'max_hp' else 30)
                candidate['base_' + stat] = value
            normalize_features(candidate)
            note = 'Original/base statistics edited: ' + ', '.join(bases)
        else:
            raise ValueError('Choose restore or bases operation')
    except (ValueError, TypeError) as exc:
        raise c.HTTPException(422, str(exc)) from exc
    c.remember_turn_successors()
    target.update(candidate)
    if not target.get('alive'):
        features.clear_concentration(ident)
        target['visible'] = True
    c.clean_order()
    features.log('statistics-' + operation, target, note=note)
    await features.persist()
    return target
