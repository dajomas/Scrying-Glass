"""SG-TODO-034: the type, property and mastery text 5e.tools adds to an item (Renderer.item.enhanceItem).

Synthetic data stands in for items-base.json; the full comparison against the pinned runtime is
``tools/fivetools_oracle`` (``compare.py items``: all 6,706 enhanced items identical, see handover 750).
"""
import json
import time
import unittest

from python.scrying_glass_fivetools_items import STYLE_ONE_TEXT, ItemReference, ItemVariantError, enhance_item
from python.scrying_glass_fivetools_nodes import NodeBuilder
from python.scrying_glass_fivetools_preparation import prepare_statblock

TAG = 'item__mergedEntryTag'
BASE = {
    'itemProperty': [
        {'abbreviation': 'V', 'source': 'PHB', 'name': 'Versatile', 'entries': [{'type': 'entries', 'name': 'Versatile', 'entries': ['Two hands.']}]},
        {'abbreviation': 'F', 'source': 'PHB', 'name': 'Finesse'},  # no text: nothing is added
    ],
    'itemType': [
        {'abbreviation': 'AIR', 'source': 'DMG', '_copy': {'abbreviation': 'SHP', 'source': 'DMG'}, 'name': 'Airship'},
        {'abbreviation': 'SHP', 'source': 'DMG', 'name': 'Ship', 'page': 119, 'entries': ['Crew rules.']},
        {'abbreviation': 'HA', 'source': 'PHB', 'name': 'Heavy Armor'},
        {'abbreviation': 'SCF', 'source': 'PHB', 'name': 'Spellcasting Focus'},
        {'abbreviation': 'AT', 'source': 'PHB', 'name': "Artisan's Tools"},
    ],
    'itemTypeAdditionalEntries': [{'appliesTo': 'AT', 'entries': ['Tool use.']}],
    'itemMastery': [{'name': 'Sap', 'source': 'XPHB', 'page': 214, 'entries': ['Disadvantage on the next attack.']}],
}


def wrapped(item, key='_fullEntries'):
    return [(e['data'][TAG], e['wrapped']) for e in item.get(key) or [] if type(e) is dict and e.get('type') == 'wrapper']


class ReferenceTests(unittest.TestCase):
    def test_internal_type_copies_are_merged_by_abbreviation(self):
        airship = ItemReference(BASE).type('AIR|DMG')
        self.assertEqual((airship['name'], airship['entries'], airship.get('page')), ('Airship', ['Crew rules.'], None))

    def test_sourceless_references_fall_back_to_phb(self):
        reference = ItemReference(BASE)
        self.assertIs(reference.property('V'), reference.property('V|PHB'))
        self.assertIs(reference.property('V|XYZ'), reference.property('V|PHB'))

    def test_unsupported_type_copies_fail_closed(self):
        broken = dict(BASE, itemType=[{'abbreviation': 'AIR', 'source': 'DMG', '_copy': {'abbreviation': 'SHP', 'source': 'DMG', '_mod': {}}},
                                      {'abbreviation': 'SHP', 'source': 'DMG', 'entries': ['x']}])
        with self.assertRaises(ItemVariantError):
            ItemReference(broken)


class EnhanceTests(unittest.TestCase):
    def setUp(self):
        self.reference = ItemReference(BASE)

    def test_type_property_and_mastery_follow_the_item_entries_in_order(self):
        item = enhance_item({'name': 'Club', 'source': 'XPHB', 'type': 'SHP|DMG', 'entries': ['Own text.'],
                             'property': ['V', 'F'], 'mastery': ['Sap|XPHB']}, self.reference)
        self.assertEqual(item['_fullEntries'][0], 'Own text.')
        self.assertEqual([tag for tag, _ in wrapped(item)], ['type', 'property', 'mastery'])
        mastery = wrapped(item)[2][1]
        self.assertEqual(mastery, {'type': 'entries', 'name': 'Mastery: Sap', 'source': 'XPHB', 'page': 214,
                                   'entries': ['Disadvantage on the next attack.']})
        self.assertEqual(item['entries'], ['Own text.'])  # the stored entries stay as they were

    def test_heavy_armor_stealth_and_strength(self):
        item = enhance_item({'name': 'Plate', 'source': 'PHB', 'type': 'HA', 'stealth': True, 'strength': '15'}, self.reference)
        self.assertEqual(wrapped(item), [
            ('type', STYLE_ONE_TEXT['stealth']),
            ('type', 'If the wearer has a Strength score lower than 15, their speed is reduced by 10 feet.')])

    def test_spellcasting_focus_except_eberron_item_groups(self):
        focus = enhance_item({'name': 'Orb', 'source': 'PHB', 'type': 'SCF', 'scfType': 'arcane'}, self.reference)
        self.assertEqual([tag for tag, _ in wrapped(focus)], ['type.SCF'])
        group = enhance_item({'name': 'Orb of Shielding', 'source': 'ERLW', 'type': 'SCF', 'scfType': 'arcane',
                              '_isItemGroup': True}, self.reference)
        self.assertEqual(wrapped(group), [])

    def test_tools_get_the_note_and_their_type_entries_after_additional_entries(self):
        item = enhance_item({'name': 'Tinker', 'source': 'PHB', 'type': 'AT', 'additionalEntries': ['Own note.']}, self.reference)
        additional = item['_fullAdditionalEntries']
        self.assertEqual(additional[0], 'Own note.')
        self.assertEqual([e['wrapped'] for e in additional[1:]], [
            {'type': 'hr'}, '{@note See the {@variantrule Tool Proficiencies|XGE} entry for more information.}',
            {'type': 'entries', 'entries': ['Tool use.']}])
        self.assertEqual(item['additionalEntries'], ['Own note.'])

    def test_enhancing_twice_changes_nothing(self):
        item = enhance_item({'name': 'Club', 'source': 'PHB', 'property': ['V']}, self.reference)
        once = json.dumps(item)
        self.assertEqual(json.dumps(enhance_item(item, self.reference)), once)

    def test_unknown_or_sourceless_masteries_fail_closed(self):
        for mastery in ('Nick|XPHB', 'Sap'):
            with self.assertRaises(ItemVariantError):
                enhance_item({'name': 'Club', 'source': 'XPHB', 'mastery': [mastery]}, self.reference)


