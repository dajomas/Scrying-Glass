"""022.05-022.07 Open5e, D&D Beyond and .monster adapters: synthetic and captured evidence."""
import glob
import io
import json
import time
import unittest
from pathlib import Path

from python.scrying_glass_dndbeyond_statblock import canonical_url, discover_dndbeyond, prepare_dndbeyond, public_statblock
from python.scrying_glass_open5e_statblock import discover_open5e, prepare_open5e
from python.scrying_glass_statblock_model import validate_snapshot
from python.scrying_glass_statblock_sources import ProviderFetcher, SourceError, markdown_entries, name_key
from python.scrying_glass_tetracube_statblock import prepare_monster_file

EXAMPLES = Path(__file__).resolve().parents[1] / 'monsters_examples'
SG_KEYS = {'name', 'species', 'ac', 'armor_class', 'hp', 'hit_points', 'max_hp', 'current_hp', 'initiative_bonus',
           'attribute_ac', 'attribute_armor_class', 'attribute_hp', 'attribute_hit_points', 'attribute_initiative'}


def text_of(snapshot):
    children = {}
    for node in snapshot['nodes']:
        children.setdefault(node['parent_local_id'], []).append(node)
    out = []
    def walk(parent):
        for node in sorted(children.get(parent, []), key=lambda n: n['position']):
            out.append(node.get('text') or ('[SPECIES]' if node['kind'] == 'species_placeholder' else ''))
            if node['kind'] in ('paragraph', 'entry'):
                out.append(' ')
            walk(node['local_id'])
    walk(None)
    return ''.join(out)


def deadline():
    return time.monotonic() + 30


def check_common(test, snapshot):
    validate_snapshot(snapshot)
    test.assertFalse({f['key'] for f in snapshot['facts']} & SG_KEYS)
    test.assertEqual(len([p for p in snapshot['provenance'] if p['role'] == 'selected']), 1)


OPEN5E = {'key': 'tst_grave-wight', 'name': 'Grave Wight', 'document': {'key': 'tst', 'name': 'Test Doc', 'display_name': 'Test Doc',
          'publisher': {'name': 'Pub'}, 'gamesystem': {'name': '5th Edition 2014'}}, 'type': {'name': 'Undead'}, 'size': {'name': 'Medium'},
          'challenge_rating': 0.25, 'experience_points': 50, 'proficiency_bonus': None, 'alignment': 'neutral evil',
          'speed': {'walk': 30, 'fly': 40, 'hover': True, 'unit': 'feet'}, 'languages': {'as_string': 'Common'},
          'armor_class': 14, 'armor_detail': 'studded', 'hit_points': 45, 'hit_dice': '6d8', 'initiative_bonus': 2,
          'ability_scores': {'strength': 15, 'dexterity': 14, 'constitution': 16, 'intelligence': 10, 'wisdom': 13, 'charisma': 15},
          'modifiers': {'strength': 2, 'dexterity': 2, 'constitution': 3, 'intelligence': 0, 'wisdom': 1, 'charisma': 2},
          'saving_throws': {'wisdom': 3}, 'skill_bonuses': {'perception': 3}, 'passive_perception': 13, 'darkvision_range': 60,
          'resistances_and_immunities': {'damage_resistances_display': 'necrotic'},
          'traits': [{'name': 'Sunlight Sensitivity', 'desc': 'The grave wight **burns**:\n\n* in sun\n* in _light_\n\n| A | B |\n|---|---|\n| 1 | 2 |'}],
          'actions': [{'name': 'Drain', 'desc': '<b>Hit</b>: the grave wight drains.', 'action_type': 'ACTION', 'order_in_statblock': 1,
                       'usage_limits': {'type': 'RECHARGE_ON_ROLL', 'param': 5}, 'legendary_action_cost': 1, 'limited_to_form': None},
                      {'name': 'Slam', 'desc': 'Slam.', 'action_type': 'ACTION', 'order_in_statblock': 0, 'usage_limits': None},
                      {'name': 'Rise', 'desc': 'Rises.', 'action_type': 'LEGENDARY_ACTION', 'order_in_statblock': 0, 'legendary_action_cost': 2}],
          'environments': [{'name': 'Grave'}], 'newField': 1}


