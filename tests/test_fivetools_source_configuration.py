"""Deterministic source/config tests; provider HTTP is mocked throughout."""
import ast
import copy
import json
import logging
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
import yaml
from python import scrying_glass_fivetools as ft

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ['MM', 'XMM', 'PHB', 'XPHB', 'DMG', 'XDMG']

def extracted(path, names, namespace):
    tree = ast.parse((ROOT / path).read_text(encoding='utf-8'))
    nodes = [n for n in tree.body if getattr(n, 'name', None) in names or
             isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace

class SourceConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.config = extracted('python/scrying_glass_init.py',
            {'DEFAULT_STORAGE_DIR','DEFAULT_CONFIG','merge','load_config'},
            dict(copy=copy, json=json, yaml=yaml, Path=Path, Any=object))
        self.selection = extracted('python/scrying_glass_monster_selection.py',
            {'ProviderError','fivetools_candidates','fivetools_source_attribution'},
            dict(ft=ft, re=re, MAX_CANDIDATES=32, LOG=logging.getLogger(__name__),
                 __name__="python.scrying_glass_monster_selection", __package__="python"))
        self.candidates = self.selection['fivetools_candidates']
        patcher = patch.object(ft, 'urlopen', side_effect=AssertionError('Live network forbidden'))
        network = patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(network.assert_not_called)

    def config_file(self, value, suffix='.json'):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ('config' + suffix)
            path.write_text(json.dumps(value) if suffix == '.json' else yaml.safe_dump(value), encoding='utf-8')
            return self.config['load_config'](path)

    def data(self, url, match_source=None, images=False):
        if url.endswith('/index.json'):
            return {source: source.lower() + '.json' for source in EXPECTED}
        source = url.rsplit('/',1)[1][:-5].upper()
        monster = {'name':'Claw' if match_source is None or source == match_source else 'Other',
                   'source':source, 'ac':[12], 'hp':{'average':7}, 'hasToken':images}
        return {'monster':[monster]}

    def test_shared_default_override_order_and_independence(self):
        self.assertEqual(ft.configured_sources({}), EXPECTED)
        display = {'fivetools_sources':['XPHB','MM','XPHB','Custom']}
        self.assertEqual(ft.configured_sources(display), ['XPHB','MM','Custom'])
        self.assertEqual(display['fivetools_sources'], ['XPHB','MM','XPHB','Custom'])
        defaults = ft.configured_sources({}); defaults.clear()
        self.assertEqual(ft.configured_sources({}), EXPECTED)

    def test_invalid_lists_are_rejected(self):
        for value in [None, 'MM', True, ('MM',), [1], [''], [' MM'], ['MM '], ['MM']*33]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ft.configured_sources({'fivetools_sources':value})

    def test_config_omitted_defaults_and_no_aliasing(self):
        self.assertEqual(self.config_file({})['display']['fivetools_sources'], EXPECTED)
        first = self.config['load_config'](None)
        first['display']['fivetools_sources'].clear()
        self.assertEqual(self.config['load_config'](None)['display']['fivetools_sources'], EXPECTED)
        self.assertEqual(self.config['DEFAULT_CONFIG']['display']['fivetools_sources'], list(ft.DEFAULT_SOURCES))

    def test_json_and_yaml_explicit_override_and_empty(self):
        for suffix in ['.json','.yaml']:
            for sources in [[], ['DMG','XPHB','DMG']]:
                result = self.config_file({'display':{'fivetools_sources':sources}},suffix)
                self.assertEqual(result['display']['fivetools_sources'], list(dict.fromkeys(sources)))
        self.assertEqual(yaml.safe_load((ROOT/'config.example.yaml').read_text())['display']['fivetools_sources'], EXPECTED)

    def test_invalid_configuration_fails_loading(self):
        for display in [None, 'invalid', {'fivetools_sources':None}, {'fivetools_sources':['']}]:
            with self.subTest(display=display):
                with self.assertRaises(ValueError):
                    self.config_file({'display':display})

    def test_legacy_stats_can_reach_each_default_source(self):
        for source in EXPECTED:
            with self.subTest(source=source):
                with patch.object(ft,'load_json',side_effect=lambda url:self.data(url,source)) as get:
                    result = ft.lookup('Claw',{})
                self.assertEqual(result['source'],source)
                self.assertEqual((result['ac'],result['hp']),(12,'7'))
                self.assertIn(source.lower(),result['source_url'])
                self.assertEqual(get.call_count,2+EXPECTED.index(source))

    def test_legacy_image_can_reach_each_default_source(self):
        for source in EXPECTED:
            with self.subTest(source=source):
                with patch.object(ft,'load_json',side_effect=lambda url:self.data(url,source,True)):
                    result = ft.lookup('Claw',{},want_image=True)
                self.assertEqual(result['source'],source)
                self.assertIn('/'+source+'/',result['image_url'])

    def test_candidates_enumerate_six_sources_in_order(self):
        with patch.object(ft,'load_json',side_effect=self.data):
            result = self.candidates('Claw',{})
        self.assertEqual([item['source'] for item in result],EXPECTED)
        self.assertEqual(len({item['source_url'] for item in result}),6)

    def test_empty_list_does_not_even_fetch_index(self):
        display = {'fivetools_sources':[]}
        with patch.object(ft,'load_json') as get:
            self.assertIsNone(ft.lookup('Claw',display))
            self.assertIsNone(ft.lookup('Claw',display,want_image=True))
            self.assertEqual(self.candidates('Claw',display),[])
        get.assert_not_called()

    def test_candidate_explicit_order_and_duplicates(self):
        with patch.object(ft,'load_json',side_effect=self.data) as get:
            result = self.candidates('Claw',{'fivetools_sources':['XPHB','DMG','XPHB']})
        self.assertEqual([item['source'] for item in result],['XPHB','DMG'])
        self.assertEqual(get.call_count,3)

    def test_candidate_errors_are_not_zero_matches(self):
        with patch.object(ft,'load_json',side_effect=OSError('private detail')):
            with self.assertRaises(self.selection['ProviderError']) as error:
                self.candidates('Claw',{})
        self.assertNotIn('private detail',str(error.exception))
        with self.assertRaises(self.selection['ProviderError']):
            self.candidates('Claw',{'fivetools_sources':None})

    def test_legacy_disabled_does_not_fetch(self):
        with patch.object(ft,'load_json') as get:
            self.assertIsNone(ft.lookup('Claw',{'fivetools_fallback':False}))
        get.assert_not_called()

if __name__ == '__main__':
    unittest.main()
