"""Helper-level coverage only, not production service or transport integration."""
import copy
import unittest
from python.scrying_glass_statblock_state import prepare_private_state, normalize_state, response_payload
from python.scrying_glass_statblock_encounters import PRIVATE_KEY


def snapshot():
    return dict(model_version=1, source_label="Source", subtitle="", completeness="available",
        definitions=[], facts=[], warnings=[], nodes=[], provenance=[dict(position=0,
        role="selected", provider="file", entity_id="fixture", adapter_version="1", credits=[])])


class Context:
    @staticmethod
    def normalize_state(raw):
        if type(raw) is not dict or type(raw.get("monsters")) is not list:
            raise ValueError("invalid state")
        return copy.deepcopy(raw)


class PrivateStateTests(unittest.TestCase):
    def test_private_map_is_separate_and_does_not_alias_input(self):
        private = {"m": snapshot()}
        before = copy.deepcopy(private)
        state = normalize_state(Context(), {"monsters":[{"id":"m","hp":7}]}, private_snapshots=private)
        self.assertEqual(set(state[PRIVATE_KEY]), {"m"})
        self.assertNotIn(PRIVATE_KEY, state["monsters"][0])
        state[PRIVATE_KEY]["m"]["source_label"] = "Changed"
        self.assertEqual(private, before)

    def test_rejects_reserved_input_bad_maps_and_foreign_targets(self):
        with self.assertRaisesRegex(ValueError, "Reserved"):
            normalize_state(Context(), {"monsters":[], PRIVATE_KEY:{}})
        for bad in ([], False, 0, ""):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    normalize_state(Context(), {"monsters":[]}, private_snapshots=bad)
        with self.assertRaisesRegex(ValueError, "not a normalized"):
            prepare_private_state({"other":snapshot()}, {"m"})

    def test_bad_snapshot_fails_before_attachment_without_mutating_input(self):
        bad = snapshot(); bad["model_version"] = 99
        raw = {"monsters":[{"id":"m"}]}
        before = copy.deepcopy(raw)
        with self.assertRaises(ValueError):
            normalize_state(Context(), raw, private_snapshots={"m":bad})
        self.assertEqual(raw, before)
        self.assertNotIn(PRIVATE_KEY, raw)

    def test_projection_filters_nested_keys_without_aliasing_or_rewriting_text(self):
        source={PRIVATE_KEY:{"m":snapshot()}, "monsters":[{"id":"m", PRIVATE_KEY:{"secret":1}, "hp":7}], "note":PRIVATE_KEY}
        result=response_payload(source)
        self.assertNotIn(PRIVATE_KEY,result)
        self.assertNotIn(PRIVATE_KEY,result["monsters"][0])
        self.assertEqual(result["note"],PRIVATE_KEY)
        result["monsters"][0]["hp"] = 1
        self.assertEqual(source["monsters"][0]["hp"],7)
        self.assertIn(PRIVATE_KEY,source["monsters"][0])


if __name__ == "__main__": unittest.main()
