"""Creature-specific copy modes for 022.04d (pinned 5etools-src 32ef600).

addSenses, addSaves/addAllSaves, addSkills/addAllSkills, addSpells,
replaceSpells, removeSpells, maxSize and scalarMultXp, mirroring the matching
``copyApplier._doMod_*`` functions. They ignore the property path, exactly as
upstream does, so a ``*`` group runs them once per COPY_ENTRY_PROPS target.
Spellcasting targets follow the runtime: ``name`` selects for addSpells, the
first spellcasting entry otherwise. Upstream's ineffective removeSpells filter
for constant/will/ritual is reproduced as validation without a change.
"""
from .scrying_glass_fivetools_jsregex import JsRegex
from .scrying_glass_fivetools_jsvalues import (
    ABIL_ABVS, SIZE_ABVS, SKILL_TO_ABILITY, SPELL_USES_KEYS, ability_mod_of, check_number,
    cr_to_pb, cr_to_xp_number, is_number, number_result, number_to_string, object_keys,
    safe_key, skill_to_ability, sort_lower, strict_equal, to_number, truthy,
)

USES_PROPS = ('recharge', 'legendary', 'charges', 'rest', 'restLong', 'daily', 'weekly', 'monthly', 'yearly')
LIST_PROPS = ('constant', 'will', 'ritual')


def _dict(value, ctx, code='malformed_modification_payload'):
    if type(value) is not dict:
        ctx.fail(code)
    return value


def _list(value, ctx, code='malformed_modification_payload'):
    if type(value) is not list:
        ctx.fail(code)
    return value


def add_senses(ctx, info):
    record = ctx.record()
    if 'senses' not in info:
        ctx.fail('malformed_modification_payload')
    senses = info['senses'] if type(info['senses']) is list else [info['senses']]
    if not truthy(record.get('senses')):
        record['senses'] = []
    existing = _list(record['senses'], ctx, 'unsupported_modification_target')
    for sense in senses:
        ctx.check()
        if type(sense) is not dict or type(sense.get('type')) is not str or not is_number(sense.get('range')):
            ctx.fail('malformed_modification_payload')
        check_number(sense['range'], ctx.fail)
        regex = JsRegex(sense['type'] + ' (\\d+)', 'i', ctx.fail)
        text = f"{sense['type']} {number_to_string(sense['range'])} ft."
        for index, current in enumerate(existing):
            ctx.check()
            if type(current) is not str:
                ctx.fail('unsupported_modification_target')
            match = regex.exec_groups(current)
            if match:
                if to_number(match[1], ctx.fail) < sense['range']:
                    existing[index] = text
                break
        else:
            existing.append(text)


def _proficiency(ctx, info, key, prop, ability_of):
    record = ctx.record()
    values = _dict(info.get(key), ctx)
    if not truthy(record.get(prop)):
        record[prop] = {}
    target = _dict(record[prop], ctx, 'unsupported_modification_target')
    for name in object_keys(values):
        ctx.check()
        safe_key(name, ctx.fail)
        mode = values[name]
        if not is_number(mode):
            ctx.fail('malformed_modification_payload')
        check_number(mode, ctx.fail)
        pb = cr_to_pb(record.get('cr'), ctx.fail)
        total = number_result(mode * (pb or 0) + ability_mod_of(record, ability_of(name), ctx.fail), ctx.fail)
        text = '+' + number_to_string(total) if total >= 0 else total
        if truthy(target.get(name)):
            current = to_number(target[name], ctx.fail)
            if current == current and current < total:
                target[name] = text
        else:
            target[name] = text


def add_saves(ctx, info):
    _proficiency(ctx, info, 'saves', 'save', lambda name: name)


def add_skills(ctx, info):
    _proficiency(ctx, info, 'skills', 'skill', lambda name: skill_to_ability(name, ctx.fail))


def add_all_saves(ctx, info):
    add_saves(ctx, {'mode': 'addSaves', 'saves': {abv: info.get('saves') for abv in ABIL_ABVS}})


def add_all_skills(ctx, info):
    add_skills(ctx, {'mode': 'addSkills', 'skills': {skill: info.get('skills') for skill in SKILL_TO_ABILITY}})


def _spellcasting(ctx):
    entries = ctx.record().get('spellcasting')
    if not truthy(entries):
        ctx.fail('missing_spellcasting')
    return _list(entries, ctx, 'unsupported_modification_target')


def _first_entry(ctx, entries):
    if not entries or type(entries[0]) is not dict:
        ctx.fail('unsupported_modification_target')
    return entries[0]


def add_spells(ctx, info):
    entries = _spellcasting(ctx)
    if truthy(info.get('name')):
        target = None
        for entry in entries:
            if entry is None:
                ctx.fail('unsupported_modification_target')
            if type(entry) is dict and strict_equal(entry.get('name'), info['name']):
                target = entry
                break
        if target is None:
            ctx.fail('missing_spellcasting')
    else:
        target = _first_entry(ctx, entries)
    if truthy(info.get('spells')):
        spells = _dict(target.get('spells'), ctx, 'unsupported_modification_target')
        added = _dict(info['spells'], ctx)
        for level in object_keys(added):
            ctx.check()
            safe_key(level, ctx.fail)
            if not truthy(spells.get(level)):
                spells[level] = added[level]
                continue
            new, old = _dict(added[level], ctx), _dict(spells[level], ctx, 'unsupported_modification_target')
            for key in object_keys(new):
                ctx.check()
                safe_key(key, ctx.fail)
                if not truthy(old.get(key)):
                    old[key] = new[key]
                elif type(old[key]) is list:
                    extra = new[key] if type(new[key]) is list else [new[key]]
                    old[key] = sort_lower(old[key] + extra, ctx.fail)
                elif type(old[key]) is dict:
                    ctx.fail('unsupported_modification_target')
                else:
                    old[key] = new[key]
    for prop in LIST_PROPS:
        if truthy(info.get(prop)):
            additions = _list(info[prop], ctx)
            if not truthy(target.get(prop)):
                target[prop] = []
            _list(target[prop], ctx, 'unsupported_modification_target').extend(additions)
    for prop in USES_PROPS:
        if not truthy(info.get(prop)):
            continue
        for key, spells in _dict(info[prop], ctx).items():
            ctx.check()
            if key not in SPELL_USES_KEYS:
                continue
            spells = _list(spells, ctx)
            if not truthy(target.get(prop)):
                target[prop] = {}
            group = _dict(target[prop], ctx, 'unsupported_modification_target')
            if not truthy(group.get(key)):
                group[key] = []
            _list(group[key], ctx, 'unsupported_modification_target').extend(spells)


