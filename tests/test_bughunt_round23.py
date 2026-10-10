"""Monster-file AC parsing must not strip signs or truncate fractions."""
import json
import unittest
import test_bughunt_round21 as fixtures
from test_sqlite_storage import HTTPError

class MonsterNumericParsingTests(unittest.TestCase):
    setUp=fixtures.BoundedCombatantImportTests.setUp
    tearDown=fixtures.BoundedCombatantImportTests.tearDown
    monster=fixtures.BoundedCombatantImportTests.monster

    def parse(self,ac,hp=10):
        raw=json.dumps({'name':'Goblin','type':'goblin','ac':ac,'hp':hp}).encode()
        self.monster(raw)
        return self.c.parse_monster(raw)

    def rejected(self,ac):
        with self.assertRaises(HTTPError) as error:self.parse(ac)
        self.assertEqual(error.exception.status_code,400)

    def test_negative_numeric_ac_is_rejected(self):self.rejected(-1)
    def test_negative_text_ac_is_rejected(self):self.rejected('-12 (natural armor)')
    def test_fractional_numeric_ac_is_rejected(self):self.rejected(12.5)
    def test_fractional_text_ac_is_rejected(self):self.rejected('12.5 (natural armor)')
    def test_out_of_range_ac_is_rejected_by_parser(self):self.rejected(1000)

    def test_valid_formatted_zero_and_upper_ac_are_preserved(self):
        self.assertEqual(self.parse('15 (natural armor)')['ac'],15)
        self.assertEqual(self.parse(0,hp=0)['ac'],0)
        self.assertEqual(self.parse(0,hp=0)['hp'],0)
        self.assertEqual(self.parse(999)['ac'],999)
        self.assertEqual(self.parse(12.0)['ac'],12)

    def test_unusable_ac_remains_rejected(self):self.rejected('unknown armor')

    def test_fractional_numeric_hp_is_rejected(self):
        with self.assertRaises(HTTPError) as error:self.parse(12,hp=12.5)
        self.assertEqual(error.exception.status_code,400)

    def test_fractional_text_hp_is_rejected(self):
        with self.assertRaises(HTTPError) as error:self.parse(12,hp='12.5 (2d8)')
        self.assertEqual(error.exception.status_code,400)

    def test_whole_scientific_tokens_are_not_truncated(self):
        self.assertEqual(self.parse('1.2e2',hp='1e2')['ac'],120)
        self.assertEqual(self.parse('1.2e2',hp='1e2')['hp'],100)

    def test_existing_signed_hp_boundaries_are_preserved(self):
        for hp in (-(2**63),-1,0,2**63-1):
            self.assertEqual(self.parse(12,hp=str(hp))['hp'],hp)
        with self.assertRaises(HTTPError):self.parse(12,hp=str(2**63))

    def test_bad_ac_import_is_rejected_before_lookup_and_mutation(self):
        raw=json.dumps({'name':'Goblin','type':'goblin','ac':-1,'hp':10}).encode()
        upload,call=self.monster(raw)
        import copy,asyncio
        before=copy.deepcopy(self.c.STATE);lookups=[]
        self.c.dnd_image=lambda species:lookups.append(species)
        with self.assertRaises(HTTPError) as error:asyncio.run(call())
        self.assertEqual(error.exception.status_code,400)
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(lookups,[])

if __name__=='__main__':unittest.main()
