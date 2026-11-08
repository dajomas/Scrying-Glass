"""Candidate plumbing fixtures; not live provider, HTTP or storage acceptance."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from python import scrying_glass_monster_selection as selection


def markup(value):
    return '<div class="mon-stat-block">AC 15 Initiative '+value+' (12) HP 10</div>'


class DndInitiativeCandidateTests(unittest.TestCase):
    def setUp(self):
        self.context=SimpleNamespace(CONFIG={"display":{"dndbeyond_image_lookup":True,"fivetools_fallback":False}},
            dnd_monster_candidates=Mock(return_value=[(False,"/monsters/example")]),
            dnd_monster_detail_html=Mock(return_value=markup("+2")),
            dnd_monster_stats_from_html=Mock(return_value=(15,"10","average")))

    def test_explicit_signed_and_zero_offers_flow_into_candidates(self):
        for text,expected in (("+12",12),("+0",0),("−2",-2)):
            with self.subTest(text=text):
                self.context.dnd_monster_detail_html.return_value=markup(text)
                with patch.object(selection,"fivetools_candidates") as fallback:
                    result=selection.lookup_candidates(self.context,"Goblin")
                fallback.assert_not_called()
                self.assertEqual(result["status"],"ok")
                candidate=result["candidates"][0]
                self.assertEqual(candidate["initiative_bonus"],expected)
                self.assertEqual(candidate["initiative_bonus_status"],"available")
                self.assertNotIn("initiative_bonus_origin",candidate)
                self.assertIn("selection_token",candidate)

    def test_unavailable_bonus_does_not_trigger_fallback_or_zero(self):
        for html,status in (('<div class="mon-stat-block">AC 15 HP 10</div>',"missing"),
                            (markup("+2.5"),"invalid")):
            self.context.dnd_monster_detail_html.return_value=html
            with patch.object(selection,"fivetools_candidates") as fallback:
                result=selection.lookup_candidates(self.context,"Goblin")
            fallback.assert_not_called()
            self.assertEqual(len(result["candidates"]),1)
            self.assertIsNone(result["candidates"][0]["initiative_bonus"])
            self.assertEqual(result["candidates"][0]["initiative_bonus_status"],status)

    def test_unusable_ac_hp_filter_is_unchanged(self):
        self.context.CONFIG["display"]["fivetools_fallback"]=True
        self.context.dnd_monster_stats_from_html.return_value=(None,None,None)
        with patch.object(selection,"fivetools_candidates",return_value=[]) as fallback:
            result=selection.lookup_candidates(self.context,"Goblin")
        fallback.assert_called_once()
        self.assertEqual(result["candidates"],[])


class DndInitiativeCreationBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_offer_is_not_automatically_assigned_or_promoted_to_source_origin(self):
        from test_manual_monster_bonus_creation import ManualBonusCreationTests
        fixture=ManualBonusCreationTests("test_explicit_manual_bonus_and_unset_roll_total")
        fixture.setUp()
        candidate=dict(species="Goblin",name="Goblin",provider="D&D Beyond",
            source_url="https://www.dndbeyond.com/monsters/example",legacy=False,
            initiative_bonus=12,initiative_bonus_status="available",image_url=None)
        result=await fixture.handler.create_monster(**dict(fixture.arguments,
            monster_species="Goblin",selection_token=selection.issue_token(candidate)))
        self.assertEqual(result[0]["initiative_bonus"],0)
        self.assertEqual(result[0]["initiative_bonus_origin"],"default")
        self.assertIsNone(result[0]["initiative_roll"])
