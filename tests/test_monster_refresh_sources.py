"""Read-only source-resolution tests with mocked provider boundaries; no HTTP/apply acceptance."""
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from python import scrying_glass_monster_selection as selection
from python.scrying_glass_monster_refresh_sources import resolve_selected_sources, proposed_fields


class MonsterRefreshSourceTests(unittest.TestCase):
    def setUp(self):
        self.context = SimpleNamespace(CONFIG={'display': {}},
            dnd_monster_detail_html=Mock(return_value='<div class="mon-stat-block">AC 15 Initiative +12 (22) HP 10</div>'),
            dnd_monster_stats_from_html=Mock(return_value=(15, '3d8+3', 'dice')))
        self.monster = dict(id='m', name='Goblin', monster_species='Goblin', ac=12, hp=4,
            max_hp=7, initiative_bonus=2, initiative_bonus_origin='manual',
            monster_source_provider='D&D Beyond',
            monster_source_url='https://www.dndbeyond.com/monsters/original',
            monster_source_name='Goblin', monster_source_legacy=True)

    def test_retained_dnd_url_is_fetched_without_search_or_fallback_or_mutation(self):
        roster = [self.monster, dict(self.monster, id='unselected')]
        before = copy.deepcopy(roster)
        with patch.object(selection, 'lookup_candidates') as lookup, patch.object(selection, 'fivetools_candidates') as fallback:
            rows = resolve_selected_sources(self.context, roster, ['m'])
        lookup.assert_not_called()
        fallback.assert_not_called()
        self.context.dnd_monster_detail_html.assert_called_once_with('/monsters/original')
        self.assertEqual(roster, before)
        self.assertEqual([row['id'] for row in rows], ['m'])
        self.assertEqual(rows[0]['fields']['initiative_bonus']['proposed'], 12)
        self.assertEqual(rows[0]['fields']['hp']['proposed'], '3d8+3')
        self.assertTrue(all(not field['checked'] for field in rows[0]['fields'].values()))
        self.assertEqual(rows[0]['source_fields']['monster_source_legacy'], True)

    def test_retained_failure_never_uses_alternate_candidate(self):
        self.context.dnd_monster_detail_html.side_effect = OSError('secret')
        with patch.object(selection, 'lookup_candidates') as lookup:
            row = resolve_selected_sources(self.context, [self.monster], ['m'])[0]
        lookup.assert_not_called()
        self.assertEqual(row['status'], 'failed')
        self.assertNotIn('secret', row['reason'])
        self.assertTrue(all(not field['enabled'] for field in row['fields'].values()))

    def test_missing_and_invalid_fields_are_independent_and_do_not_default_bonus(self):
        fields = proposed_fields(self.monster, dict(ac=0, hp='10', hp_source='average'))
        self.assertEqual(fields['initiative_bonus']['status'], 'missing')
        self.assertIsNone(fields['initiative_bonus']['proposed'])
        self.assertTrue(fields['ac']['enabled'])
        self.assertEqual(fields['ac']['proposed'], 0)
        fields = proposed_fields(self.monster, dict(ac=True, hp='2d8-99',
            initiative_bonus=True, initiative_bonus_status='available'))
        self.assertTrue(all(not field['enabled'] for field in fields.values()))

    def test_fivetools_requires_exact_book_edition_identity(self):
        monster = dict(self.monster, monster_source_provider='5e.tools',
            monster_source_url='https://5e.tools/bestiary.html#goblin_mm',
            monster_source_book='MM', monster_source_legacy=True)
        original = dict(name='Goblin', provider='5e.tools', source='MM', legacy=True,
            source_url=monster['monster_source_url'], ac=12, hp='7', hp_source='average')
        other = dict(original, source='XMM', legacy=False,
            source_url='https://5e.tools/bestiary.html#goblin_xmm', ac=19)
        with patch.object(selection, 'fivetools_candidates', return_value=[other, original]):
            row = resolve_selected_sources(self.context, [monster], ['m'])[0]
        self.assertEqual(row['fields']['ac']['proposed'], 12)
        with patch.object(selection, 'fivetools_candidates', return_value=[other]):
            self.assertEqual(resolve_selected_sources(self.context, [monster], ['m'])[0]['status'], 'failed')

    def test_identityless_single_result_requires_explicit_choice(self):
        monster = {key: value for key, value in self.monster.items() if not key.startswith('monster_source_')}
        candidate = dict(species='Goblin', name='Goblin', provider='D&D Beyond', legacy=False,
            source_url='https://www.dndbeyond.com/monsters/chosen')
        candidate['selection_token'] = selection.issue_token(candidate)
        with patch.object(selection, 'lookup_candidates', return_value={'status': 'ok', 'candidates': [candidate]}):
            row = resolve_selected_sources(self.context, [monster], ['m'])[0]
        self.assertEqual(row['status'], 'selection_required')
        self.context.dnd_monster_detail_html.assert_not_called()
        row = resolve_selected_sources(self.context, [monster], ['m'],
            choices={'m': candidate['selection_token']})[0]
        self.assertEqual(row['status'], 'resolved')
        self.context.dnd_monster_detail_html.assert_called_once_with('/monsters/chosen')

    def test_invalid_signed_choice_does_not_fetch_and_other_rows_are_preserved(self):
        other = dict(self.monster, id='n')
        choices = {'m': 'invalid'}
        before = copy.deepcopy(choices)
        rows = resolve_selected_sources(self.context, [self.monster, other], ['m', 'n'], choices=choices)
        self.assertEqual([row['status'] for row in rows], ['invalid_choice', 'resolved'])
        self.assertEqual(choices, before)
        self.context.dnd_monster_detail_html.assert_called_once_with('/monsters/original')

    def test_bad_selection_rejected_before_provider_calls(self):
        for ids, choices in ((['missing'], None), (['m', 'm'], None), (['m'], {'other': 'token'})):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                resolve_selected_sources(self.context, [self.monster], ids, choices=choices)
        self.assertEqual(resolve_selected_sources(self.context, [self.monster], []), [])
        self.context.dnd_monster_detail_html.assert_not_called()

    def test_disabled_provider_and_oversized_hp_do_not_create_proposals(self):
        self.context.CONFIG['display']['dndbeyond_image_lookup'] = False
        row = resolve_selected_sources(self.context, [self.monster], ['m'])[0]
        self.assertEqual(row['status'], 'failed')
        self.context.dnd_monster_detail_html.assert_not_called()
        for hp in (str(2**63), '9999999999999999999d9999999999999999999', 'bad'):
            fields = proposed_fields(self.monster, dict(hp=hp, ac=12))
            self.assertFalse(fields['hp']['enabled'])
            self.assertTrue(fields['ac']['enabled'])


if __name__ == '__main__':
    unittest.main()
