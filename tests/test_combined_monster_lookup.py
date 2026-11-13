"""Offline orchestration tests; no provider HTTP, application routes or signing."""
import copy
import unittest
from unittest.mock import Mock
from python.scrying_glass_combined_lookup import combined_candidates


def candidate(provider, book, **changes):
    result = dict(provider=provider, source=book, species="Goblin", name="Goblin",
                  ac=12, hp="7", initiative_bonus=2,
                  source_url="https://example.test/" + book)
    result.update(changes)
    return result


class CombinedLookupTests(unittest.TestCase):
    def setUp(self):
        self.old = candidate("D&D Beyond", "2014", legacy=True)
        self.new = candidate("5e.tools", "XMM", ac=16, hp="10", initiative_bonus=7)
        self.dnd = Mock(return_value=[self.old])
        self.ft = Mock(return_value=[self.new])

    def run_lookup(self, **options):
        return combined_candidates(self.dnd, self.ft, **options)

    def test_both_enabled_versions_keep_their_own_statistics_and_identity(self):
        result = self.run_lookup()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["candidates"], [self.old, self.new])
        self.dnd.assert_called_once_with()
        self.ft.assert_called_once_with()
        self.assertEqual([item["count"] for item in result["providers"]], [1, 1])

    def test_all_book_versions_are_retained_without_cross_provider_deduplication(self):
        other = candidate("5e.tools", "MM")
        self.ft.return_value = [other, self.new]
        self.assertEqual(self.run_lookup()["candidates"], [self.old, other, self.new])

    def test_empty_primary_still_searches_secondary(self):
        self.dnd.return_value = []
        self.assertEqual(self.run_lookup()["candidates"], [self.new])
        self.ft.assert_called_once_with()

    def test_disabled_providers_are_never_called(self):
        for dnd_enabled, ft_enabled in ((False, True), (True, False), (False, False)):
            self.dnd.reset_mock()
            self.ft.reset_mock()
            result = self.run_lookup(dnd_enabled=dnd_enabled, fivetools_enabled=ft_enabled)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(self.dnd.call_count, int(dnd_enabled))
            self.assertEqual(self.ft.call_count, int(ft_enabled))
            self.assertEqual(result["candidates"],
                ([self.old] if dnd_enabled else []) + ([self.new] if ft_enabled else []))

    def test_first_failure_does_not_skip_other_enabled_provider(self):
        self.dnd.side_effect = OSError("private endpoint or credentials")
        result = self.run_lookup()
        self.ft.assert_called_once_with()
        self.assertEqual((result["status"], result["candidates"]), ("error", []))
        self.assertIn("D&D Beyond", result["reason"])
        self.assertNotIn("private", repr(result))
        self.assertEqual(result["providers"][1]["status"], "ok")

    def test_secondary_failure_discards_primary_candidates_and_tokens(self):
        self.old["selection_token"] = "must-not-escape"
        self.ft.side_effect = TimeoutError("secret")
        result = self.run_lookup()
        self.assertEqual((result["status"], result["candidates"]), ("error", []))
        self.assertIn("5e.tools", result["reason"])
        self.assertNotIn("must-not-escape", repr(result))
        self.assertNotIn("secret", repr(result))

    def test_both_failures_are_reported_without_exception_details(self):
        self.dnd.side_effect = RuntimeError("secret one")
        self.ft.side_effect = ValueError("secret two")
        result = self.run_lookup()
        self.assertEqual([item["status"] for item in result["providers"]], ["failed", "failed"])
        self.assertEqual(result["candidates"], [])
        self.assertNotIn("secret", repr(result))

    def test_malformed_or_over_limit_result_blocks_whole_lookup(self):
        for value in (None, {}, (), [None], [dict(self.new, provider="Other")], [self.new]*33):
            self.ft.return_value = value
            result = self.run_lookup()
            self.assertEqual((result["status"], result["candidates"]), ("error", []))
        self.ft.return_value = [self.new]*32
        self.assertEqual(len(self.run_lookup()["candidates"]), 33)

    def test_two_successful_zero_match_searches_are_not_errors(self):
        self.dnd.return_value = []
        self.ft.return_value = []
        result = self.run_lookup()
        self.assertEqual((result["status"], result["candidates"]), ("ok", []))
        self.assertTrue(all(item["status"] == "ok" for item in result["providers"]))

    def test_returned_candidates_are_independent_deep_copies(self):
        self.old["metadata"] = {"tags": ["original"]}
        before = copy.deepcopy(self.old)
        result = self.run_lookup()
        result["candidates"][0]["metadata"]["tags"].append("changed")
        self.assertEqual(self.old, before)
        self.assertEqual(self.run_lookup()["candidates"][0], before)

    def test_bad_settings_fail_before_provider_calls(self):
        for options in ({"dnd_enabled": 1}, {"fivetools_enabled": "false"},
                        {"max_candidates": True}, {"max_candidates": 0}):
            with self.assertRaises(ValueError):
                self.run_lookup(**options)
        self.dnd.assert_not_called()
        self.ft.assert_not_called()

    def test_same_name_candidates_are_not_collapsed_or_field_merged(self):
        self.old.pop("initiative_bonus")
        self.new.pop("hp")
        result = self.run_lookup()["candidates"]
        self.assertNotIn("initiative_bonus", result[0])
        self.assertNotIn("hp", result[1])
        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
