"""Pure selected-source identity and signed snapshot checks; no provider fetches."""
import base64
import copy
import hashlib
import hmac
import json
import unittest
from python.scrying_glass_monster_source_snapshot import (
    capture_source_fields, validate_source_fields, issue_selection, read_selection,
    PROVIDER, URL, NAME, BOOK, LEGACY)


class SourceSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.key=b"test-only-source-snapshot-key"
        self.candidate=dict(species="Goblin",name="Goblin",provider="5e.tools",
            source="XMM",legacy=False,source_url="https://5e.tools/bestiary.html#goblin_xmm",
            image_url="https://example.test/goblin.png")

    def read(self, token, **changes):
        options=dict(now=1000,max_age=1800,image_validator=lambda value:
                     isinstance(value,str) and value.startswith("https://"))
        options.update(changes)
        return read_selection(token,"Goblin",self.key,**options)

    def token(self, candidate=None):
        return issue_selection(self.candidate if candidate is None else candidate,self.key,now=1000)

    def signed(self, payload):
        data=base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        return data+"."+hmac.new(self.key,data.encode(),hashlib.sha256).hexdigest()

    def test_exact_fivetools_identity_and_book(self):
        fields=capture_source_fields(self.candidate)
        self.assertEqual(fields,{PROVIDER:"5e.tools",URL:self.candidate["source_url"],NAME:"Goblin",BOOK:"XMM",LEGACY:False})
        self.assertEqual(validate_source_fields(fields),fields)

    def test_dnd_identity_does_not_invent_a_book(self):
        fields=capture_source_fields(dict(self.candidate,provider="D&D Beyond",
            source="Source book unavailable",source_url="https://www.dndbeyond.com/monsters/123-goblin",legacy=True))
        self.assertEqual(fields[PROVIDER],"D&D Beyond")
        self.assertTrue(fields[LEGACY])
        self.assertNotIn(BOOK,fields)

    def test_distinct_sources_remain_distinct(self):
        other=dict(self.candidate,source="MM",source_url="https://5e.tools/bestiary.html#goblin_mm",legacy=True)
        self.assertNotEqual(capture_source_fields(other),capture_source_fields(self.candidate))

    def test_unknown_or_missing_provider_identity_is_not_inferred(self):
        for candidate in ({"species":"Goblin"},dict(self.candidate,provider="Unknown"),dict(self.candidate,source_url=None)):
            self.assertEqual(capture_source_fields(candidate),{})

    def test_untrusted_dnd_urls_are_not_retained(self):
        for url in ("http://www.dndbeyond.com/monsters/1", "https://evil.test/monsters/1",
                    "https://www.dndbeyond.com.evil.test/monsters/1", "https://user@www.dndbeyond.com/monsters/1",
                    "https://www.dndbeyond.com:444/monsters/1", "https://www.dndbeyond.com/monsters/1?edition=other",
                    "https://www.dndbeyond.com/monsters/1#other", "https://www.dndbeyond.com/login"):
            with self.subTest(url=url):
                self.assertEqual(capture_source_fields(dict(self.candidate,provider="D&D Beyond",source_url=url)),{})

    def test_untrusted_fivetools_fragments_are_not_retained(self):
        for url in ("https://evil.test/bestiary.html#goblin_xmm", "https://5e.tools/bestiary.html?x=1#goblin_xmm",
                    "https://5e.tools/bestiary.html#goblin%00_xmm", "https://5e.tools/bestiary.html#goblin%ZZ_xmm"):
            self.assertEqual(capture_source_fields(dict(self.candidate,source_url=url)),{})

    def test_percent_encoded_names_are_preserved_exactly(self):
        url="https://5e.tools/bestiary.html#adult%20blue%20dragon_xmm"
        self.assertEqual(capture_source_fields(dict(self.candidate,source_url=url))[URL],url)

    def test_bonus_or_dexterity_is_not_captured(self):
        fields=capture_source_fields(dict(self.candidate,initiative_bonus=12,dex=20))
        self.assertNotIn("initiative_bonus",fields)
        self.assertNotIn("dex",fields)

    def test_invalid_optional_metadata_is_not_retained(self):
        fields=capture_source_fields(dict(self.candidate,name=chr(0xD800),source="X"*101,legacy=1))
        self.assertEqual(fields,{PROVIDER:"5e.tools",URL:self.candidate["source_url"]})

    def test_invalid_stored_source_fields_are_rejected(self):
        for fields in (None,[],{PROVIDER:"5e.tools"},{"verified":True},
                       dict(capture_source_fields(self.candidate),monster_source_legacy=1)):
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):validate_source_fields(fields)

    def test_image_and_source_share_one_authenticated_snapshot(self):
        image,fields=self.read(self.token())
        self.assertEqual(image,self.candidate["image_url"])
        self.assertEqual(fields,capture_source_fields(self.candidate))

    def test_input_changes_after_issue_do_not_change_snapshot(self):
        candidate=copy.deepcopy(self.candidate)
        token=self.token(candidate)
        candidate["source_url"]="https://5e.tools/bestiary.html#goblin_mm"
        self.assertEqual(self.read(token)[1][URL],self.candidate["source_url"])

    def test_tampered_signature_species_and_key_are_rejected(self):
        token=self.token()
        with self.assertRaises(ValueError):self.read(token+"x")
        with self.assertRaises(ValueError):
            read_selection(token,"Orc",self.key,now=1000,max_age=1800,image_validator=lambda value:True)
        with self.assertRaises(ValueError):
            read_selection(token,"Goblin",b"wrong-key",now=1000,max_age=1800,image_validator=lambda value:True)

    def test_source_tampering_without_signature_is_rejected(self):
        data,signature=self.token().rsplit(".",1)
        payload=json.loads(base64.urlsafe_b64decode(data))
        payload["source_fields"][URL]="https://5e.tools/bestiary.html#goblin_mm"
        changed=base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()+"."+signature
        with self.assertRaises(ValueError):self.read(changed)

    def test_expired_future_and_oversized_tokens_are_rejected(self):
        for now in (2801,939):
            with self.assertRaises(ValueError):self.read(self.token(),now=now)
        with self.assertRaises(ValueError):self.read("x"*8193)

    def test_old_image_only_token_remains_compatible(self):
        token=self.signed(dict(species="Goblin",image_url="https://example.test/old.png",issued=1000))
        self.assertEqual(self.read(token),("https://example.test/old.png",{}))

    def test_manual_selection_and_missing_image(self):
        self.assertEqual(self.read("manual"),(None,{}))
        candidate=dict(self.candidate,image_url=None)
        image,fields=self.read(self.token(candidate))
        self.assertIsNone(image)
        self.assertEqual(fields[BOOK],"XMM")

    def test_image_validation_still_applies(self):
        with self.assertRaises(ValueError):
            self.read(self.token(dict(self.candidate,image_url="http://example.test/image.png")))

    def test_signed_but_invalid_identity_is_rejected(self):
        token=self.signed(dict(species="Goblin",issued=1000,image_url=None,
            source_fields={PROVIDER:"D&D Beyond",URL:"https://evil.test/monsters/1"}))
        with self.assertRaises(ValueError):self.read(token)

    def test_result_is_independent_and_does_not_mutate_candidate(self):
        before=copy.deepcopy(self.candidate)
        token=self.token()
        first=self.read(token)[1]
        first[BOOK]="changed"
        self.assertEqual(self.read(token)[1][BOOK],"XMM")
        self.assertEqual(self.candidate,before)
