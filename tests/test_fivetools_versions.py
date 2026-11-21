"""SG-TODO-033: 5e.tools monster versions (DataUtil.monster.getVersions at the pinned runtime).

Synthetic records stand in for the dataset; the full comparison against the pinned
runtime is ``tools/fivetools_oracle`` (368 of 368 versions identical, see handover 720).
"""
import json
import time
import unittest

from python.scrying_glass_fivetools_preparation import PreparationError, prepare_statblock
from python.scrying_glass_fivetools_resolution import DatasetLoader, Identity, Limits
from python.scrying_glass_fivetools_versions import VersionError, resolve_version, version_names, version_specs

BASE = {
    'name': 'Battle Familiar', 'source': 'AU', 'page': 3, 'size': ['M'], 'type': 'celestial', 'ac': [14],
    'hp': {'average': 30, 'formula': '4d8 + 12'}, 'speed': {'walk': 40, 'fly': 30},
    'str': 16, 'dex': 16, 'con': 16, 'int': 6, 'wis': 12, 'cha': 8, 'passive': 11, 'cr': '2',
    'hasToken': True, 'hasFluff': True,
    'otherSources': [{'source': 'AU', 'page': 9}, {'source': 'XMM', 'page': 1}],
    'trait': [{'name': 'Flyby (Flyer Only)', 'entries': ['It flies by.']}, {'name': 'Loyal', 'entries': ['Loyal.']}],
    'action': [{'name': 'Bite', 'entries': ['{@atk mw} {@hit 5} to hit.']}],
    'variant': [{'type': 'variant', 'name': 'Familiar Sentinels', '_version': {'name': 'Battle Familiar Sentinel',
                 'addHeadersAs': 'action'}, 'entries': ['Intro.', {'type': 'entries', 'name': 'Guard', 'entries': ['It guards.']}]}],
    '_versions': [
        {'name': 'Battle Familiar (Flyer)', 'source': 'AU', 'ac': [12],
         '_mod': {'trait': [{'mode': 'renameArr', 'renames': {'rename': 'Flyby (Flyer Only)', 'with': 'Flyby'}}]}},
        {'_abstract': {'name': 'Battle Familiar ({{kind}})', 'source': 'AU',
                       '_mod': {'trait': {'mode': 'appendArr', 'items': {'name': 'Kind', 'entries': ['{{kind}} kind.']}}}},
         '_implementations': [{'_variables': {'kind': 'Fire'}, 'resist': ['fire']}, {'_variables': {'kind': 'Cold'}}]},
    ],
}


def loader(*records):
    return DatasetLoader('d', [(Identity('d', 'monster', r['source'], r['name']), json.dumps(r).encode()) for r in records])


def resolve(record, name, source):
    return resolve_version(loader(record), record, name, source, limits=Limits(), deadline=time.monotonic() + 30,
                           cancelled=lambda: False, clock=time.monotonic, dataset='d')


class SpecTests(unittest.TestCase):
    def test_runtime_order_basic_templates_then_variants(self):
        self.assertEqual(version_names(BASE), [
            ('Battle Familiar (Flyer)', 'AU'), ('Battle Familiar (Fire)', 'AU'), ('Battle Familiar (Cold)', 'AU'),
            ('Battle Familiar Sentinel', 'AU')])

    def test_copy_metadata_as_the_runtime_expands_it(self):
        flyer, fire, _, sentinel = version_specs(BASE)
        self.assertEqual(flyer['_copy'], {'_preserve': {'*': True}, '_mod': BASE['_versions'][0]['_mod']})
        self.assertNotIn('_mod', flyer)
        self.assertEqual(fire['_copy']['_mod']['trait']['items']['entries'], ['Fire kind.'])
        self.assertEqual(fire['resist'], ['fire'])
        self.assertNotIn('_variables', fire)
        self.assertIsNone(sentinel['variant'])
        self.assertEqual(sentinel['_copy']['_mod'], {'action': {'mode': 'appendArr', 'items': [{'name': 'Guard', 'entries': ['It guards.']}]}})

    def test_missing_variable_becomes_undefined_and_malformed_versions_fail(self):
        record = dict(BASE, _versions=[{'_abstract': {'name': 'X {{nope}}', 'source': 'AU'}, '_implementations': [{'_variables': {'a': 1}}]}],
                      variant=[])
        self.assertEqual(version_names(record), [('X undefined', 'AU')])
        for bad in ([{}], ['x'], {'name': 'x'}):
            with self.subTest(bad=bad), self.assertRaises(VersionError):
                version_specs(dict(BASE, _versions=bad, variant=[]))


class ResolveTests(unittest.TestCase):
    def test_version_copies_the_parent_and_applies_its_modifications(self):
        record, provenance = resolve(BASE, 'Battle Familiar (Flyer)', 'AU')
        self.assertEqual(record['ac'], [12])
        self.assertEqual([t['name'] for t in record['trait']], ['Flyby', 'Loyal'])
        self.assertEqual(record['hp'], BASE['hp'])
        for key in ('_versions', 'hasToken', 'hasFluff', '_copy'):
            self.assertNotIn(key, record)
        self.assertEqual(record['otherSources'], [{'source': 'XMM', 'page': 1}])  # its own source is dropped
        self.assertEqual((record['_versionBase_name'], record['_versionBase_source'], record['_versionBase_hash'],
                          record['_versionBase_hasToken'], record['_isCopy']),
                         ('Battle Familiar', 'AU', 'battle%20familiar_au', True, True))
        self.assertEqual([(p.role, p.identity.name) for p in provenance][:1], [('selected', 'Battle Familiar (Flyer)')])

    def test_unknown_version_is_unavailable(self):
        with self.assertRaises(LookupError):
            resolve(BASE, 'Battle Familiar (Brute)', 'AU')


