"""Generated 5e.tools magic-item variants (SG-TODO-033 part 2), pinned to RUNTIME_COMMIT.

Mirrors ``Renderer.item`` in js/render.js: the internal ``_copy`` merge of
``magicvariants.json``, ``_genericVariants_addInheritedPropertiesToSelf`` and
``_createSpecificVariants`` over ``items-base.json``, up to but not including
``_enhanceItems`` (item enhancement is a separate TODO). The runtime's object sharing is
kept on purpose: ``applyAllProperties`` rebuilds arrays but rewrites objects in place,
and inherited values are assigned by reference, so later variants see earlier changes
exactly as the runtime does. No network, no JavaScript execution.
"""
from __future__ import annotations

import copy
import json
import re
import time

from .scrying_glass_fivetools_jsvalues import number_to_string, truthy
from .scrying_glass_fivetools_ordered_resolution import OrderedResolver
from .scrying_glass_fivetools_resolution import DatasetLoader, Identity

CORE_SOURCES = frozenset(('PHB', 'XPHB', 'DMG', 'XDMG'))
# Parser.sourceJsonToFull (js/parser.js) for the non-core sources of pinned base items;
# a base item from any other non-core source is refused (see _source_full).
SOURCE_FULL = {
    'SCAG': 'Sword Coast Adventurer’s Guide', 'FRHoF': 'Forgotten Realms: Heroes of Faerûn',
    'OotA': 'Out of the Abyss', 'ERLW': 'Eberron: Rising from the Last War',
    'DSotDQ': 'Dragonlance: Shadow of the Dragon Queen', 'ToA': 'Tomb of Annihilation',
}
DMG_TYPES = {'A': 'acid', 'B': 'bludgeoning', 'C': 'cold', 'F': 'fire', 'O': 'force', 'L': 'lightning',
             'N': 'necrotic', 'P': 'piercing', 'I': 'poison', 'Y': 'psychic', 'R': 'radiant', 'S': 'slashing',
             'T': 'thunder'}
INHERITED_BLOCKLIST = frozenset(('entries', 'propertyAdd', 'namePrefix', 'nameSuffix', 'propertyRemove'))
VULN_RES_IMMUNE = ('vulnerable', 'resist', 'immune')
NOTE_TAG = 'item__mergedEntryTag'  # VeCt.ENTDATA_ITEM_MERGED_ENTRY_TAG
UNDEFINED = object()  # JavaScript undefined


class ItemVariantError(ValueError):
    """Data the port does not support; the stable code says what."""


def _str(value):
    """JavaScript ToString inside template literals and string concatenation."""
    if value is UNDEFINED:
        return 'undefined'
    if value is None:
        return 'null'
    if type(value) is bool:
        return 'true' if value else 'false'
    if type(value) in (int, float):
        return number_to_string(value)
    if type(value) is str:
        return value
    raise ItemVariantError('unsupported_string_coercion')


def split_by_tags(text):
    """Renderer.splitByTags: top-level {@...} and {=...} segments and the text between."""
    depth, out, cur, i = 0, [], '', 0
    while i < len(text):
        char, nxt = text[i], text[i + 1] if i + 1 < len(text) else ''
        if char == '{' and nxt in ('@', '='):
            if depth > 0:
                cur += '{'
            else:
                if cur:
                    out.append(cur)
                cur = '{' + nxt
                i += 1
            depth += 1
        elif char == '}':
            cur += '}'
            if depth != 0:
                depth -= 1
                if depth == 0:
                    if cur:
                        out.append(cur)
                    cur = ''
        else:
            cur += char
        i += 1
    if cur:
        out.append(cur)
    return out


def _title(word):
    if type(word) is not str or ' ' in word or not word.isalpha():
        raise ItemVariantError('unsupported_property_modifier')  # String.prototype.toTitleCase: single words only
    return word[:1].upper() + word[1:]


def apply_properties(text, obj):
    """Renderer.applyProperties: {=prop/modifiers} injection (modifiers apply in written order)."""
    if '{=' not in text:
        return text
    out = ''
    for part in split_by_tags(text):
        if part.startswith('{@'):
            tag, _, rest = part[1:-1].partition(' ')
            out += '{' + tag + ' ' + apply_properties(rest, obj) + '}'
            continue
        if not part.startswith('{='):
            out += part
            continue
        path, _, modifiers = part[2:-1].partition('/')
        value = obj.get(path, UNDEFINED) if type(obj) is dict else UNDEFINED
        if not modifiers:
            out += _str(value)
            continue
        if value is None or value is UNDEFINED:
            raise ItemVariantError('property_null')
        for modifier in modifiers:  # the runtime sorts a copy and discards it
            if modifier == 'a':
                text = _str(value)
                if not text:
                    raise ItemVariantError('property_null')  # fromProp[0].toLowerCase() throws
                value = 'an' if text[0].lower() in ('a', 'e', 'i', 'o', 'u') else 'a'
            elif modifier == 'l':
                value = _str(value).lower()
            elif modifier == 'u':
                value = _str(value).upper()
            elif modifier == 't':
                value = _title(value)
            else:
                raise ItemVariantError('unsupported_property_modifier')
        out += _str(value)
    return out


