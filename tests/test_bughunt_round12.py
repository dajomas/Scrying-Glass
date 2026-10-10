"""Campaign roster identities stay compatible with saved setups during recovery."""
import copy
import io
import json
import unittest
import zipfile
import test_encounter_features as fixture
from test_sqlite_storage import HTTPError

class RosterRecoveryIdentityTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown
    call=fixture.FeatureTests.call

    def bundle(self,mutate):
        with zipfile.ZipFile(io.BytesIO(self.f.export_bundle())) as archive:
            members={key:archive.read(key) for key in archive.namelist()}
        payload=json.loads(members['campaign.json']);mutate(payload)
        members['campaign.json']=json.dumps(payload).encode()
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
            for key,data in members.items():archive.writestr(key,data)
        return out.getvalue()

    def reject_bundle(self,mutate):
        before=self.c.read_campaigns();state=copy.deepcopy(self.c.STATE)
        with self.assertRaises(HTTPError) as error:self.call('import_bundle',self.bundle(mutate))
        self.assertEqual(error.exception.status_code,422)
        self.assertEqual(self.c.read_campaigns(),before)
        self.assertEqual(self.c.STATE,state)
        self.assertEqual(list(self.c.UPLOAD_DIR.iterdir()),[])

    def test_bundle_rejects_roster_monster_collision(self):
        self.reject_bundle(lambda p:p['setups']['default']['monsters'][0].update(id='c'))

    def test_bundle_rejects_roster_lair_collision(self):
        def mutate(p):p['setups']['default']['lairs']=[{'id':'c','name':'Lair'}]
        self.reject_bundle(mutate)

    def test_bundle_rejects_runtime_roster_collision_with_other_setup(self):
        def mutate(p):
            p['setups']['other']=copy.deepcopy(p['setups']['default'])
            p['setups']['other']['monsters'][0]['id']='future-character'
            p['encounter']['characters'][0]['id']='future-character'
        self.reject_bundle(mutate)

    def test_valid_bundle_remains_additive(self):
        active=self.c.active_campaign()
        result=self.call('import_bundle',self.f.export_bundle())
        self.assertNotEqual(result['campaign_id'],active)
        self.assertEqual(self.c.active_campaign(),active)
        self.c.load_setup_state('default',result['campaign_id'])

    def test_runtime_replacement_can_replace_its_own_setup_ids(self):
        def mutate(p):
            p['setups']['default']['monsters'][0]['id']='replacement-character'
            p['encounter']['characters'][0]['id']='replacement-character'
        result=self.call('import_bundle',self.bundle(mutate))
        self.assertIn('checkpoint_id',result)

    def checkpoint_then_remove_roster(self):
        ident=self.call('save_checkpoint',{'name':'Before removal'})['id']
        self.c.clear_turns();self.c.STATE['characters']=[]
        self.c.STATE['battle_order']=['m']
        self.c.save_active_campaign_characters();self.c.save_active_setup_monsters();self.c.save_state()
        return ident

    def restore(self,ident):
        preview=self.f.preview_checkpoint(ident)
        return self.call('restore_checkpoint',ident,{'confirm':True,'revision':preview['revision']})

    def reject_restore(self,kind):
        ident=self.checkpoint_then_remove_roster()
        item={'id':'c','name':'Reused identity'}
        if kind=='monsters':item['hp']=10
        state=self.c.normalize_state({kind:[item]})
        campaign=self.c.active_campaign()
        self.c.STORAGE.save_setup(campaign,'other',self.c.setup_snapshot(state))
        before=copy.deepcopy(self.c.STATE)
        saved=self.c.STORAGE.load_setup(campaign,'default');other=self.c.STORAGE.load_setup(campaign,'other')
        revision=self.f.store.revision()
        with self.assertRaises(HTTPError) as error:self.restore(ident)
        self.assertEqual(error.exception.status_code,409)
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.c.STORAGE.load_characters(campaign),[])
        self.assertEqual(self.c.STORAGE.load_setup(campaign,'default'),saved)
        self.assertEqual(self.c.STORAGE.load_setup(campaign,'other'),other)
        self.assertEqual(self.f.store.revision(),revision)

    def test_checkpoint_rejects_roster_collision_with_other_monster(self):self.reject_restore('monsters')
    def test_checkpoint_rejects_roster_collision_with_other_lair(self):self.reject_restore('lairs')

    def test_checkpoint_can_replace_colliding_ids_in_its_own_setup(self):
        ident=self.checkpoint_then_remove_roster()
        state=self.c.normalize_state({'monsters':[{'id':'c','name':'Replacement','hp':10}]})
        campaign=self.c.active_campaign()
        self.c.STORAGE.save_setup(campaign,'default',self.c.setup_snapshot(state))
        self.restore(ident)
        self.assertEqual(self.c.STATE['characters'][0]['id'],'c')
        loaded=self.c.load_setup_state('default',campaign)
        self.assertEqual(loaded['monsters'][0]['id'],'m')

    def test_ordinary_checkpoint_restore_still_works(self):
        ident=self.call('save_checkpoint',{'name':'Normal'})['id']
        self.call('edit_features','c',{'hp_delta':-1})
        self.restore(ident)
        self.assertEqual(self.c.entity('c')['hp'],20)

if __name__=='__main__':unittest.main()
