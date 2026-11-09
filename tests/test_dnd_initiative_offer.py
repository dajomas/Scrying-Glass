"""Synthetic provider-markup fixtures; no live provider or entitlement tests."""
import unittest
from python.scrying_glass_dnd_initiative_offer import dnd_initiative_offer


class DndInitiativeOfferTests(unittest.TestCase):
    def block(self, value="+2", score="12"):
        return '<div class="mon-stat-block"><h1>Goblin</h1><div>AC 15 Initiative '+value+' ('+score+')</div><div>HP 10 (3d6)</div><div>Speed 30 ft.</div></div>'

    def test_positive_and_not_the_parenthesized_score(self):
        result=dnd_initiative_offer(self.block("+12","22"))
        self.assertEqual(result["initiative_bonus"],12)
        self.assertEqual(result["initiative_bonus_status"],"available")
        self.assertNotEqual(result["initiative_bonus"],22)

    def test_explicit_zero_is_available_not_missing(self):
        result=dnd_initiative_offer(self.block("+0","10"))
        self.assertEqual(result["initiative_bonus"],0)
        self.assertEqual(result["initiative_bonus_status"],"available")

    def test_ascii_and_unicode_negative(self):
        for value in ("-2","−2"):
            self.assertEqual(dnd_initiative_offer(self.block(value,"8"))["initiative_bonus"],-2)

    def test_nested_spans_entities_and_whitespace(self):
        html='<div class="other mon-stat-block"><span>AC</span> 15 <span>Initiative</span> <b>&#43;2</b> (12)<br><span>HP</span> 10</div>'
        self.assertEqual(dnd_initiative_offer(html)["initiative_bonus"],2)

    def test_dexterity_is_not_used_when_initiative_is_missing(self):
        result=dnd_initiative_offer('<div class="mon-stat-block">AC 15 HP 10 DEX 20 (+5)</div>')
        self.assertIsNone(result["initiative_bonus"])
        self.assertEqual(result["initiative_bonus_status"],"missing")

    def test_lair_actions_do_not_supply_an_initiative_bonus(self):
        result=dnd_initiative_offer('<div class="mon-stat-block">AC 15 HP 10 Actions On initiative count 20 take an action. Initiative +12 (22)</div>')
        self.assertIsNone(result["initiative_bonus"])

    def test_outside_comments_or_other_page_text_are_ignored(self):
        html='<p>AC 15 Initiative +99 (109) HP 100</p><div class="mon-stat-block">AC 15 HP 10</div><div>AC 15 Initiative +88 (98) HP 100</div>'
        self.assertIsNone(dnd_initiative_offer(html)["initiative_bonus"])

    def test_scripts_hidden_and_navigation_do_not_supply_labels(self):
        html='<div class="mon-stat-block"><script>AC 15 Initiative +99 (109) HP</script><nav>AC 15 Initiative +88 (98) HP</nav><span hidden>Initiative +77</span><span aria-hidden="true">Initiative +66</span>AC 15 Initiative +2 (12) HP 10</div>'
        self.assertEqual(dnd_initiative_offer(html)["initiative_bonus"],2)

    def test_multiple_visible_blocks_are_ambiguous(self):
        result=dnd_initiative_offer(self.block()+self.block("+12","22"))
        self.assertEqual(result["initiative_bonus_status"],"ambiguous")
        self.assertIsNone(result["initiative_bonus"])

    def test_hidden_duplicate_block_does_not_make_a_second_offer(self):
        html='<div hidden>'+self.block("+99","109")+'</div>'+self.block()
        self.assertEqual(dnd_initiative_offer(html)["initiative_bonus"],2)

    def test_duplicate_header_labels_are_ambiguous(self):
        result=dnd_initiative_offer('<div class="mon-stat-block">AC 15 Initiative +2 (12) Initiative +12 (22) HP 10</div>')
        self.assertEqual(result["initiative_bonus_status"],"ambiguous")

    def test_malformed_or_unsigned_values_are_not_zero(self):
        for value in ("2","+2.5","+2 advantage","+true","+9223372036854775808"):
            with self.subTest(value=value):
                result=dnd_initiative_offer(self.block(value))
                self.assertEqual(result["initiative_bonus_status"],"invalid")
                self.assertIsNone(result["initiative_bonus"])

    def test_unrecognized_container_is_missing(self):
        self.assertEqual(dnd_initiative_offer('AC 15 Initiative +2 (12) HP 10')["initiative_bonus_status"],"missing")

    def test_invalid_input_is_bounded(self):
        for html in (None,{},"x"*8_000_001):
            self.assertEqual(dnd_initiative_offer(html)["initiative_bonus_status"],"invalid")

    def test_offer_contains_evidence_but_no_assignment_origin(self):
        result=dnd_initiative_offer(self.block())
        self.assertIn('Initiative +2 (12)',result["initiative_bonus_evidence"])
        self.assertNotIn('initiative_bonus_origin',result)

    def test_inline_hidden_duplicate_is_ignored(self):
        for style in ('display: none', 'visibility: hidden !important'):
            html='<div style="'+style+'">'+self.block("+99","109")+'</div>'+self.block()
            self.assertEqual(dnd_initiative_offer(html)["initiative_bonus"],2)