class Open5eTests(unittest.TestCase):
    def fetch(self, record=OPEN5E, document=None):
        calls = []
        def fetch(url, deadline):
            calls.append(url)
            if '/documents/' in url:
                if document is None:
                    raise SourceError('not_found')
                return json.dumps(document).encode()
            return json.dumps(record).encode()
        fetch.calls = calls
        return fetch

    def test_conversion(self):
        snapshot, measurements = prepare_open5e('tst_grave-wight', fetch=self.fetch(), deadline=deadline())
        check_common(self, snapshot)
        facts = {f['key']: f['display_text'] for f in snapshot['facts']}
        self.assertEqual(facts['speed'], '30 ft., fly 40 ft. (hover)')
        self.assertEqual(facts['challenge'], '1/4 (XP 50)')
        self.assertEqual(facts['saving_throws'], 'Wis +3')
        labels = [n.get('label') for n in snapshot['nodes'] if n['kind'] in ('section', 'entry')]
        self.assertEqual(labels, ['Traits', 'Sunlight Sensitivity', 'Actions', 'Slam', 'Drain (Recharge 5–6)', 'Legendary Actions',
                                  'Rise (Costs 2 Actions)'])
        kinds = {n['kind'] for n in snapshot['nodes']}
        self.assertTrue({'list', 'table', 'strong', 'emphasis', 'species_placeholder'} <= kinds)
        self.assertIn('The [SPECIES] burns', text_of(snapshot))
        self.assertIn('Hit: the [SPECIES] drains.', text_of(snapshot))
        codes = [w['code'] for w in snapshot['warnings']]
        self.assertEqual(sorted(codes), ['html_removed', 'license_unavailable', 'unrecognized_property'])
        self.assertEqual(snapshot['completeness'], 'available')
        self.assertEqual(snapshot['provenance'][0]['edition'], '5th Edition 2014')

    def test_licence_from_document(self):
        document = {'key': 'tst', 'licenses': [{'name': 'CC-BY-4.0', 'url': 'https://creativecommons.org/licenses/by/4.0/'}]}
        snapshot, _ = prepare_open5e('tst_grave-wight', fetch=self.fetch(document=document), deadline=deadline())
        credit = snapshot['provenance'][0]['credits'][0]
        self.assertEqual((credit['license_name'], credit['publisher']), ('CC-BY-4.0', 'Pub'))
        self.assertNotIn('license_unavailable', [w['code'] for w in snapshot['warnings']])

    def test_identity_and_failures(self):
        for key in ('', '../x', 'a b'):
            with self.assertRaises(SourceError):
                prepare_open5e(key, fetch=self.fetch(), deadline=deadline())
        with self.assertRaises(SourceError) as caught:
            prepare_open5e('other', fetch=self.fetch(), deadline=deadline())
        self.assertEqual(caught.exception.code, 'identity_mismatch')
        with self.assertRaises(SourceError) as caught:
            prepare_open5e('tst_grave-wight', fetch=self.fetch(), deadline=time.monotonic() - 1)
        self.assertEqual(caught.exception.code, 'deadline')

    def test_discovery_matches_apostrophes(self):
        listing = {'results': [{'key': 'a_wisp', 'name': 'Will-o’-Wisp', 'document': {'name': 'A'}}, {'key': 'b', 'name': 'Wisp'}], 'next': None}
        found = discover_open5e("Will-o'-Wisp", fetch=lambda url, deadline: json.dumps(listing).encode(), deadline=deadline())
        self.assertEqual([c['key'] for c in found], ['a_wisp'])
        self.assertEqual(name_key('Will-o’-Wisp'), name_key("will-o'-wisp"))