def _replace_one(ctx, holder, meta, key):
    meta = _dict(meta, ctx)
    if 'with' not in meta:
        ctx.fail('malformed_modification_payload')
    replacement = meta['with'] if type(meta['with']) is list else [meta['with']]
    holder = _dict(holder, ctx, 'unsupported_modification_target')
    current = _list(holder.get(key), ctx, 'unsupported_modification_target')
    index = next((i for i, value in enumerate(current) if strict_equal(value, meta.get('replace'))), -1)
    if index < 0:
        ctx.fail('missing_modification_item')
    current[index:index + 1] = replacement
    holder[key] = sort_lower(current, ctx.fail)


def replace_spells(ctx, info):
    target = _first_entry(ctx, _spellcasting(ctx))
    if truthy(info.get('spells')):
        levels = _dict(target.get('spells'), ctx, 'unsupported_modification_target')
        changes = _dict(info['spells'], ctx)
        for level in object_keys(changes):
            ctx.check()
            if truthy(levels.get(level)):
                for meta in _list(changes[level], ctx):
                    _replace_one(ctx, levels[level], meta, 'spells')
    if truthy(info.get('daily')):
        for key, metas in _dict(info['daily'], ctx).items():
            ctx.check()
            if key not in SPELL_USES_KEYS:
                continue
            for meta in _list(metas, ctx):
                _replace_one(ctx, target.get('daily'), meta, key)


def _without(values, removed, ctx):
    removed = _list(removed, ctx)
    return [value for value in _list(values, ctx, 'unsupported_modification_target')
            if not any(strict_equal(value, item) for item in removed)]


def remove_spells(ctx, info):
    target = _first_entry(ctx, _spellcasting(ctx))
    if truthy(info.get('spells')):
        levels = _dict(target.get('spells'), ctx, 'unsupported_modification_target')
        changes = _dict(info['spells'], ctx)
        for level in object_keys(changes):
            ctx.check()
            group = levels.get(level)
            if not truthy(group.get('spells') if type(group) is dict else None):
                continue
            group['spells'] = _without(group['spells'], changes[level], ctx)
    for prop in LIST_PROPS:
        if truthy(info.get(prop)):
            _without(target.get(prop), info[prop], ctx)
    for prop in USES_PROPS:
        if not truthy(info.get(prop)):
            continue
        for key, spells in _dict(info[prop], ctx).items():
            ctx.check()
            if key not in SPELL_USES_KEYS:
                continue
            if not truthy(target.get(prop)):
                target[prop] = {}
            group = _dict(target[prop], ctx, 'unsupported_modification_target')
            group[key] = _without(group.get(key), spells, ctx)


def max_size(ctx, info):
    record = ctx.record()
    size = record.get('size')
    if type(size) is str:
        values = list(size)
    elif type(size) is list:
        values = list(size)
    else:
        ctx.fail('unsupported_modification_target')
    def index(value):
        return SIZE_ABVS.index(value) if type(value) is str and value in SIZE_ABVS else -1
    current = sorted((index(value) for value in values))
    limit = index(info.get('max'))
    if limit == -1 or -1 in current:
        ctx.fail('unsupported_size')
    allowed = [i for i in current if i <= limit] or [limit]
    record['size'] = [SIZE_ABVS[i] for i in allowed]


def scalar_mult_xp(ctx, info):
    import math
    record = ctx.record()
    scalar = info.get('scalar')
    if not is_number(scalar):
        ctx.fail('malformed_modification_payload')
    check_number(scalar, ctx.fail)
    def output(value):
        if value is not None and not is_number(value):
            ctx.fail('unsupported_numeric_value')
        result = (value or 0) * scalar
        if truthy(info.get('floor')):
            result = math.floor(result)
        return number_result(result, ctx.fail)
    cr = record.get('cr')
    if cr is None:
        ctx.fail('missing_modification_target')
    if type(cr) is dict and truthy(cr.get('xp')):
        cr['xp'] = output(cr['xp'])
        return
    lookup = number_to_string(cr) if is_number(cr) else cr
    current = cr_to_xp_number(lookup)
    if not (type(cr) is dict and truthy(cr.get('cr'))):
        record['cr'] = {'cr': cr}
    record['cr']['xp'] = output(current)


CREATURE_MODES = {
    'addSenses': add_senses, 'addSaves': add_saves, 'addSkills': add_skills,
    'addAllSaves': add_all_saves, 'addAllSkills': add_all_skills,
    'addSpells': add_spells, 'replaceSpells': replace_spells, 'removeSpells': remove_spells,
    'maxSize': max_size, 'scalarMultXp': scalar_mult_xp,
}
