"""Generated batch names must remain valid and must not mask invalid bases."""
import asyncio
import copy
import unittest
import test_encounter_features as fixture
import test_bughunt_round10 as helpers
from test_sqlite_storage import HTTPError
from python.scrying_glass_database_transactions import transactional_handler

class BatchMonsterNameTests(unittest.TestCase):
    def setUp(self):
        fixture.FeatureTests.setUp(self)
        self.images=helpers.load_class('scrying_glass_service_images.py','ImagesService')(self.c)
        self.c.make_monster=self.images.make_monster;self.c.make_monsters=self.images.make_monsters
        self.c.hp_value_factory=lambda start,end:lambda:10
        self.lookups=[]
        self.c.dnd_image=lambda species:self.lookups.append(species)
    tearDown=fixture.FeatureTests.tearDown

    def batch(self,name,quantity):
        return self.images.make_monsters({'name':name,'monster_species':'goblin','ac':12,'hp':10},'#842029',quantity,None)

    def create(self,name,quantity):
        cls=helpers.load_class('scrying_glass_admin_monsters.py','AdminMonstersMixin',dict(asyncio=asyncio))
        handler=cls();handler.context=self.c
        return asyncio.run(transactional_handler(self.c,handler.create_monster)(
            name=name,monster_species='goblin',ac=12,hprangestart='10',hprangeend='',
            color='#842029',quantity=quantity,image=None))

    def test_singleton_max_length_name_is_not_truncated(self):
        name='x'*100
        self.assertEqual(self.batch(name,1)[0]['name'],name)

    def test_batch_max_length_name_reserves_suffix_space(self):
        items=self.batch('x'*100,12)
        self.assertEqual(len(items),12)
        self.assertEqual(len({x['name'] for x in items}),12)
        self.assertTrue(all(len(x['name'])<=100 for x in items))
        prefixes=[x['name'].rsplit(' - ',1)[0] for x in items]
        self.assertEqual(len(set(prefixes)),1)
        self.assertTrue(items[-1]['name'].endswith(' - 12'))

    def test_short_batch_names_keep_existing_format(self):
        self.assertEqual([x['name'] for x in self.batch('Goblin',2)],['Goblin - 1','Goblin - 2'])

    def test_create_handler_accepts_long_valid_batch_name(self):
        items=self.create('x'*100,2)
        self.assertEqual(len(items),2)
        self.assertTrue(all(len(x['name'])<=100 for x in items))
        self.assertEqual(len(self.c.STORAGE.load_setup(self.c.active_campaign(),'default')['monsters']),3)

    def test_blank_create_base_is_rejected_before_lookup_and_mutation(self):
        before=copy.deepcopy(self.c.STATE)
        with self.assertRaises(HTTPError) as error:self.create('   ',2)
        self.assertEqual(error.exception.status_code,422)
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.lookups,[])

    def test_oversized_create_base_is_not_silently_truncated(self):
        before=copy.deepcopy(self.c.STATE)
        with self.assertRaises(HTTPError) as error:self.create('x'*101,2)
        self.assertEqual(error.exception.status_code,422)
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.lookups,[])

    def test_blank_import_batch_base_is_rejected(self):
        with self.assertRaises(HTTPError) as error:self.batch('   ',2)
        self.assertEqual(error.exception.status_code,422)

    def test_unicode_batch_and_max_quantity_keep_names_valid(self):
        items=self.batch('é'*100,50)
        self.assertEqual(len(items),50)
        self.assertEqual(len({x['name'] for x in items}),50)
        self.assertTrue(all(1<=len(x['name'])<=100 for x in items))

if __name__=='__main__':unittest.main()