DDB_PAGE = '''<html><body><script>var x = "<div class='mon-stat-block'>";</script>
<div class="mon-stat-block"><div class="mon-stat-block__name"><a class="mon-stat-block__name-link" href="/monsters/123-grave-wight">Grave Wight</a></div>
<div class="mon-stat-block__meta">Medium Undead, Neutral Evil</div>
<div class="mon-stat-block__attribute"><span class="mon-stat-block__attribute-label">Armor Class</span><span class="mon-stat-block__attribute-value"><span class="mon-stat-block__attribute-data-value">14</span></span></div>
<div class="mon-stat-block__attribute"><span class="mon-stat-block__attribute-label">Speed</span><span class="mon-stat-block__attribute-data-value">30 ft.</span></div>
<div class="ability-block__stat"><div class="ability-block__heading">STR</div><span class="ability-block__score">15</span><span class="ability-block__modifier">(+2)</span></div>
<div class="mon-stat-block__tidbit"><span class="mon-stat-block__tidbit-label">Senses</span><span class="mon-stat-block__tidbit-data">Darkvision 60 ft.</span></div>
<div class="mon-stat-block__description-block"><div class="mon-stat-block__description-block-heading">Actions</div>
<div class="mon-stat-block__description-block-content"><p><em><strong>Drain.</strong></em> The grave wight casts <a class="spell-tooltip" href="/spells/1-chill">chill</a> or <a href="javascript:alert(1)">bad</a>.</p>
<ul><li>one</li></ul><img src="https://x/y.png"></div></div></div>
<div class="more-info-content"><h3>Lair Actions</h3><p>The lair stirs.</p></div>
<footer><p class="tags environment-tags">Habitat: <span>Graves</span></p><p class="source">Test Book, pg. 1</p></footer></body></html>'''


class DndBeyondTests(unittest.TestCase):
    def test_conversion(self):
        snapshot, _ = prepare_dndbeyond('/monsters/123-grave-wight', fetch=lambda url, deadline: DDB_PAGE.encode(), deadline=deadline())
        check_common(self, snapshot)
        facts = {f['label']: f['display_text'] for f in snapshot['facts']}
        self.assertEqual(facts['Speed'], '30 ft.')
        self.assertEqual(facts['STR'], '15 (+2)')
        self.assertEqual((facts['Habitat'], facts['Source']), ('Graves', 'Test Book, pg. 1'))
        self.assertNotIn('Armor Class', facts)
        links = [n['url'] for n in snapshot['nodes'] if n['kind'] == 'link']
        self.assertEqual(links, ['https://www.dndbeyond.com/spells/1-chill'])
        text = text_of(snapshot)
        self.assertIn('The [SPECIES] casts chill or bad.', text)
        self.assertIn('The lair stirs.', text)
        self.assertIn('media_omitted', [w['code'] for w in snapshot['warnings']])
        self.assertEqual(snapshot['provenance'][0]['entity_id'], 'monster|123')

    def test_gated_mismatched_and_invalid(self):
        for page, code in (('<html><p>Sign in</p></html>', 'statblock_unavailable'), (DDB_PAGE.replace('123-grave', '999-grave'), 'identity_mismatch')):
            with self.assertRaises(SourceError) as caught:
                prepare_dndbeyond('/monsters/123-grave-wight', fetch=lambda url, deadline, p=page: p.encode(), deadline=deadline())
            self.assertEqual(caught.exception.code, code)
        for path in ('/spells/1-chill', 'https://evil.example/monsters/1', '/monsters/abc'):
            with self.assertRaises(SourceError):
                canonical_url(path)

    def test_discovery(self):
        page = '<a href="/monsters/1-lich">Lich</a><a href="/monsters/2-lich-lord">Lich Lord</a><a href="/monsters/1-lich">Lich</a>'
        found = discover_dndbeyond('lich', fetch=lambda url, deadline: page.encode(), deadline=deadline())
        self.assertEqual([c['path'] for c in found], ['/monsters/1-lich'])