class WrapperNodeTests(unittest.TestCase):
    def test_wrappers_render_in_place(self):
        warnings = []
        builder = NodeBuilder(check=lambda: None, warn=lambda *a: warnings.append(a), reference=lambda *a: None)
        builder.entries(None, 'd1', [{'type': 'wrapper', 'wrapped': 'Plain text.', 'data': {TAG: 'type'}},
                                     {'type': 'wrapper', 'wrappeds': ['A.', {'type': 'entries', 'name': 'B', 'entries': ['C.']}]}], '$/x')
        self.assertEqual([r['kind'] for r in builder.rows if r.get('parent_local_id') is None], ['paragraph', 'paragraph', 'entry'])
        self.assertEqual(warnings, [])


class PreparationTests(unittest.TestCase):
    MONSTER = {'name': 'Smith', 'source': 'TST', 'size': ['M'], 'type': 'humanoid', 'ac': [10], 'hp': {'average': 9},
               'speed': {'walk': 30}, 'str': 10, 'dex': 10, 'con': 10, 'int': 10, 'wis': 10, 'cha': 10, 'passive': 10, 'cr': '0',
               'action': [{'name': 'Work', 'entries': ['It uses {@item Tinker|PHB} and {@item Club|XPHB}.']}]}
    TOOLS = {'name': 'Tinker', 'source': 'PHB', 'type': 'AT', 'entries': ['Tools.'], 'additionalEntries': ['Own note.']}
    CLUB = {'name': 'Club', 'source': 'XPHB', 'type': 'M', 'weapon': True, 'property': ['V'], 'mastery': ['Sap|XPHB']}

    def fetch(self, path, base=BASE):
        files = {'bestiary/index.json': {'TST': 'bestiary-tst.json'}, 'bestiary/bestiary-tst.json': {'monster': [self.MONSTER]},
                 'items.json': {'item': [self.TOOLS], 'itemGroup': []}, 'items-base.json': dict(base, baseitem=[self.CLUB]),
                 'magicvariants.json': {'magicvariant': []},
                 'variantrules.json': {'variantrule': [{'name': 'Tool Proficiencies', 'source': 'XGE', 'entries': ['Rules.']}]},
                 'generated/gendata-variantrules.json': {'variantrule': []}}
        if path not in files:
            raise LookupError('reference_unavailable')
        return json.dumps(files[path]).encode()

    def prepare(self, fetch):
        return prepare_statblock('Smith', 'TST', fetch=fetch, deadline=time.monotonic() + 30).snapshot

    def texts(self, snapshot, name):
        item = next(d for d in snapshot['definitions'] if d['name'] == name)
        return [n['text'] for n in snapshot['nodes'] if n.get('definition_id') == item['local_id'] and n.get('text')]

    def test_items_show_the_added_text(self):
        snapshot = self.prepare(self.fetch)
        self.assertEqual((snapshot['completeness'], [w['code'] for w in snapshot['warnings']]), ('available', []))
        self.assertEqual(self.texts(snapshot, 'Tinker')[:2], ['Tools.', 'Own note.'])
        self.assertIn('Tool use.', self.texts(snapshot, 'Tinker'))
        club = self.texts(snapshot, 'Club')
        self.assertIn('Two hands.', club)
        self.assertIn('Disadvantage on the next attack.', club)

    def test_unavailable_text_keeps_the_item_and_marks_the_snapshot_partial(self):
        snapshot = self.prepare(lambda path: self.fetch(path, base=dict(BASE, itemMastery=[])))
        self.assertEqual((snapshot['completeness'], [w['code'] for w in snapshot['warnings']]),
                         ('partial', ['item_text_unavailable']))
        self.assertEqual(self.texts(snapshot, 'Club'), [])  # the stored item, without any added text
        self.assertIn('Tool use.', self.texts(snapshot, 'Tinker'))


if __name__ == '__main__':
    unittest.main()