class PreparationTests(unittest.TestCase):
    def fetch(self, path):
        files = {'bestiary/index.json': {'AU': 'bestiary-au.json'}, 'bestiary/bestiary-au.json': {'monster': [BASE]}}
        if path not in files:
            raise LookupError('reference_unavailable')
        return json.dumps(files[path]).encode()

    def prepare(self, name, version_of=None):
        return prepare_statblock(name, 'AU', fetch=self.fetch, deadline=time.monotonic() + 30, version_of=version_of)

    def test_version_with_and_without_its_base(self):
        for version_of in (('Battle Familiar', 'AU'), None):
            with self.subTest(version_of=version_of):
                prepared = self.prepare('Battle Familiar (Fire)', version_of)
                self.assertEqual(prepared.snapshot['source_label'], 'Battle Familiar (Fire)')
                self.assertEqual(prepared.selected.name, 'Battle Familiar (Fire)')
                self.assertIn('Fire kind.', json.dumps(prepared.snapshot))
        self.assertEqual(self.prepare('Battle Familiar').snapshot['source_label'], 'Battle Familiar')

    def test_unknown_names_and_bad_requests(self):
        with self.assertRaises(PreparationError) as caught:
            self.prepare('Battle Familiar (Brute)')
        self.assertEqual(caught.exception.code, 'selected_unavailable')
        for bad in (('Battle Familiar',), ('', 'AU'), 'Battle Familiar|AU'):
            with self.subTest(bad=bad), self.assertRaises(PreparationError):
                self.prepare('Battle Familiar (Fire)', bad)


@unittest.skipUnless(__import__('sys').platform == 'linux' and any(
    __import__('os').path.exists(p) for p in ('/usr/bin/prlimit', '/bin/prlimit')), 'isolated preparation needs Linux prlimit')
class IsolatedWorkerTests(PreparationTests):
    """The same version preparation through the isolated worker (version_of crosses the RPC)."""
    def prepare(self, name, version_of=None):
        import types
        from python.scrying_glass_fivetools_fetch import FetchError
        from python.scrying_glass_fivetools_preparation_worker import prepare_isolated

        def fetch(path, deadline):
            try:
                return PreparationTests.fetch(self, path)
            except LookupError:
                raise FetchError('not_found') from None
        snapshot, _ = prepare_isolated(name, 'AU', fetch=fetch, deadline=time.monotonic() + 30, version_of=version_of)
        return types.SimpleNamespace(snapshot=snapshot, selected=types.SimpleNamespace(name=snapshot['source_label']))

    def test_unknown_names_and_bad_requests(self):
        with self.assertRaises(PreparationError) as caught:
            self.prepare('Battle Familiar (Brute)')
        self.assertEqual(caught.exception.code, 'selected_unavailable')
        for bad in (('Battle Familiar',), 'Battle Familiar|AU', ('Battle Familiar', 3)):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'invalid_worker_input'):
                self.prepare('Battle Familiar (Fire)', bad)


class DiscoveryTests(unittest.TestCase):
    def discover(self, species, monsters=(BASE,)):
        from python.scrying_glass_statblock_discovery import FIVETOOLS, Discovery, ProviderConfig
        files = {'https://5e.tools/data/bestiary/index.json': {'AU': 'bestiary-au.json'},
                 'https://5e.tools/data/bestiary/bestiary-au.json': {'monster': list(monsters)}}
        config = ProviderConfig({FIVETOOLS: True}, 'https://5e.tools/data', ('AU',), None)
        fetch = lambda provider, url, deadline: json.dumps(files[url]).encode()
        return Discovery(config, fetch, time.monotonic() + 30).run(FIVETOOLS, species)

    def test_base_name_offers_the_base_and_every_version(self):
        result = self.discover('battle familiar')
        rows = [(i['name'], i.get('version_of'), s.get('version_of', {}).get('label')) for i, s in result['candidates']]
        base = {'name': 'Battle Familiar', 'source': 'AU'}
        self.assertEqual(rows, [('Battle Familiar', None, None)] + [
            (name, base, 'Battle Familiar') for name, _ in version_names(BASE)])
        self.assertNotIn('omitted_versions', result)
        self.assertEqual(result['candidates'][1][1]['name'], 'Battle Familiar (Flyer)')

    def test_own_name_offers_that_version_only(self):
        result = self.discover('Battle Familiar (Cold)')
        self.assertEqual([(i['name'], i['version_of']['name']) for i, _ in result['candidates']],
                         [('Battle Familiar (Cold)', 'Battle Familiar')])

    def test_malformed_versions_are_counted_not_offered(self):
        result = self.discover('Battle Familiar', [dict(BASE, _versions=[{}])])
        self.assertEqual([i['name'] for i, _ in result['candidates']], ['Battle Familiar'])
        self.assertEqual(result['omitted_versions'], 1)


if __name__ == '__main__':
    unittest.main()
