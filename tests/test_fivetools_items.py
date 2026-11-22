"""SG-TODO-033 part 2: generated 5e.tools magic-item variants (Renderer.item at the pinned runtime).

Synthetic data stands in for the dataset; the full comparison against the pinned runtime is
``tools/fivetools_oracle`` (230 generic and 3,513 specific variants and 90 item copies
identical, see handover 730).
"""
import json
import time
import unittest

from python.scrying_glass_fivetools_fetch import allowed_dataset_path
from python.scrying_glass_fivetools_items import (ItemVariantError, apply_all_properties, apply_properties,
                                                  generate_variants, split_by_tags)
from python.scrying_glass_fivetools_ordered_resolution import OrderedResolver
from python.scrying_glass_fivetools_preparation import prepare_statblock
from python.scrying_glass_fivetools_resolution import DatasetLoader, Identity

LONGSWORD = {'name': 'Longsword', 'source': 'PHB', 'page': 149, 'type': 'M', 'weapon': True, 'weaponCategory': 'martial',
             'property': ['V'], 'dmg1': '1d8', 'dmgType': 'S', 'dmg2': '1d10', 'weight': 3, 'value': 1500, 'srd': True}
TRIDENT = {'name': 'Spiked Trident', 'source': 'SCAG', 'page': 7, 'type': 'M', 'weapon': True, 'weaponCategory': 'martial',
           'dmg1': '1d6', 'dmgType': 'P', 'weight': 4, 'value': 500}
SHIELD = {'name': 'Shield', 'source': 'PHB', 'type': 'S', 'armor': True, 'ac': 2, 'value': 1000}
PLUS_ONE = {'name': '+1 Weapon', 'source': 'DMG', 'type': 'GV', 'requires': [{'weapon': True}], 'excludes': {'net': True},
            'inherits': {'namePrefix': '+1 ', 'source': 'DMG', 'page': 213, 'rarity': 'uncommon', 'bonusWeapon': '+1',
                         'lootTables': ['Magic Item Table F'],
                         'entries': ['You have a {=bonusWeapon} bonus to attack and damage rolls made with this magic weapon.',
                                     {'type': 'entries', 'name': 'Note', 'entries': ['{=baseName} of {=dmgType} damage']}]}}
GOLDEN = {'name': 'Golden Weapon', 'source': 'XGE', 'requires': [{'weaponCategory': 'martial'}],
          'inherits': {'nameSuffix': ' of Gold', 'source': 'XGE', 'rarity': 'rare', 'valueExpression': '[[baseItem.value]] * 4',
                       'propertyAdd': ['F'], 'resist': ['fire']}}
COPIED = {'name': 'Bright Golden Weapon', 'source': 'XGE',
          '_copy': {'name': 'Golden Weapon', 'source': 'XGE', '_mod': {'inherits.nameSuffix': {'mode': 'setProp', 'value': ' of Light'}}}}


def generate(bases=(LONGSWORD, TRIDENT, SHIELD), variants=(PLUS_ONE, GOLDEN, COPIED), loot=None):
    return generate_variants({'baseitem': [dict(b) for b in bases]},
                             {'magicvariant': [json.loads(json.dumps(v)) for v in variants],
                              'linkedLootTables': loot or {}}, deadline=time.monotonic() + 30)


def by_name(items):
    return {item['name']: item for item in items}


class PropertyTests(unittest.TestCase):
    def test_split_and_inject(self):
        self.assertEqual(split_by_tags('a {@b {=c}} d {=e} f'), ['a ', '{@b {=c}}', ' d ', '{=e}', ' f'])
        self.assertEqual(apply_properties('{@b {=x}} and {=x/u} and {=y}', {'x': 'axe'}), '{@b axe} and AXE and undefined')
        self.assertEqual(apply_properties('{=x/a} {=x/at} {=n}', {'x': 'Ice', 'n': 2}), 'an An 2')
        for text, obj in (('{=x/l}', {}), ('{=x/z}', {'x': 'a'}), ('{=x/v}', {'x': 1})):
            with self.subTest(text=text), self.assertRaises(ItemVariantError):
                apply_properties(text, obj)

    def test_arrays_rebuilt_objects_rewritten_in_place(self):
        nested = {'entries': ['{=x}']}
        entries = ['{=x}', nested]
        out = apply_all_properties(entries, {'x': 'one'})
        self.assertIsNot(out, entries)
        self.assertEqual(entries[0], '{=x}')
        self.assertIs(out[1], nested)
        self.assertEqual(nested['entries'], ['one'])  # later variants see this, as in the runtime


