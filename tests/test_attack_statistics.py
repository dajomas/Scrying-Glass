"""Real SQLite/transaction tests for attack reductions and manual restoration."""
import asyncio
import copy
import io
import json
import sqlite3
import unittest
import zipfile
from contextlib import closing
from unittest.mock import patch
import test_bughunt_round18 as fixture
import test_bughunt_round10 as helpers
from test_sqlite_storage import HTTPError
from python.scrying_glass_classes import BattleActions
from python.scrying_glass_feature_rules import apply_hp, normalize_features
from python.scrying_glass_statistics import STATS, ABILITIES, statistics_token, legacy_max_edit
from python.scrying_glass_turn_rules import can_take_turn, permanently_dead
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_combatant import reset_entity, reset_imported_monster


class AttackStatisticsTests(unittest.TestCase):
    setUp=fixture.InlineConcentrationLogTests.setUp
    tearDown=fixture.InlineConcentrationLogTests.tearDown
    call=fixture.InlineConcentrationLogTests.call

    def submit(self, rows, token=None):
        cls=helpers.load_class('scrying_glass_admin_battle.py','AdminBattleMixin',
            dict(apply_hp=apply_hp,can_take_turn=can_take_turn,permanently_dead=permanently_dead))
        handler=cls();handler.context=self.c
        payload=BattleActions(actor_id='c',actions=rows,statistics_token=token or statistics_token(self.c))
        return asyncio.run(transactional_handler(self.c,handler.apply_battle_actions)(payload))

    def edit(self, ident='m', **body):
        return self.call('edit_statistics',ident,dict(token=statistics_token(self.c),**body))

    def bases(self, ident='m', **values):
        return self.edit(ident,operation='bases',bases=values)

    def reduce(self, stat='max_hp', amount=5, ident='m'):
        return dict(target_id=ident,action='reduce-stat',stat=stat,amount=amount)

    def item(self, ident='m'):return self.c.entity(ident)

    def test_all_seven_statistics(self):
        self.bases(**dict.fromkeys(ABILITIES,12))
        self.submit([self.reduce(s,2) for s in STATS])
        self.assertEqual(self.item()['base_max_hp'],12)
        for stat in STATS:self.assertEqual(self.item()[stat],10)
        self.assertEqual(self.item()['hp'],10)

    def test_unknown_base_rejects_whole_attack(self):
        before=copy.deepcopy(self.c.STATE)
        with self.assertRaisesRegex(HTTPError,'Unknown original STR'):
            self.submit([dict(target_id='m',action='damage',amount=3),self.reduce('strength')])
        self.assertEqual(self.c.STATE,before)

    def test_damage_then_reduction_not_double_damage(self):
        self.item()['temp_hp']=3
        self.submit([dict(target_id='m',action='damage',amount=6),self.reduce('max_hp',4)])
        self.assertEqual((self.item()['hp'],self.item()['max_hp'],self.item()['temp_hp']),(8,8,0))

    def test_order_changes_healing_cap(self):
        self.item()['hp']=2
        self.submit([self.reduce('max_hp',8),dict(target_id='m',action='heal',amount=20)])
        self.assertEqual((self.item()['hp'],self.item()['max_hp']),(4,4))

    def test_zero_and_stack_no_death_or_temp_consumption(self):
        self.item()['temp_hp']=8
        self.submit([self.reduce('max_hp',20),self.reduce('max_hp',4)])
        self.assertEqual((self.item()['hp'],self.item()['max_hp'],self.item()['temp_hp'],self.item()['death_failures']),(0,0,8,0))
        self.assertEqual(self.item()['life_state'],'down')
        self.assertEqual([e['mechanical']['amount'] for e in self.item()['effects']],[20,4])

    def test_restore_one_or_all_without_healing(self):
        self.bases(strength=10,dexterity=14)
        self.submit([self.reduce(),self.reduce('strength',3),self.reduce('dexterity',4)])
        self.edit(operation='restore',stat='strength')
        self.assertEqual((self.item()['strength'],self.item()['dexterity'],self.item()['max_hp']),(10,10,7))
        self.edit(operation='restore',stat='all')
        self.assertEqual((self.item()['max_hp'],self.item()['hp'],self.item()['dexterity']),(12,7,14))

    def test_restore_never_resurrects(self):
        self.submit([self.reduce('max_hp',20)])
        self.call('edit_features','m',{'life_state':'dead'})
        self.edit(operation='restore',stat='max_hp')
        self.assertEqual((self.item()['hp'],self.item()['life_state']),(0,'dead'))

    def test_sources_and_turns_do_not_expire_reductions(self):
        self.submit([self.reduce()]);self.f.expire('c','end');self.f.clear_concentration('c')
        self.c.STATE['characters']=[];self.f.reconcile()
        self.assertEqual(self.item()['max_hp'],7)
        self.assertEqual(len(self.item()['effects']),1)

    def test_attack_token_required_and_stale(self):
        token=statistics_token(self.c);self.call('edit_features','m',{'temp_hp':1})
        with self.assertRaises(HTTPError):self.submit([self.reduce()],token)
        self.assertEqual(self.item()['max_hp'],12)

    def test_restore_token_stale(self):
        token=statistics_token(self.c);self.submit([self.reduce()])
        with self.assertRaises(HTTPError):self.call('edit_statistics','m',dict(operation='restore',stat='all',token=token))
        self.assertEqual(self.item()['max_hp'],7)

    def test_invalid_stats_amounts_and_base_bounds(self):
        for body in [dict(operation='bases',bases={'strength':True}),dict(operation='bases',bases={'dexterity':31}),dict(operation='bases',bases={'charisma':-1}),dict(operation='bases',bases={'unknown':4}),dict(operation='restore',stat='unknown')]:
            before=copy.deepcopy(self.c.STATE)
            with self.assertRaises(HTTPError):self.edit(**body)
            self.assertEqual(self.c.STATE,before)
        for amount in [0,-1,100000]:
            with self.assertRaises(Exception):self.submit([self.reduce(amount=amount)])

    def test_ability_base_cannot_clear_while_reduced(self):
        self.bases(wisdom=10);self.submit([self.reduce('wisdom',3)])
        with self.assertRaises(HTTPError):self.bases(wisdom=None)
        self.assertEqual(self.item()['wisdom'],7)

    def test_new_base_does_not_heal(self):
        self.submit([self.reduce()]);self.bases(max_hp=30)
        self.assertEqual((self.item()['max_hp'],self.item()['hp']),(25,7))

    def test_reset_retains_reductions_and_monster_template(self):
        self.item()['original_hp']=9;self.bases(max_hp=20,strength=12)
        self.submit([self.reduce('max_hp',4),self.reduce('strength',2)])
        reset_entity(self.item())
        self.assertEqual((self.item()['hp'],self.item()['max_hp'],self.item()['strength']),(9,16,10))
        copied=reset_imported_monster(self.item());self.assertEqual(copied['effects'],self.item()['effects'])

    def test_storage_rollback_across_damage_and_reductions(self):
        before=copy.deepcopy(self.c.STATE);stored=self.c.STORAGE.load_setup(self.c.active_campaign(),'default')
        with patch.object(self.c,'save_state',side_effect=RuntimeError('write failure')),patch.object(self.c,'broadcast') as broadcast:
            with self.assertRaises(RuntimeError):self.submit([dict(target_id='m',action='damage',amount=1),self.reduce()])
            broadcast.assert_not_called()
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.c.STORAGE.load_setup(self.c.active_campaign(),'default'),stored)

    def test_persist_restart_and_undo(self):
        self.bases('c',charisma=16)
        self.submit([self.reduce('charisma',4,'c')])
        self.c.STORAGE.close();self.c.STORAGE=self.c.STORAGE.__class__(self.c.DATA_DIR/'scrying-glass.sqlite3');self.c.load_state()
        self.assertEqual(self.item('c')['charisma'],12)
        self.call('undo',{'id':self.f.summary()['undo']['id']})
        self.assertEqual(self.item('c')['charisma'],16)

    def test_checkpoint_restores_reductions(self):
        self.submit([self.reduce()]);ident=self.call('save_checkpoint',{'name':'Reduced'})['id']
        self.edit(operation='restore',stat='all');p=self.f.preview_checkpoint(ident)
        self.call('restore_checkpoint',ident,dict(confirm=True,revision=p['revision']))
        self.assertEqual(self.item()['max_hp'],7)

    def test_bundle_and_player_privacy(self):
        self.bases('c',intelligence=18);self.submit([self.reduce('intelligence',4,'c'),self.reduce()])
        result=self.call('import_bundle',self.f.export_bundle())
        self.assertEqual(self.c.STORAGE.load_characters(result['campaign_id'])[0]['intelligence'],14)
        monster=self.c.STORAGE.load_setup(result['campaign_id'],'default')['monsters'][0]
        self.assertEqual(monster['base_max_hp'],12);self.assertEqual(monster['max_hp'],7)
        public=json.dumps(self.c.display_state())
        for field in ['base_max_hp','base_intelligence','mechanical','statistics_token']:
            self.assertNotIn(field,public)

    def test_unsupported_mechanical_import_rolls_back(self):
        self.submit([self.reduce()]);raw=self.f.export_bundle()
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:payload=json.loads(archive.read('campaign.json'))
        payload['encounter']['monsters'][0]['effects'][0]['mechanical']['version']=99
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as archive:archive.writestr('campaign.json',json.dumps(payload))
        before=self.c.read_campaigns()
        with self.assertRaises(HTTPError):self.call('import_bundle',out.getvalue())
        self.assertEqual(self.c.read_campaigns(),before)

    def test_legacy_max_edit_rejected_with_reductions(self):
        self.submit([self.reduce()])
        with self.assertRaises(ValueError):legacy_max_edit(self.item(),{'max_hp':20})
        legacy_max_edit(self.item(),{'max_hp':7});self.assertEqual(self.item()['base_max_hp'],12)

    def test_v7_backup(self):
        path=self.c.DATA_DIR/'v7.sqlite3';db=self.c.STORAGE.__class__(path)
        for table in ('characters','monsters','snapshot_characters'):
            for col in ('mechanical_version','reduction_stat','reduction_amount'):
                db.connection.execute(f'ALTER TABLE {table}_effects DROP COLUMN {col}')
        db.connection.execute('PRAGMA user_version=7');db.close();db=self.c.STORAGE.__class__(path)
        self.assertEqual(db.connection.execute('PRAGMA user_version').fetchone()[0],8)
        with closing(sqlite3.connect(db.migration_backup)) as backup:self.assertEqual(backup.execute('PRAGMA user_version').fetchone()[0],7)
        db.close()

if __name__=='__main__':unittest.main()
