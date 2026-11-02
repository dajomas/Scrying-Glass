"""Attack statistic reductions: no damage, expiry or monster-specific death rules."""
import hashlib
import uuid
from .scrying_glass_health_limits import MAX_STORED_HP

ABILITIES = ('strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma')
STATS = ('max_hp',) + ABILITIES
LABELS = dict(zip(STATS, ('Max HP', 'STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA')))


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
    if type(m['version']) is not int or m['version'] != 1 or m['stat'] not in STATS:
        raise ValueError('Unsupported statistic reduction version or stat')
    integer(m['amount'], 'Reduction amount', maximum=99999, minimum=1)
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
        item[stat] = None if base is None else max(0, base - total)
    item['hp'] = min(item['hp'], item['max_hp'])


def reduce_stat(item, stat, amount, source_id=None):
    from .scrying_glass_feature_rules import normalize_features
    if stat not in STATS:
        raise ValueError('Unsupported reduction statistic')
    integer(amount, 'Reduction amount', maximum=99999, minimum=1)
    item.setdefault('base_max_hp', item['max_hp'])
    effect = dict(id=uuid.uuid4().hex, name=LABELS[stat] + ' reduction', source_id=source_id,
                  notes='', public=False, concentration=False, timing='manual',
                  turns=None, anchor_id=None, mechanical=dict(version=1, stat=stat, amount=amount))
    item.setdefault('effects', []).append(effect)
    normalize_features(item)
    return effect


def restore_stat(item, stat):
    from .scrying_glass_feature_rules import normalize_features
    if stat not in (*STATS, 'all'):
        raise ValueError('Choose a statistic or all')
    removed = [e for e in item.get('effects', []) if 'mechanical' in e and
               (stat == 'all' or e['mechanical']['stat'] == stat)]
    item['effects'] = [e for e in item.get('effects', []) if e not in removed]
    normalize_features(item)
    return len(removed)


def legacy_max_edit(candidate, values):
    if 'base_max_hp' not in candidate or 'max_hp' not in values:
        return
    total = sum(e['mechanical']['amount'] for e in candidate.get('effects', [])
                if e.get('mechanical', {}).get('stat') == 'max_hp')
    if total and values['max_hp'] != max(0, candidate['base_max_hp'] - total):
        raise ValueError('Active Max HP reductions: edit original maximum via Restore statistics')
    if not total:
        candidate['base_max_hp'] = values['max_hp']


def statistics_token(context):
    from .scrying_glass_service_features import fingerprint
    return hashlib.sha256((str(context.active_campaign()) + ':' +
        str(context.features.store.revision()) + ':' + fingerprint(context.STATE)).encode()).hexdigest()