class GenerationTests(unittest.TestCase):
    def test_generic_variants_carry_their_inherited_properties(self):
        generics, _ = generate()
        plus, golden, bright = generics
        self.assertEqual((plus['rarity'], plus['bonusWeapon'], plus['_isInherited']), ('uncommon', '+1', True))
        self.assertEqual(plus['entries'][0], 'You have a +1 bonus to attack and damage rolls made with this magic weapon.')
        self.assertEqual(plus['entries'][1]['entries'], ['undefined of undefined damage'])  # no base item yet
        self.assertEqual(golden['property'], ['F'])
        self.assertEqual((bright['inherits']['nameSuffix'], bright['_isCopy']), (' of Light', True))

    def test_specific_variants(self):
        _, specifics = generate()
        names = [item['name'] for item in specifics]
        self.assertEqual(names, ['+1 Longsword', 'Longsword of Gold', 'Longsword of Light', '+1 Spiked Trident',
                                 'Spiked Trident of Gold', 'Spiked Trident of Light'])  # the shield is no weapon
        sword = by_name(specifics)['+1 Longsword']
        self.assertEqual((sword['source'], sword['rarity'], sword['baseItem'], sword['_baseName'], sword['_baseValue']),
                         ('DMG', 'uncommon', 'longsword|phb', 'Longsword', 1500))
        self.assertEqual(sword['_baseSource'], 'PHB')
        for gone in ('value', 'srd'):
            self.assertNotIn(gone, sword)
        self.assertEqual(sword['page'], 213)  # the base item's page is dropped; the variant's comes in
        self.assertEqual(sword['_baseSrd'], True)
        self.assertEqual(sword['_fullEntries'][0], 'You have a +1 bonus to attack and damage rolls made with this magic weapon.')
        self.assertEqual(sword['genericVariant'], {'name': '+1 Weapon', 'source': 'DMG'})
        gold = by_name(specifics)['Longsword of Gold']
        self.assertEqual((gold['value'], gold['property'], gold['resist']), (6000, ['V', 'F'], ['fire']))

    def test_non_core_base_items_get_the_runtime_note(self):
        _, specifics = generate()
        trident = by_name(specifics)['+1 Spiked Trident']
        self.assertEqual(trident['_fullEntries'][0], {
            'type': 'wrapper', 'data': {'item__mergedEntryTag': 'note'},
            'wrapped': '{@note The {@item Spiked Trident|SCAG|base item} can be found in Sword Coast Adventurer’s Guide, page 7.}'})
        # The nested entry was rewritten in place for the first base item and stays so.
        self.assertEqual(trident['_fullEntries'][2]['entries'], ['undefined of undefined damage'])

    def test_editions_requirements_and_loot_tables(self):
        modern = dict(LONGSWORD, source='XPHB', edition='one')
        classic = dict(PLUS_ONE, edition='classic')
        _, specifics = generate(bases=(modern,), variants=(classic, GOLDEN))
        self.assertEqual([item['name'] for item in specifics], ['Longsword of Gold'])  # "one" base, "classic" variant
        _, specifics = generate(bases=(LONGSWORD,), variants=(PLUS_ONE,), loot={'DMG': {'+1 Longsword': ['Table X']}})
        self.assertEqual(specifics[0]['lootTables'], ['Magic Item Table F', 'Table X'])
        with self.assertRaises(ItemVariantError):
            generate(bases=(dict(LONGSWORD, edition='future'),), variants=(dict(PLUS_ONE, edition='classic'),))

    def test_unsupported_data_fails_closed(self):
        with self.assertRaises(ItemVariantError):
            generate(bases=(dict(TRIDENT, source='NEW'),), variants=(PLUS_ONE,))  # no full source name known
        with self.assertRaises(ItemVariantError):
            generate(variants=(dict(GOLDEN, inherits=dict(GOLDEN['inherits'], valueExpression='2d6 * [[baseItem.value]]')),))


