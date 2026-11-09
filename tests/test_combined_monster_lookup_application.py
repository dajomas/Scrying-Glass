"""Secured ASGI/SQLite checks with synthetic Goblin data and mocked provider transport.

Real candidate/stat/initiative parsing, signing, creation and Refresh paths are used.
Sessions are pre-seeded; HP generation is mocked. No live provider, password login,
TCP server, browser-to-server or new-process restart verification is claimed.
"""
import copy
import unittest
from unittest.mock import Mock, patch
import test_source_bonus_offer_acceptance as creation
import test_monster_refresh_review as reviews
from python import scrying_glass_monster_selection as selection
from python import scrying_glass_dndbeyond as dnd
from python import scrying_glass_source_bonus_offer as offers
from python.scrying_glass_monster_refresh_review import install_monster_refresh
from python.scrying_glass_monster_source_snapshot import FIELDS
from python.scrying_glass_storage import SQLiteStorage


class CombinedLookupApplicationTests(unittest.IsolatedAsyncioTestCase):
    request = creation.SourceBonusOfferAcceptanceTests.request
    form = creation.SourceBonusOfferAcceptanceTests.form
    snapshot = creation.SourceBonusOfferAcceptanceTests.snapshot
    json_request = reviews.MonsterRefreshReviewTests.json_request

    def setUp(self):
        creation.SourceBonusOfferAcceptanceTests.setUp(self)
        install_monster_refresh(self.context, self.app)
        c = self.context
        c.CONFIG['display'].update(dndbeyond_image_lookup=True,
            fivetools_fallback=True, fivetools_sources=['XMM'])
        c.dnd_monster_candidates = Mock(return_value=[(True, '/monsters/old-goblin')])
        c.dnd_monster_detail_html = Mock(return_value=
            '<div class="mon-stat-block">AC 12 Initiative +2 (12) HP 7'
            '<span class="mon-stat-block__attribute-label">Armor Class</span>'
            '<span class="mon-stat-block__attribute-data-value">12</span>'
            '<span class="mon-stat-block__attribute-label">Hit Points</span>'
            '<span class="mon-stat-block__attribute-data-value">7</span>'
            '<span class="mon-stat-block__attribute-label">Speed</span></div>')
        c.dnd_monster_stats_from_html = dnd.dnd_monster_stats_from_html
        c.hp_value_factory = Mock(side_effect=lambda start, end: lambda: int(start))
        self.source = dict(name='Goblin', source='XMM', ac=[16], hp={'average': 10},
                           dex=16, cr='10', initiative={'proficiency': 1})
        def load(url):
            if url.endswith('/index.json'):
                return {'XMM': 'bestiary-xmm.json'}
            if url.endswith('/bestiary-xmm.json'):
                return {'monster': [copy.deepcopy(self.source)]}
            raise AssertionError('Unexpected provider URL: '+url)
        patcher = patch.object(selection.ft, 'load_json', side_effect=load)
        self.json_fetch = patcher.start()
        self.addCleanup(patcher.stop)

    async def lookup_combined(self):
        status, result = await self.request('GET', '/api/monsters/lookup', query='species=Goblin')
        self.assertEqual((status, result['status']), (200, 'ok'))
        return result['candidates']

    async def create_from(self, candidate):
        fields = dict(self.form(candidate), ac=str(candidate['ac']), hprangestart=candidate['hp'])
        status, created = await self.request('POST', '/api/monsters', fields=fields)
        self.assertEqual(status, 200)
        return created[0]

    def reopen(self):
        self.context.STORAGE.close()
        self.context.STORAGE = SQLiteStorage(self.directory/'scrying-glass.sqlite3')
        self.context.load_state()
        return self.context.STATE['monsters']

    async def test_both_selected_sources_survive_creation_and_storage_reopen(self):
        before = self.snapshot()
        candidates = await self.lookup_combined()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual([item['provider'] for item in candidates], ['D&D Beyond', '5e.tools'])
        self.assertEqual([item['legacy'] for item in candidates], [True, False])
        self.assertEqual([item['initiative_bonus'] for item in candidates], [2, 7])
        expected = {}
        for candidate in candidates:
            created = await self.create_from(candidate)
            expected[created['id']] = (candidate['source_url'], candidate['initiative_bonus'],
                                        candidate['ac'], int(candidate['hp']))
        for item in self.reopen():
            self.assertEqual((item['monster_source_url'], item['initiative_bonus'], item['ac'], item['hp']), expected[item['id']])
            self.assertEqual(item['initiative_bonus_origin'], 'source')
            self.assertIsNone(item['initiative_roll'])
            self.assertIsNone(item['initiative'])

    async def test_either_provider_failure_blocks_candidates_signing_and_mutation(self):
        for failing in ('dnd', 'fivetools'):
            self.context.dnd_monster_candidates.side_effect = TimeoutError('secret D&D endpoint') if failing == 'dnd' else None
            if failing == 'fivetools':
                self.json_fetch.side_effect = OSError('secret 5e.tools endpoint')
            self.json_fetch.reset_mock()
            self.context.dnd_monster_candidates.reset_mock()
            before = self.snapshot()
            with patch.object(selection, 'issue_token') as sign, patch.object(offers, 'issue_bonus_offer') as bonus:
                status, result = await self.request('GET', '/api/monsters/lookup', query='species=Goblin')
            self.assertEqual((status, result['status'], result['candidates']), (200, 'error', []))
            self.assertNotIn('secret', repr(result))
            sign.assert_not_called()
            bonus.assert_not_called()
            self.json_fetch.assert_called()
            self.context.dnd_monster_candidates.assert_called_once_with('Goblin')
            self.assertEqual(self.snapshot(), before)
        self.context.hp_value_factory.assert_not_called()
        self.context.make_monster.assert_not_called()

    async def test_refresh_choice_apply_retains_identity_raw_roll_and_unselected_state(self):
        candidates = await self.lookup_combined()
        first = await self.create_from(candidates[0])
        await self.create_from(candidates[1])
        c = self.context
        item = c.STATE['monsters'][0]
        for field in FIELDS:
            item.pop(field, None)
        item.update(initiative_bonus=1, initiative_bonus_origin='manual', initiative_roll=16, initiative=17)
        await c.combatants_changed(monsters=True)
        c.hp_value_factory.reset_mock()
        before = self.snapshot()
        status, review = await self.json_request('/api/monsters/refresh/preview', {'ids': [first['id']]})
        self.assertEqual(status, 200)
        row = review['rows'][0]
        self.assertEqual(row['status'], 'selection_required')
        self.assertEqual(len(row['candidates']), 2)
        self.assertEqual(self.snapshot(), before)
        selected = next(candidate for candidate in row['candidates'] if candidate['provider'] == '5e.tools')
        status, resolved = await self.json_request('/api/monsters/refresh/preview',
            {'review_id': review['review_id'], 'choices': {first['id']: selected['selection_token']}})
        self.assertEqual(status, 200)
        self.assertEqual(resolved['rows'][0]['source_fields']['monster_source_book'], 'XMM')
        self.assertTrue(all(not field['checked'] for field in resolved['rows'][0]['fields'].values()))
        self.assertEqual(self.snapshot(), before)
        c.hp_value_factory.assert_not_called()
        status, _ = await self.json_request('/api/monsters/refresh/apply',
            {'review_id': resolved['review_id'], 'selected': {first['id']: ['initiative_bonus', 'ac']}})
        self.assertEqual(status, 200)
        self.assertEqual(c.STATE['monsters'][1], before[0]['monsters'][1])
        restored = next(item for item in self.reopen() if item['id'] == first['id'])
        self.assertEqual((restored['initiative_bonus'], restored['initiative_roll'], restored['initiative']), (7, 16, 23))
        self.assertEqual(restored['initiative_bonus_origin'], 'source')
        self.assertEqual(restored['monster_source_url'], selected['source_url'])
        self.assertEqual((restored['monster_source_book'], restored['ac']), ('XMM', 16))
        self.assertEqual((restored['hp'], restored['max_hp']),
            (before[0]['monsters'][0]['hp'], before[0]['monsters'][0]['max_hp']))
        c.dnd_monster_candidates.reset_mock()
        c.dnd_monster_candidates.side_effect = AssertionError('Retained 5e.tools identity must not search D&D')
        status, retained = await self.json_request('/api/monsters/refresh/preview', {'ids': [first['id']]})
        self.assertEqual(status, 200)
        self.assertEqual(retained['rows'][0]['status'], 'resolved')
        self.assertEqual(retained['rows'][0]['source_fields']['monster_source_url'], selected['source_url'])
        c.dnd_monster_candidates.assert_not_called()
        c.hp_value_factory.assert_not_called()

    async def test_disabled_providers_and_empty_source_list_make_no_disabled_requests(self):
        for dnd_enabled, ft_enabled, sources, expected in (
            (False, True, ['XMM'], ['5e.tools']),
            (True, False, ['XMM'], ['D&D Beyond']),
            (False, False, ['XMM'], []),
            (True, True, [], ['D&D Beyond'])):
            self.context.CONFIG['display'].update(dndbeyond_image_lookup=dnd_enabled,
                fivetools_fallback=ft_enabled, fivetools_sources=sources)
            self.context.dnd_monster_candidates.reset_mock()
            self.json_fetch.reset_mock()
            candidates = await self.lookup_combined()
            self.assertEqual([item['provider'] for item in candidates], expected)
            self.assertEqual(self.context.dnd_monster_candidates.call_count, int(dnd_enabled))
            if not ft_enabled or not sources:
                self.json_fetch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