def apply_all_properties(value, obj):
    """Renderer.applyAllProperties with an object: arrays rebuilt, objects rewritten in place."""
    if type(value) is str:
        return apply_properties(value, obj)
    if type(value) is list:
        return [apply_all_properties(v, obj) for v in value]
    if type(value) is dict:
        for key in list(value):
            value[key] = apply_all_properties(value[key], obj)
        return value
    return value


def _get(obj, path):
    """MiscUtil.get: undefined for a missing step."""
    for key in path:
        if type(obj) is dict and key in obj:
            obj = obj[key]
        elif type(obj) is list and key.isdigit() and int(key) < len(obj):
            obj = obj[int(key)]
        else:
            return UNDEFINED
    return obj


_NUMBER = r'\s*(\d+(?:\.\d+)?)\s*'
_EXPRESSION = re.compile(_NUMBER + r'([*+])' + _NUMBER + r'\Z')


def _evaluate(expression):
    """Renderer.dice.parseRandomise2 for the pinned expressions: 'number op number', else null."""
    match = _EXPRESSION.match(expression)
    if match is None:
        if 'undefined' in expression or 'null' in expression:
            return None  # a missing base value: the runtime's parser fails and returns null
        raise ItemVariantError('unsupported_expression')
    left, op, right = float(match.group(1)), match.group(2), float(match.group(3))
    result = left * right if op == '*' else left + right
    return int(result) if result.is_integer() else result


def _unique(values):
    """Array.prototype.unique: by value for strings and numbers, by identity for objects."""
    seen, out = set(), []
    for value in values:
        key = (type(value), value) if type(value) in (str, int, float, bool) or value is None else ('id', id(value))
        if key not in seen:
            seen.add(key)
            out.append(value)
    return out


def _uid(value):
    return value.get('uid') or value if type(value) is dict else value


def _near_equal(a, b):
    return (a is None and b is None) or a == b


def _edition_match(base, generic):
    """_createSpecificVariants_isEditionMatch outside a VTT."""
    if _near_equal(base.get('edition'), generic.get('edition')):
        return True
    edition = base.get('edition')
    if edition == 'classic':
        return False
    if edition is None:
        return True
    if edition == 'one':
        return generic.get('edition') != 'classic'
    raise ItemVariantError('unsupported_edition')


def _matching(candidate_value, requirement, every):
    if type(requirement) is list:
        if type(candidate_value) is list:
            return any(v in requirement for v in candidate_value)
        return candidate_value in requirement
    if type(requirement) is dict:
        return _matches(candidate_value, requirement, every)
    if type(candidate_value) is list:
        return any(v == requirement and type(v) is type(requirement) for v in candidate_value)
    return requirement == candidate_value and type(requirement) is type(candidate_value)


def _matches(candidate, requirements, every=False):
    if candidate is None or candidate is UNDEFINED or requirements is None or type(candidate) is not dict:
        return False
    for key, requirement in requirements.items():
        found = _matching(candidate.get(key, UNDEFINED), requirement, every)
        if every and not found:
            return False
        if not every and found:
            return True
    return every


def _source_full(source):
    if source not in SOURCE_FULL:
        raise ItemVariantError('unknown_source_name')
    return SOURCE_FULL[source]


def _full_entries(item):
    if '_fullEntries' not in item or not truthy(item['_fullEntries']):
        item['_fullEntries'] = copy.deepcopy(item['entries']) if truthy(item.get('entries')) else []
    return item['_fullEntries']