MONSTER = {'name': 'Grave Wight', 'size': 'medium', 'type': 'undead', 'tag': 'Ash', 'alignment': 'neutral evil', 'cr': '5',
           'customProf': 2, 'strPoints': '16', 'dexPoints': '14', 'conPoints': '10', 'intPoints': '10', 'wisPoints': '12', 'chaPoints': '8',
           'speed': '30', 'flySpeed': '40', 'hover': True, 'darkvision': '60', 'hpText': '99 (secret)', 'otherArmorDesc': '18 plate',
           'abilities': [{'name': 'Grim', 'desc': '[MON] hits for [STR ATK] and [2d6+3] or [1d8 + 2] (DC [CON SAVE]); [BOGUS] _sly_ **bold'}],
           'actions': [{'name': 'Slam', 'desc': 'Line one\nLine two'}], 'legendaries': [{'name': 'Rise', 'desc': 'It rises.'}],
           'isLegendary': False, 'legendariesDescription': 'The monster can take 3 legendary actions.',
           'isLair': True, 'lairDescription': 'In its lair:', 'lairs': [{'name': 'Chill', 'desc': 'Cold.'}], 'lairDescriptionEnd': 'Done.',
           'sthrows': [{'name': 'wis', 'order': 4}], 'skills': [{'name': 'perception', 'stat': 'wis', 'note': ' (ex)'}],
           'damagetypes': [{'name': 'cold', 'type': 'i'}, {'name': 'fire', 'type': 'r'}],
           'specialdamage': [{'name': 'nonmagical attacks', 'type': 'r'}], 'conditions': [{'name': 'Charmed'}],
           'languages': [{'name': 'Common', 'speaks': True}, {'name': 'Elvish', 'speaks': False}], 'telepathy': 60}


class TetraCubeTests(unittest.TestCase):
    def prepare(self, data=MONSTER, **kwargs):
        return prepare_monster_file(json.dumps(data).encode(), filename='wight.monster', **kwargs)[0]

    def test_conversion(self):
        snapshot = self.prepare()
        check_common(self, snapshot)
        facts = {f['key']: f['display_text'] for f in snapshot['facts']}
        self.assertEqual(snapshot['subtitle'], 'Medium undead (Ash), neutral evil')
        self.assertEqual(facts['speed'], '30 ft., fly 40 ft. (hover)')
        self.assertEqual(facts['skills'], 'Perception +7')
        self.assertEqual(facts['senses'], 'darkvision 60 ft., passive Perception 17')
        self.assertEqual(facts['damage_resistances'], 'fire; nonmagical attacks')
        self.assertEqual(facts['languages'], 'Common, understands Elvish, telepathy 60 ft.')
        self.assertEqual(facts['challenge'], '5 (1,800 XP)')
        text = text_of(snapshot)
        self.assertIn('[SPECIES] hits for +6 and 10 (2d6 + 3) or 6 (1d8 + 2) (DC 11); [BOGUS] sly bold', text)
        self.assertIn('Line one Line two', text)
        self.assertNotIn('99', text + json.dumps(snapshot['facts']))
        sections = [(n['label'], n.get('enabled')) for n in snapshot['nodes'] if n['kind'] == 'section']
        self.assertEqual(sections, [('Traits', None), ('Actions', None), ('Legendary Actions (disabled)', False), ('Lair Actions', True)])
        self.assertIn('In its lair:', text)
        self.assertNotIn('legendary actions.', text)
        self.assertEqual([w['code'] for w in snapshot['warnings']], ['unresolved_placeholder'])
        provenance = snapshot['provenance'][0]
        self.assertEqual((provenance['provider'], provenance['file_name']), ('file', 'wight.monster'))
        self.assertTrue(provenance['entity_id'].startswith('file|sha256:'))

    def test_rejections(self):
        for raw, code in ((b'not json', 'malformed_file'), (b'[]', 'malformed_file'), (json.dumps({'name': 'x', 'actions': {}}).encode(), 'malformed_file'),
                          (b' ' * (5 * 1024 * 1024 + 1), 'file_too_large')):
            with self.assertRaises(SourceError) as caught:
                prepare_monster_file(raw)
            self.assertEqual(caught.exception.code, code)