class ItemPreserveTests(unittest.TestCase):
    def test_item_copies_keep_loot_tables_only_when_preserved(self):
        base = {'name': 'Wand', 'source': 'DMG', 'rarity': 'rare', 'lootTables': ['G'], 'tier': 'major'}
        plain = {'name': 'Charred Wand', 'source': 'WDH', '_copy': {'name': 'Wand', 'source': 'DMG'}}
        kept = {'name': 'Kept Wand', 'source': 'WDH', '_copy': {'name': 'Wand', 'source': 'DMG', '_preserve': {'tier': True}}}
        loader = DatasetLoader('d', [(Identity('d', 'item', r['source'], r['name']), json.dumps(r).encode()) for r in (base, plain, kept)])
        resolve = lambda name: OrderedResolver(loader).resolve(Identity('d', 'item', 'WDH', name), deadline=time.monotonic() + 30).record()
        self.assertEqual({k: resolve('Charred Wand').get(k) for k in ('rarity', 'lootTables', 'tier')},
                         {'rarity': 'rare', 'lootTables': None, 'tier': None})
        self.assertEqual(resolve('Kept Wand')['tier'], 'major')


class PreparationTests(unittest.TestCase):
    MONSTER = {'name': 'Knight', 'source': 'TST', 'size': ['M'], 'type': 'humanoid', 'ac': [18], 'hp': {'average': 52},
               'speed': {'walk': 30}, 'str': 16, 'dex': 11, 'con': 14, 'int': 11, 'wis': 11, 'cha': 15, 'passive': 10, 'cr': '3',
               'action': [{'name': 'Longsword', 'entries': ['It swings its {@item +1 longsword|DMG}.']}]}

    def fetch(self, path):
        files = {'bestiary/index.json': {'TST': 'bestiary-tst.json'}, 'bestiary/bestiary-tst.json': {'monster': [self.MONSTER]},
                 'items.json': {'item': [], 'itemGroup': []}, 'items-base.json': {'baseitem': [LONGSWORD]},
                 'magicvariants.json': {'magicvariant': [PLUS_ONE]}}
        if path not in files:
            raise LookupError('reference_unavailable')
        return json.dumps(files[path]).encode()

    def test_generated_item_is_a_full_definition(self):
        self.assertTrue(allowed_dataset_path('magicvariants.json'))
        snapshot = prepare_statblock('Knight', 'TST', fetch=self.fetch, deadline=time.monotonic() + 30).snapshot
        self.assertEqual(snapshot['completeness'], 'available')
        self.assertEqual([w['code'] for w in snapshot['warnings']], [])
        item = next(d for d in snapshot['definitions'] if d['kind'] == 'item')
        self.assertEqual((item['name'], item['source_code']), ('+1 Longsword', 'DMG'))
        facts = {f['label']: f['display_text'] for f in snapshot['facts'] if f.get('definition_id') == item['local_id']}
        self.assertEqual(facts['Rarity'], 'uncommon')
        text = [n.get('text') for n in snapshot['nodes'] if n.get('definition_id') == item['local_id'] and n.get('text')]
        self.assertIn('You have a +1 bonus to attack and damage rolls made with this magic weapon.', text)

    def test_missing_variant_data_keeps_the_reference_unavailable(self):
        original = self.fetch
        self.fetch = lambda path: (_ for _ in ()).throw(LookupError('reference_unavailable')) if path == 'magicvariants.json' else original(path)
        snapshot = prepare_statblock('Knight', 'TST', fetch=self.fetch, deadline=time.monotonic() + 30).snapshot
        self.assertEqual((snapshot['completeness'], [w['code'] for w in snapshot['warnings']]),
                         ('partial', ['reference_unavailable']))


if __name__ == '__main__':
    unittest.main()
