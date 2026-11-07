"""Read-only selected-source refresh resolution; callers must authorize scope.

No endpoint, apply, HP generation, user binding or review storage is provided here.
"""
import copy
import logging
import re
from urllib.parse import urlsplit
from .scrying_glass_monster_source_snapshot import (
    FIELDS, PROVIDER, URL, NAME, capture_source_fields, validate_source_fields,
)
from .scrying_glass_health_limits import MAX_STORED_HP
from .scrying_glass_initiative_input import creation_bonus_fields

LOG = logging.getLogger(__name__)


def _field(current, value, status, reason=''):
    return dict(current=current, proposed=value, status=status,
                enabled=status == 'available', checked=False, reason=reason)


def _hp_available(value):
    if not isinstance(value, str) or len(value) > 100:
        return False
    if re.fullmatch(r'[0-9]{1,19}', value):
        return int(value) <= MAX_STORED_HP
    match = re.fullmatch(r'([1-9][0-9]{0,18})d([1-9][0-9]{0,18})([+-][0-9]{1,19})?', value, re.I)
    if not match:
        return False
    count, sides = int(match[1]), int(match[2])
    modifier = int(match[3] or 0)
    return sides >= 2 and count + modifier >= 0 and count * sides + modifier <= MAX_STORED_HP


def proposed_fields(monster, candidate):
    """Validate fields independently; absence is never a source-backed default."""
    bonus = candidate.get('initiative_bonus')
    bonus_status = candidate.get('initiative_bonus_status', 'missing')
    if bonus_status == 'available':
        try:
            if type(bonus) is not int:
                raise ValueError()
            bonus = creation_bonus_fields(bonus, origin='source')['initiative_bonus']
        except ValueError:
            bonus, bonus_status = None, 'invalid'
    elif bonus_status not in {'missing', 'invalid', 'ambiguous'}:
        bonus, bonus_status = None, 'invalid'
    else:
        bonus = None
    ac = candidate.get('ac')
    ac_status = 'missing' if ac is None else 'available' if type(ac) is int and 0 <= ac <= 999 else 'invalid'
    hp = candidate.get('hp')
    hp_status = 'missing' if hp is None else 'available' if _hp_available(hp) else 'invalid'
    result = {
        'initiative_bonus': _field(monster.get('initiative_bonus'), bonus, bonus_status,
                                  candidate.get('initiative_bonus_reason', '')),
        'ac': _field(monster.get('ac'), ac if ac_status == 'available' else None, ac_status),
    }
    for field in ('max_hp', 'hp'):
        result[field] = _field(monster.get(field), hp if hp_status == 'available' else None, hp_status)
        result[field]['format'] = candidate.get('hp_source') if hp_status == 'available' else None
    return result


def _fetch_exact(context, monster, identity):
    from . import scrying_glass_monster_selection as selection
    from .scrying_glass_dnd_initiative_offer import dnd_initiative_offer
    display = context.CONFIG['display']
    if identity[PROVIDER] == 'D&D Beyond':
        if not display.get('dndbeyond_image_lookup', True):
            raise ValueError('Provider disabled')
        html = context.dnd_monster_detail_html(urlsplit(identity[URL]).path)
        ac, hp, hp_source = context.dnd_monster_stats_from_html(html)
        return dict(ac=ac, hp=hp, hp_source=hp_source, **dnd_initiative_offer(html))
    if not display.get('fivetools_fallback', True):
        raise ValueError('Provider disabled')
    name = identity.get(NAME) or monster['monster_species']
    candidates = selection.fivetools_candidates(name, display)
    matches = [candidate for candidate in candidates if all(
        capture_source_fields(candidate).get(key) == value for key, value in identity.items())]
    if len(matches) != 1:
        raise ValueError('Retained source missing or ambiguous')
    return matches[0]


def resolve_selected_sources(context, roster, ids, *, choices=None):
    """Return selected rows in requested order; choices are signed selection tokens.

    No candidate is auto-selected for an identity-less monster, even for one match.
    Repeating this function with row choices preserves choices for other rows when
    callers pass the same mapping. Applying changes is deliberately separate.
    """
    from . import scrying_glass_monster_selection as selection
    if (not isinstance(ids, list) or any(not isinstance(ident, str) or not ident for ident in ids)
            or len(set(ids)) != len(ids)):
        raise ValueError('Expected distinct selected monster IDs')
    if not isinstance(roster, list) or any(not isinstance(item, dict) for item in roster):
        raise ValueError('Invalid monster roster')
    indexed = {item.get('id'): item for item in roster}
    if len(indexed) != len(roster) or any(ident not in indexed for ident in ids):
        raise ValueError('Selected monster missing or duplicate roster ID')
    if choices is None:
        choices = {}
    if not isinstance(choices, dict) or set(choices) - set(ids):
        raise ValueError('Candidate choices must belong to the original selection')
    rows = []
    for ident in ids:
        monster = copy.deepcopy(indexed[ident])
        row = dict(id=ident, status='unavailable', source_fields={}, fields={})
        rows.append(row)
        species = monster.get('monster_species')
        if not isinstance(species, str) or not 1 <= len(species.strip()) <= 100:
            row['reason'] = 'Monster species unavailable'
            continue
        retained = {key: monster[key] for key in FIELDS if key in monster}
        try:
            identity = validate_source_fields(retained)
        except ValueError:
            identity = {}
        if ident in choices:
            try:
                _, identity = selection.selected_snapshot(choices[ident], species)
                if not identity:
                    raise ValueError()
            except ValueError:
                row.update(status='invalid_choice', reason='Candidate choice expired or invalid; repeat lookup.')
                continue
        if not identity:
            result = selection.lookup_candidates(context, species.strip())
            row.update(status='selection_required' if result.get('status') == 'ok' else 'failed',
                       candidates=copy.deepcopy(result.get('candidates', [])),
                       reason=result.get('reason', 'Choose a source candidate explicitly.'))
            continue
        row['source_fields'] = copy.deepcopy(identity)
        try:
            candidate = _fetch_exact(context, monster, identity)
            row['fields'] = proposed_fields(monster, candidate)
            row['status'] = 'resolved' if any(field['enabled'] for field in row['fields'].values()) else 'unavailable'
        except Exception:
            LOG.warning('Selected monster source refresh failed for %s', ident, exc_info=True)
            row.update(status='failed', reason='Retained source unavailable; no substitute was used.')
            row['fields'] = {field: _field(monster.get(field), None, 'failed')
                             for field in ('initiative_bonus', 'ac', 'max_hp', 'hp')}
    return rows
