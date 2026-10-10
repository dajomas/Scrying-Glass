"""Campaign ID parsing remains bounded and returns controlled errors."""
import unittest
import test_encounter_features as fixture
from test_sqlite_storage import HTTPError

class CampaignIdBoundsTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown

    def rejected(self,value):
        with self.assertRaises(HTTPError) as error:self.c.require_campaign(value)
        self.assertEqual(error.exception.status_code,404)

    def test_very_long_positive_id_is_rejected(self):self.rejected('9'*5000)
    def test_very_long_zero_id_is_rejected(self):self.rejected('0'*5000)
    def test_signed_storage_overflow_id_is_rejected(self):self.rejected(str(2**63))
    def test_zero_padded_existing_id_is_canonicalized(self):
        ident=self.c.active_campaign()
        self.assertEqual(self.c.require_campaign('0'*5000+ident),ident)
    def test_normal_ids_and_invalid_formats_keep_behavior(self):
        ident=self.c.active_campaign()
        self.assertEqual(self.c.require_campaign(' 00'+ident+' '),ident)
        self.assertEqual(self.c.require_campaign(None),ident)
        for value in ('0','-1','1.0','abc','١'):
            with self.subTest(value=value):self.rejected(value)

if __name__=='__main__':unittest.main()