def _inherit_to_self(generic):
    """_genericVariants_addInheritedPropertiesToSelf."""
    if generic.get('_isInherited'):
        return
    generic['_isInherited'] = True
    inherits = generic['inherits']
    for prop, value in inherits.items():
        if prop in INHERITED_BLOCKLIST:
            continue
        if value is None:
            generic.pop(prop, None)
        elif truthy(generic.get(prop)):
            generic[prop] = copy.deepcopy(generic[prop]) + value if type(generic[prop]) is list and type(value) is list else value
        else:
            generic[prop] = value
    if not truthy(generic.get('entries')) and truthy(inherits.get('entries')):
        generic['entries'] = copy.deepcopy(apply_all_properties(inherits['entries'], inherits))
    if truthy(inherits.get('propertyAdd')):
        generic['property'] = list(generic.get('property') or []) + list(inherits['propertyAdd'])
    requires = generic.get('requires')
    if type(requires) is dict and truthy(requires.get('armor')):  # an array in the data: never applies
        generic['armor'] = requires['armor']


def _merge_vuln_res_immune(variant, inherits):
    from_base = {prop: list(variant[prop]) for prop in VULN_RES_IMMUNE if truthy(variant.get(prop))}
    for prop in VULN_RES_IMMUNE:
        if prop not in inherits:
            continue
        value = inherits[prop]
        if value is None:
            from_base.pop(prop, None)
            continue
        names = set()
        for item in value:
            if type(item) is str:
                names.add(item)
            if type(item) is dict and truthy(item.get(prop)):
                names.update(sub for sub in item[prop] if type(sub) is str)
        for other in VULN_RES_IMMUNE:
            if other == prop or other not in from_base:
                continue
            kept = []
            for item in from_base[other]:
                if type(item) is str:
                    if item not in names:
                        kept.append(item)
                    continue
                if type(item) is dict and truthy(item.get(other)):
                    item[other] = [sub for sub in item[other] if type(sub) is not str or sub not in names]
                kept.append(item)
            from_base[other] = kept
            if not kept:
                del from_base[other]
    for prop in VULN_RES_IMMUNE:
        if prop in from_base or truthy(inherits.get(prop)):
            variant[prop] = _unique(from_base.get(prop, []) + list(inherits.get(prop) or []))
        else:
            variant.pop(prop, None)


def _specific_variant(base, generic, loot_tables):
    """_createSpecificVariants_createSpecificVariant (without the generic's back-reference)."""
    inherits = generic['inherits']
    variant = copy.deepcopy(base)
    variant.pop('_isBaseItem', None)
    variant['_isEnhanced'] = False
    variant.pop('_fullEntries', None)
    variant['_baseName'] = base['name']
    for target, key in (('_baseSrd', 'srd'), ('_baseSrd52', 'srd52'), ('_baseBasicRules', 'basicRules'),
                        ('_baseFreeRules2024', 'basicRules2024')):
        if key in base:
            variant[target] = base[key]
    if base.get('source') != inherits.get('source', UNDEFINED):
        variant['_baseSource'] = base['source']
    variant['_variantName'] = generic['name']
    if 'value' in base:
        variant['_baseValue'] = base['value']
    for key in ('value', 'srd', 'srd52', 'basicRules', 'basicRules2024', 'page', 'reprintedAs',
                'referenceSources', 'hasFluff', 'hasFluffImages'):
        variant.pop(key, None)
    variant['_category'] = 'Specific Variant'
    variant['baseItem'] = f"{base['name']}|{base['source']}".lower()
    for prop, value in sorted(inherits.items(), key=lambda kv: 0 if 'Remove' in kv[0] else 1):
        if prop == 'namePrefix':
            variant['name'] = _str(value) + variant['name']
        elif prop == 'nameSuffix':
            variant['name'] = variant['name'] + _str(value)
        elif prop == 'entries':
            entries = _full_entries(variant)
            injectable = {'baseName': base['name'], 'dmgType': None, 'bonusAc': inherits.get('bonusAc', UNDEFINED)}
            if truthy(base.get('dmgType')):
                if base['dmgType'] not in DMG_TYPES:
                    raise ItemVariantError('unknown_damage_type')
                injectable['dmgType'] = DMG_TYPES[base['dmgType']].title()  # style "one": title case
            for key in ('bonusWeapon', 'bonusWeaponAttack', 'bonusWeaponDamage', 'bonusWeaponCritDamage',
                        'bonusSpellAttack', 'bonusSpellSaveDc', 'bonusSavingThrow'):
                injectable[key] = inherits.get(key, UNDEFINED)
            for index, entry in enumerate(apply_all_properties(value, injectable)):
                entries.insert(index, entry)
        elif prop in VULN_RES_IMMUNE:
            pass
        elif prop == 'conditionImmune':
            variant[prop] = _unique(list(variant.get(prop) or []) + list(value))
        elif prop == 'nameRemove':
            variant['name'] = variant['name'].replace(_str(value), '')
        elif prop in ('weightExpression', 'valueExpression'):
            def part(match):
                path = match.group(1).split('.')
                if path[0] == 'item':
                    return _str(_get(variant, path[1:]))
                if path[0] == 'baseItem':
                    return _str(_get(base, path[1:]))
                return _str(_get(variant, path))
            result = _evaluate(re.sub(r'\[\[([^\]]+)]]', part, value))
            if result is not None:
                variant['weight' if prop == 'weightExpression' else 'value'] = result
        elif prop == 'barding':
            variant['bardingType'] = base.get('type', UNDEFINED)
            if variant['bardingType'] is UNDEFINED:
                del variant['bardingType']
        elif prop == 'propertyAdd':
            current = variant.get('property')
            variant['property'] = list(current or []) + [
                it for it in value if not current or not any(_uid(p) is _uid(it) or (type(_uid(p)) is str and _uid(p) == _uid(it))
                                                             for p in current)]
        elif prop == 'propertyRemove':
            if truthy(variant.get('property')):
                variant['property'] = [it for it in variant['property'] if _uid(it) not in value]
                if not variant['property']:
                    del variant['property']
        else:
            variant[prop] = value  # by reference, as the runtime assigns it
    _merge_vuln_res_immune(variant, inherits)
    for flag in ('hasFluff', 'hasFluffImages'):
        if truthy(generic.get(flag)):
            variant[flag] = generic[flag]
    variant['genericVariant'] = {'name': generic['name'], 'source': generic['source']}
    linked = (loot_tables or {}).get(variant['source'], {})
    if type(linked) is dict and truthy(linked.get(variant['name'])):
        if not truthy(variant.get('lootTables')):
            variant['lootTables'] = []
        variant['lootTables'].extend(linked[variant['name']])
    if base['source'] not in CORE_SOURCES:
        page = f", page {_str(base['page'])}" if truthy(base.get('page')) else ''
        _full_entries(variant).insert(0, {'type': 'wrapper', 'wrapped':
            f"{{@note The {{@item {base['name']}|{base['source']}|base item}} can be found in "
            f"{_source_full(base['source'])}{page}.}}", 'data': {NOTE_TAG: 'note'}})
    return variant


