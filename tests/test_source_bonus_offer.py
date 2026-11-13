"""Pure signed-offer tests; not HTTP, browser, user-scope or storage acceptance."""
import base64
import hashlib
import hmac
import json
import unittest
from python.scrying_glass_source_bonus_offer import issue_bonus_offer, read_bonus_offer


class SourceBonusOfferTests(unittest.TestCase):
    def setUp(self):
        self.key = b"fixture-only-key"
        self.candidate = dict(species="Goblin", name="Goblin", provider="D&D Beyond",
            source_url="https://www.dndbeyond.com/monsters/example", legacy=False,
            initiative_bonus=12, initiative_bonus_status="available")

    def read(self, token, **changes):
        args = dict(species="Goblin", key=self.key, now=1000, max_age=1800)
        args.update(changes)
        return read_bonus_offer(token, **args)

    def token(self, **changes):
        return issue_bonus_offer(dict(self.candidate, **changes), self.key, now=1000)

    def test_signed_zero_negative_and_storage_boundaries(self):
        for value in (12, 0, -2, -(2**63), 2**63-1):
            with self.subTest(value=value):
                result = self.read(self.token(initiative_bonus=value))
                self.assertEqual(result["initiative_bonus"], value)
                self.assertEqual(result["initiative_bonus_origin"], "source")
                self.assertEqual(result["monster_source_url"], self.candidate["source_url"])
                self.assertNotIn("initiative_roll", result)
                self.assertNotIn("initiative", result)

    def test_invalid_or_unavailable_candidate_has_no_offer(self):
        for status in ("missing", "invalid", "ambiguous", None):
            self.assertIsNone(self.token(initiative_bonus_status=status))
        for value in (None, True, False, 2.5, "12", [], {}, 2**63, -(2**63)-1):
            self.assertIsNone(self.token(initiative_bonus=value))
        for changes in ({"source_url": "https://evil.test/monsters/example"},
                        {"species": ""}, {"species": "x"*101}, {"provider": "unknown"}):
            self.assertIsNone(self.token(**changes))
        self.assertIsNone(issue_bonus_offer(None, self.key, now=1000))

    def test_signature_species_expiry_and_future_are_checked(self):
        token = self.token()
        for changes in ({"key": b"wrong"}, {"species": "Orc"}, {"now": 2801},
                        {"now": 939}, {"now": float("nan")}, {"max_age": -1}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.read(token, **changes)
        self.assertEqual(self.read(token, now=2800)["initiative_bonus"], 12)
        for bad in (None, "manual", token + "x", "x"*8193):
            with self.assertRaises(ValueError):
                self.read(bad)

    def test_tampered_payload_is_rejected(self):
        data, signature = self.token().split(".")
        payload = json.loads(base64.urlsafe_b64decode(data))
        payload["initiative_bonus"] = 99
        changed = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        with self.assertRaises(ValueError):
            self.read(changed + "." + signature)

    def test_wrong_purpose_and_invalid_signed_schema_are_rejected(self):
        data, _ = self.token().split(".")
        original = json.loads(base64.urlsafe_b64decode(data))
        for change in ({"purpose": "image-selection"}, {"initiative_bonus": True},
                       {"issued": True}, {"source_fields": {}}, {"extra": 1}):
            payload = dict(original, **change)
            encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
            signed = encoded + "." + hmac.new(self.key, encoded.encode(), hashlib.sha256).hexdigest()
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.read(signed)

    def test_candidate_is_not_mutated_and_same_species_sources_stay_distinct(self):
        before = dict(self.candidate)
        first = self.token()
        second = self.token(source_url="https://www.dndbeyond.com/monsters/other", legacy=True)
        self.assertEqual(self.candidate, before)
        self.assertNotEqual(first, second)
        self.assertNotEqual(self.read(first)["monster_source_url"], self.read(second)["monster_source_url"])


if __name__ == "__main__":
    unittest.main()
