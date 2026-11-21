"""022.04e preparation on a synthetic dataset; no third-party data or network."""
import json
import time
import unittest

from python.scrying_glass_fivetools_collector import CollectionLimits
from python.scrying_glass_fivetools_fetch import allowed_dataset_path
from python.scrying_glass_fivetools_preparation import PreparationError, PreparationLimits, prepare_statblock
from python.scrying_glass_statblock_model import ModelLimits, content_digest, validate_snapshot


def dataset():
    wight = {'name': 'Grave Wight', 'source': 'TST', 'size': ['M'], 'type': 'undead', 'alignment': ['N', 'E'],
             'ac': [14], 'hp': {'average': 45, 'formula': '6d8 + 18'}, 'initiative': {'proficiency': 1},
             'speed': {'walk': 30}, 'str': 15, 'dex': 14, 'con': 16, 'int': 10, 'wis': 13, 'cha': 15,
             'senses': ['darkvision 60 ft.'], 'passive': 13, 'languages': ['the languages it knew in life'], 'cr': '3',
             'trait': [{'name': 'Sunlight Sensitivity', 'entries': ['The grave wight\'s eyes burn; see {@condition Blinded|TST}.']}],
             'action': [{'name': 'Life Drain', 'entries': ['{@atk mw} {@hit 4} The grave wight drains. A slain humanoid rises as a {@creature Grave Thrall|TST}, not a grave wight thrall.']}],
             'spellcasting': [{'name': 'Innate Spellcasting', 'headerEntries': ['The grave wight casts:'], 'will': ['{@spell Chill|TST}'],
                               'displayAs': 'action'}],
             'legendaryGroup': {'name': 'Grave Wight', 'source': 'TST'}, 'srd52': True,
             'mysteryProperty': {'a': 'shown anyway'}, 'damageTags': ['N']}
    elder = {'name': 'Grave Wight Elder', 'source': 'TST',
             '_copy': {'name': 'Grave Wight', 'source': 'TST', '_templates': [{'name': 'Veteran', 'source': 'TST'}],
                       '_mod': {'*': {'mode': 'replaceTxt', 'replace': 'the grave wight', 'with': 'the elder', 'flags': 'i'},
                                'action': {'mode': 'appendArr', 'items': {'name': 'Command', 'entries': ['<$name$> commands ({@dc <$dc__cha$>}).']}}}},
             'cr': '5'}
    thrall = {'name': 'Grave Thrall', 'source': 'TST', 'size': ['M'], 'type': 'undead', 'ac': [12], 'hp': {'average': 9, 'formula': '2d8'},
              'str': 10, 'dex': 10, 'con': 10, 'int': 3, 'wis': 8, 'cha': 3, 'cr': '1/4',
              'action': [{'name': 'Claw', 'entries': ['It claws, causing {@condition Blinded|TST}.']}]}
    files = {
        'bestiary/index.json': {'TST': 'bestiary-tst.json'},
        'bestiary/bestiary-tst.json': {'monster': [wight, elder, thrall]},
        'bestiary/template.json': {'monsterTemplate': [{'name': 'Veteran', 'source': 'TST', 'apply': {
            '_root': {'treasure': ['armaments']},
            '_mod': {'trait': {'mode': 'appendArr', 'items': {'name': 'Veteran', 'entries': ['<$title_short_name$> has seen battle.']}}}}}]},
        'bestiary/legendarygroups.json': {'legendaryGroup': [{'name': 'Grave Wight', 'source': 'TST',
                                                              'regionalEffects': ['Graves near the grave wight\'s lair stir.']}]},
        'spells/index.json': {'TST': 'spells-tst.json'},
        'spells/spells-tst.json': {'spell': [{'name': 'Chill', 'source': 'TST', 'level': 0, 'school': 'N',
                                              'time': [{'number': 1, 'unit': 'action'}], 'range': {'type': 'point', 'distance': {'type': 'feet', 'amount': 60}},
                                              'components': {'v': True, 's': True}, 'duration': [{'type': 'instant'}],
                                              'entries': ['A chill; see {@variantrule Cold|TST}.']}]},
        'conditionsdiseases.json': {'condition': [{'name': 'Blinded', 'source': 'TST', 'entries': ['You cannot see.']}], 'disease': [], 'status': []},
        'variantrules.json': {'variantrule': [{'name': 'Cold', 'source': 'TST', 'ruleType': 'C', 'entries': ['Cold hurts.']}]},
        'generated/gendata-variantrules.json': {'variantrule': []},
    }
    return {path: json.dumps(value).encode() for path, value in files.items()}