class FetcherTests(unittest.TestCase):
    def test_host_allowlist_and_size(self):
        class Opener:
            def __init__(self, data, final=None):
                self.data, self.final = data, final
            def __call__(self, redirects):
                return self
            def open(self, request, timeout):
                response = io.BytesIO(self.data)
                response.geturl = lambda: self.final or request.full_url
                response.headers = {}
                return response
        fetch = ProviderFetcher({'api.open5e.com'}, response_bytes=4, opener_factory=Opener(b'1234'))
        self.assertEqual(fetch('https://api.open5e.com/v2/x', deadline=deadline()), b'1234')
        for url, opener, code in (('http://api.open5e.com/x', Opener(b''), 'unsafe_url'), ('https://evil.example/x', Opener(b''), 'unsafe_url'),
                                  ('https://api.open5e.com/x', Opener(b'12345'), 'response_bytes_limit'),
                                  ('https://api.open5e.com/x', Opener(b'1', 'https://evil.example/'), 'unsafe_redirect')):
            with self.assertRaises(SourceError) as caught:
                ProviderFetcher({'api.open5e.com'}, response_bytes=4, opener_factory=opener)(url, deadline=deadline())
            self.assertEqual(caught.exception.code, code)

    def test_markdown_entries(self):
        self.assertEqual(markdown_entries('a\n* b\n- c\n\n> d'), ['a', {'type': 'list', 'items': ['b', 'c']}, 'd'])


@unittest.skipUnless(EXAMPLES.is_dir(), 'captured monsters_examples evidence not present')
class CapturedEvidenceTests(unittest.TestCase):
    def test_every_captured_open5e_record(self):
        records = {json.loads(Path(f).read_bytes())['key']: Path(f).read_bytes() for f in glob.glob(str(EXAMPLES / '*/0*-open5e.json'))}
        fetch = lambda url, deadline: records[url.split('/creatures/')[1].split('/')[0]] if '/creatures/' in url else (_ for _ in ()).throw(SourceError('not_found'))
        for key in records:
            with self.subTest(key=key):
                snapshot, _ = prepare_open5e(key, fetch=fetch, deadline=deadline())
                check_common(self, snapshot)

    def test_every_captured_dndbeyond_page(self):
        pages, available, unavailable = {}, 0, 0
        for manifest in glob.glob(str(EXAMPLES / '*/manifest.json')):
            for request in json.loads(Path(manifest).read_text(encoding='utf-8'))['requests']:
                if request['label'].startswith('dndbeyond-detail') and request.get('file'):
                    pages[request['url']] = Path(manifest).parent / request['file']
        for url, path in pages.items():
            with self.subTest(url=url):
                # Discovery's public check agrees with preparation for every captured page.
                public = public_statblock(url, fetch=lambda u, deadline, p=path: p.read_bytes(), deadline=deadline())
                try:
                    snapshot, _ = prepare_dndbeyond(url, fetch=lambda u, deadline, p=path: p.read_bytes(), deadline=deadline())
                except SourceError as exc:
                    self.assertEqual(exc.code, 'statblock_unavailable')
                    self.assertFalse(public)
                    unavailable += 1
                    continue
                self.assertTrue(public)
                check_common(self, snapshot)
                available += 1
        self.assertGreater(available, 0)
        self.assertGreater(unavailable, 0)

    def test_captured_document_licences(self):
        documents = {Path(f).stem: Path(f).read_bytes() for f in glob.glob(str(EXAMPLES / 'open5e-documents/*.json'))}
        record = json.loads(next(Path(f).read_bytes() for f in glob.glob(str(EXAMPLES / 'lich/0*-open5e.json'))
                                 if json.loads(Path(f).read_bytes())['document']['key'] == 'srd-2014'))
        def fetch(url, deadline):
            if '/documents/' in url:
                return documents[url.split('/documents/')[1].split('/')[0]]
            return json.dumps(record).encode()
        snapshot, _ = prepare_open5e(record['key'], fetch=fetch, deadline=deadline())
        credits = snapshot['provenance'][0]['credits']
        self.assertEqual([c['license_name'] for c in credits], ['Creative Commons Attribution 4.0', 'OPEN GAME LICENSE Version 1.0a'])
        self.assertEqual(credits[0]['publisher'], 'Wizards of the Coast')
        self.assertTrue(credits[0]['attribution'].startswith('5e 2014 Rules by Mike Mearls'))
        self.assertNotIn('license_unavailable', [w['code'] for w in snapshot['warnings']])

    def test_every_captured_monster_file(self):
        for path in sorted(glob.glob(str(EXAMPLES / 'tetra-cube/*.monster'))):
            with self.subTest(path=Path(path).name):
                snapshot, _ = prepare_monster_file(Path(path).read_bytes(), filename=Path(path).name)
                check_common(self, snapshot)


if __name__ == '__main__':
    unittest.main()