def _entity_source(record):
    """SourceUtil.getEntitySource: ``source``, else ``inherits.source``."""
    source = record.get('source')
    if not truthy(source) and type(record.get('inherits')) is dict:
        source = record['inherits'].get('source')
    return source


def _merged_generic_variants(variants, *, deadline):
    """The internal ``_copy`` merge DataUtil.loadJSON applies to magicvariants.json."""
    encode = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode()
    loader = DatasetLoader('magicvariants', [(Identity('magicvariants', 'magicvariant', _entity_source(v), v['name']), encode(v))
                                             for v in variants if type(v.get('name')) is str and type(_entity_source(v)) is str])
    resolver = OrderedResolver(loader)
    out = []
    for variant in variants:
        if '_copy' in variant:
            variant = resolver.resolve(Identity('magicvariants', 'magicvariant', _entity_source(variant), variant['name']),
                                       deadline=deadline).record()
        out.append(variant)
    return out


def generate_variants(base_data, variant_data, *, deadline=None):
    """(generic variants, specific variants) as the runtime builds them, in runtime order."""
    deadline = time.monotonic() + 30 if deadline is None else deadline
    if type(base_data) is not dict or type(variant_data) is not dict:
        raise ItemVariantError('malformed_dataset')
    bases = copy.deepcopy(base_data.get('baseitem') or [])
    generics = _merged_generic_variants(copy.deepcopy(variant_data.get('magicvariant') or []), deadline=deadline)
    loot_tables = variant_data.get('linkedLootTables')
    for generic in generics:
        if type(generic) is not dict or type(generic.get('inherits')) is not dict or type(generic.get('requires')) is not list:
            raise ItemVariantError('malformed_variant')
        _inherit_to_self(generic)
    specifics = []
    for base in bases:
        if time.monotonic() >= deadline:
            raise ItemVariantError('deadline')
        base['_isBaseItem'] = True
        base['_category'] = 'Basic'
        if base.get('entries') is None:
            base['entries'] = []
        if truthy(base.get('packContents')):
            continue
        for generic in generics:
            if not _edition_match(base, generic):
                continue
            if not any(_matches(base, requirement, True) for requirement in generic['requires']):
                continue
            if _matches(base, generic.get('excludes')):
                continue
            specifics.append(_specific_variant(base, generic, loot_tables))
    return generics, specifics