class Fetcher:
    def __init__(self, files=None):
        self.files, self.calls = files or dataset(), []

    def __call__(self, path):
        assert allowed_dataset_path(path), path
        self.calls.append(path)
        if path not in self.files:
            raise LookupError('reference_unavailable')
        return self.files[path]


def prepare(name='Grave Wight', source='TST', fetch=None, **kwargs):
    return prepare_statblock(name, source, fetch=fetch or Fetcher(), deadline=time.monotonic() + 30, **kwargs)


def text_of(snapshot, owner=None):
    children = {}
    for node in snapshot['nodes']:
        if node.get('definition_id') == owner:
            children.setdefault(node['parent_local_id'], []).append(node)
    out = []
    def walk(parent):
        for node in sorted(children.get(parent, []), key=lambda n: n['position']):
            out.append(node.get('text') or ('[SPECIES]' if node['kind'] == 'species_placeholder' else
                       f"<{node['label']}>" if node['kind'] == 'reference' else ''))
            walk(node['local_id'])
    walk(None)
    return ''.join(out)


class PreparationTests(unittest.TestCase):
    def test_snapshot_validates_and_excludes_scrying_glass_fields(self):
        prepared = prepare()
        snapshot = prepared.snapshot
        validate_snapshot(snapshot)
        self.assertEqual(snapshot['content_digest'], content_digest(snapshot))
        self.assertEqual(snapshot['source_label'], 'Grave Wight')
        self.assertEqual(snapshot['subtitle'], 'Medium Undead, Neutral Evil')
        root_keys = {f['key'] for f in snapshot['facts'] if 'definition_id' not in f}
        self.assertFalse(root_keys & {'armor_class', 'hit_points', 'initiative', 'name'})
        self.assertIn('challenge', root_keys)
        self.assertEqual(prepared.measurements['supporting_definitions'], 4)

    def test_references_definitions_and_placeholders(self):
        snapshot = prepare().snapshot
        kinds = [(d['kind'], d['name']) for d in snapshot['definitions']]
        self.assertEqual(sorted(kinds), [('condition', 'Blinded'), ('monster', 'Grave Thrall'), ('spell', 'Chill'), ('variantrule', 'Cold')])
        text = text_of(snapshot)
        self.assertIn("The [SPECIES]'s eyes burn; see <Blinded>.", text)
        self.assertIn('rises as a <Grave Thrall>, not a [SPECIES] thrall.', text)
        self.assertIn("Graves near the [SPECIES]'s lair stir.", text)
        thrall = next(d['local_id'] for d in snapshot['definitions'] if d['name'] == 'Grave Thrall')
        self.assertIn('<Blinded>', text_of(snapshot, thrall))
        thrall_facts = {f['key'] for f in snapshot['facts'] if f.get('definition_id') == thrall}
        self.assertIn('armor_class', thrall_facts)
        self.assertEqual(snapshot['completeness'], 'available')
        self.assertEqual([w['code'] for w in snapshot['warnings']], ['unrecognized_property'])
        sections = [n['label'] for n in snapshot['nodes'] if n['kind'] == 'section' and n['definition_id'] is None]
        self.assertEqual(sections, ['Traits', 'Actions', 'Regional Effects'])

    def test_inheritance_templates_and_substitutions(self):
        snapshot = prepare('Grave Wight Elder').snapshot
        text = text_of(snapshot)
        self.assertIn('[SPECIES] commands (DC 13).', text)
        self.assertIn('the elder elder has seen battle.', text)
        self.assertIn("the elder's eyes burn", text.lower())
        roles = [(p['role'], p['entity_id']) for p in snapshot['provenance'] if 'definition_id' not in p]
        self.assertEqual(roles[:3], [('selected', 'monster|Grave Wight Elder|TST'), ('base', 'monster|Grave Wight|TST'),
                                     ('template', 'monsterTemplate|Veteran|TST')])
        treasure = [f['display_text'] for f in snapshot['facts'] if f['key'] == 'treasure']
        self.assertEqual(treasure, ['armaments'])

    def test_missing_references_are_partial_not_substituted(self):
        files = dataset()
        files['variantrules.json'] = json.dumps({'variantrule': []}).encode()
        snapshot = prepare(fetch=Fetcher(files)).snapshot
        self.assertEqual(snapshot['completeness'], 'partial')
        self.assertIn('reference_unavailable', [w['code'] for w in snapshot['warnings']])
        self.assertNotIn('Cold', [d['name'] for d in snapshot['definitions']])

    def test_reference_limits(self):
        def limited(**values):
            return PreparationLimits(collection=CollectionLimits(**values))
        cases = ((dict(reference_steps=1), 'reference_depth_limit'), (dict(supporting_definitions=1), 'supporting_definitions_limit'),
                 (dict(supporting_reference_bytes=200), 'supporting_reference_bytes_limit'), (dict(dataset_files=5), 'dataset_file_limit'))
        for values, code in cases:
            with self.subTest(code=code):
                snapshot = prepare(limits=limited(**values)).snapshot
                self.assertEqual(snapshot['completeness'], 'partial')
                self.assertIn(code, [w['code'] for w in snapshot['warnings']])

    def test_failures_are_explicit(self):
        for kwargs, code in ((dict(name='Nope'), 'selected_unavailable'),
                             (dict(limits=PreparationLimits(model=ModelLimits(content_nodes=5))), 'node_limit'),
                             (dict(limits=PreparationLimits.from_mapping({'snapshot_bytes': 500})), 'snapshot_limit')):
            with self.subTest(code=code):
                with self.assertRaises(PreparationError) as caught:
                    prepare(**kwargs)
                self.assertEqual(caught.exception.code, code)
        with self.assertRaises(PreparationError) as caught:
            prepare_statblock('Grave Wight', 'TST', fetch=Fetcher(), deadline=time.monotonic() + 30, cancelled=lambda: True)
        self.assertEqual(caught.exception.code, 'cancelled')
        with self.assertRaises(PreparationError) as caught:
            prepare_statblock('Grave Wight', 'TST', fetch=Fetcher(), deadline=time.monotonic() - 1)
        self.assertEqual(caught.exception.code, 'deadline')
        with self.assertRaises(ValueError):
            PreparationLimits.from_mapping({'not_a_limit': 1})

    def test_unsafe_markup_and_links_never_survive(self):
        files = dataset()
        data = json.loads(files['bestiary/bestiary-tst.json'])
        data['monster'][0]['trait'].append({'name': 'Odd', 'entries': ['<script>x</script> {@link a|javascript:alert(1)} {@link b|https://example.org/x} {@b bold {@i both}}',
                                                                      {'type': 'image', 'href': {'type': 'external', 'url': 'https://example.org/i.png'}, 'title': 'Pic'}]})
        files['bestiary/bestiary-tst.json'] = json.dumps(data).encode()
        snapshot = prepare(fetch=Fetcher(files)).snapshot
        links = [n['url'] for n in snapshot['nodes'] if n['kind'] == 'link']
        self.assertEqual(links, ['https://example.org/x'])
        self.assertIn('<script>x</script> a b bold both', text_of(snapshot))
        self.assertIn('media_omitted', [w['code'] for w in snapshot['warnings']])
        kinds = {n['kind'] for n in snapshot['nodes']}
        self.assertTrue({'strong', 'emphasis'} <= kinds)


if __name__ == '__main__':
    unittest.main()
