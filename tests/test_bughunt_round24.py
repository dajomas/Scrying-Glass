"""Monster-file fields must not be inferred from JSON container representations."""
import asyncio
import copy
import json
import unittest
import test_bughunt_round21 as fixtures
from test_sqlite_storage import HTTPError

class MonsterFieldTypeTests(unittest.TestCase):
    setUp=fixtures.BoundedCombatantImportTests.setUp
    tearDown=fixtures.BoundedCombatantImportTests.tearDown
    monster=fixtures.BoundedCombatantImportTests.monster

    def raw(self,**changes):
        data={'name':'Goblin','type':'goblin','ac':12,'hp':10};data.update(changes)
        return json.dumps(data).encode()

    def parse(self,**changes):
        raw=self.raw(**changes);self.monster(raw)
        return self.c.parse_monster(raw)

    def reject(self,**changes):
        with self.assertRaises(HTTPError) as error:self.parse(**changes)
        self.assertEqual(error.exception.status_code,400)

    def test_name_and_type_must_be_text_not_coerced_containers(self):
        for field in ('name','type'):
            for value in (['Goblin'],{'value':'Goblin'},True,123):
                with self.subTest(field=field,value=value):self.reject(**{field:value})

    def test_hp_containers_and_booleans_are_rejected(self):
        for value in ([10],{'value':10},True,False):
            with self.subTest(value=value):self.reject(hp=value)

    def test_ac_containers_and_booleans_are_rejected(self):
        for value in ([12],{'value':12},True,False):
            with self.subTest(value=value):self.reject(ac=value)

    def test_invalid_primary_hp_text_is_not_silently_reinterpreted(self):
        self.reject(hpText={'value':5},hp=10)

    def test_overlong_name_is_rejected_during_parsing(self):self.reject(name='x'*101)
    def test_overlong_type_is_rejected_during_parsing(self):self.reject(type='x'*101)

    def test_supported_text_and_numeric_stat_forms_keep_priority_and_zero(self):
        fields=self.parse(name=' 123 ',type=' goblin ',ac=None,armorClass='15 (natural armor)',hpText=0,hp=10)
        self.assertEqual(fields,{'name':'123','monster_species':'goblin','ac':15,'hp':0})
        self.assertEqual(self.parse(ac=12.0,hp='10 (2d6)')['hp'],10)

    def test_invalid_structured_stat_import_does_not_mutate_or_lookup(self):
        upload,call=self.monster(self.raw(hp={'value':10}))
        before=copy.deepcopy(self.c.STATE);lookups=[]
        self.c.dnd_image=lambda species:lookups.append(species)
        with self.assertRaises(HTTPError) as error:asyncio.run(call())
        self.assertEqual(error.exception.status_code,400)
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(lookups,[])

if __name__=='__main__':unittest.main()
