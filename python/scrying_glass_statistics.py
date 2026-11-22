"""Attack statistic reductions: no damage, expiry or monster-specific death rules."""
import hashlib
import uuid
from .scrying_glass_health_limits import MAX_STORED_HP

ABILITIES = ('strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma')
STATS = ('max_hp',) + ABILITIES
LABELS = dict(zip(STATS, ('Max HP', 'STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA')))
# SG-TODO-025: a Max HP increase is its own mechanical kind, so reductions keep their rules.
MAX_HP_INCREASE = 'max_hp_increase'


def integer(value, name, maximum=MAX_STORED_HP, minimum=0):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f'{name} must be an integer from {minimum} to {maximum}')
    return value


def validate_mechanical(effect):
    if 'mechanical' not in effect:
        return
    m = effect['mechanical']
    if not isinstance(m, dict) or set(m) != {'version', 'stat', 'amount'}:
        raise ValueError('Unsupported mechanical schema')
    if type(m['version']) is not int or m['version'] != 1 or m['stat'] not in (*STATS, MAX_HP_INCREASE):
        raise ValueError('Unsupported statistic reduction version or stat')
    integer(m['amount'], 'Increase amount' if m['stat'] == MAX_HP_INCREASE else 'Reduction amount',
            maximum=99999, minimum=1)
    if effect.get('timing') != 'manual' or effect.get('concentration') or effect.get('anchor_id'):
        raise ValueError('Statistic reductions recover manually only')


def normalize_statistics(item):
    mechanics = [e['mechanical'] for e in item.get('effects', []) if 'mechanical' in e]
    if not mechanics and not any('base_' + s in item for s in STATS):
        return
    if mechanics and 'base_max_hp' not in item:
        raise ValueError('Mechanical effects require base_max_hp')
    item.setdefault('base_max_hp', item.get('max_hp', 0))
    for stat in STATS:
        key = 'base_' + stat
        base = item.get(key)
        if stat == 'max_hp' or base is not None:
            integer(base, key, maximum=MAX_STORED_HP if stat == 'max_hp' else 30)
        total = sum(m['amount'] for m in mechanics if m['stat'] == stat)
        if base is None and total:
            raise ValueError(f'Unknown original {LABELS[stat]}; enter its base score via Restore statistics first')
        item[key] = base
        if stat == 'max_hp':
            total -= sum(m['amount'] for m in mechanics if m['stat'] == MAX_HP_INCREASE)
            item[stat] = min(MAX_STORED_HP, max(0, base - total))
            continue
        item[stat] = None if base is None else max(0, base - total)
    item['hp'] = min(item['hp'], item['max_hp'])


def reduce_stat(item, stat, amount, source_id=None):
    from .scrying_glass_feature_rules import normalize_features
    if stat not in STATS:
        raise ValueError('Unsupported reduction statistic')
    integer(amount, 'Reduction amount', maximum=99999, minimum=1)
    if stat == 'max_hp' and item.get('track_hp') is False and 'monster_species' not in item:
        raise ValueError(f"HP is not tracked for {item.get('name')}")  # SG-TODO-024
    item.setdefault('base_max_hp', item['max_hp'])
    effect = dict(id=uuid.uuid4().hex, name=LABELS[stat] + ' reduction', source_id=source_id,
                  notes='', public=False, concentration=False, timing='manual',
                  turns=None, anchor_id=None, mechanical=dict(version=1, stat=stat, amount=amount))
    item.setdefault('effects', []).append(effect)
    normalize_features(item)
    return effect


def increase_max_hp(item, amount, source_id=None):
    """SG-TODO-025/026: raise maximum HP; current HP rises by the same amount.

    A dead creature stays dead. A downed one whose HP rises above 0 is up again
    (normalize_features). Lasts until removed by hand or by Restore statistics.
    """
    from .scrying_glass_feature_rules import normalize_features, tracks_hp
    from .scrying_glass_turn_rules import permanently_dead
    integer(amount, 'Increase amount', maximum=99999, minimum=1)
    if not tracks_hp(item):
        raise ValueError(f"HP is not tracked for {item.get('name')}")
    if permanently_dead(item):
        raise ValueError(f"{item.get('name')} is dead; explicitly recover before raising maximum HP")
    if item['max_hp'] + amount > MAX_STORED_HP:
        raise ValueError(f'Maximum HP must not exceed {MAX_STORED_HP}')
    item.setdefault('base_max_hp', item['max_hp'])
    effect = dict(id=uuid.uuid4().hex, name='Max HP increase', source_id=source_id,
                  notes='', public=False, concentration=False, timing='manual',
                  turns=None, anchor_id=None, mechanical=dict(version=1, stat=MAX_HP_INCREASE, amount=amount))
    current = item['hp']
    item.setdefault('effects', []).append(effect)
    normalize_features(item)
    item['hp'] = min(item['max_hp'], current + amount)
    normalize_features(item)
    return effect


def follow_max_increase(before, candidate, hp_given=False):
    """SG-TODO-026: when maximum HP rises and current HP was not set, current HP rises too.

    Used by the Edit dialogs and monster refresh. Dead creatures and characters whose HP
    is not tracked are left alone; the result is capped at the new maximum.
    """
    from .scrying_glass_feature_rules import tracks_hp
    from .scrying_glass_turn_rules import permanently_dead
    if hp_given or not tracks_hp(candidate) or permanently_dead(before):
        return
    rise = candidate.get('max_hp', 0) - before.get('max_hp', 0)
    if type(rise) is int and rise > 0:
        candidate['hp'] = min(candidate['max_hp'], before.get('hp', 0) + rise)


def restore_stat(item, stat):
    from .scrying_glass_feature_rules import normalize_features
    if stat not in (*STATS, 'all'):
        raise ValueError('Choose a statistic or all')
    # Restoring Max HP also removes increases (SG-TODO-025); current HP is only capped.
    removed = [e for e in item.get('effects', []) if 'mechanical' in e and
               (stat == 'all' or e['mechanical']['stat'] == stat
                or (stat == 'max_hp' and e['mechanical']['stat'] == MAX_HP_INCREASE))]
    item['effects'] = [e for e in item.get('effects', []) if e not in removed]
    normalize_features(item)
    return len(removed)


def legacy_max_edit(candidate, values):
    if 'base_max_hp' not in candidate or 'max_hp' not in values:
        return
    active = [e['mechanical'] for e in candidate.get('effects', [])
              if e.get('mechanical', {}).get('stat') in ('max_hp', MAX_HP_INCREASE)]
    net = sum(m['amount'] if m['stat'] == 'max_hp' else -m['amount'] for m in active)
    if active and values['max_hp'] != min(MAX_STORED_HP, max(0, candidate['base_max_hp'] - net)):
        raise ValueError('Active Max HP reductions or increases: edit original maximum via Restore statistics')
    if not active:
        candidate['base_max_hp'] = values['max_hp']


def statistics_token(context):
    from .scrying_glass_service_features import fingerprint
    return hashlib.sha256((str(context.active_campaign()) + ':' +
        str(context.features.store.revision()) + ':' + fingerprint(context.STATE)).encode()).hexdigest()
