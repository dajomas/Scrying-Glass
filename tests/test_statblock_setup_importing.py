"""Protected setup-import regressions; native execution is delegated to CI.

Service fixtures and deferred-emitter observations are not actor/HTTP/socket tests.
"""
import asyncio
import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import test_statblock_stage2_contracts as contracts
from python.scrying_glass_admin_setups import AdminSetupsMixin
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_statblock_detaching import detach_loaded_setup
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_importing import import_limits, prepare_setup_import
from python.scrying_glass_statblock_loading import PrivateEncounterState
from python.scrying_glass_statblock_model import ModelLimits
from python.scrying_glass_statblock_restore import restore_bindings, restore_encounter


def graph(label):
    value = contracts.reference_snapshot(label)
    value['facts'] = [dict(position=0, key='alignment', label='Alignment', display_text='Neutral')]
    value['warnings'] = [dict(position=0, code='fixture', message='Private import warning')]
    value['provenance'][0]['credits'] = [dict(position=0, attribution='Private fixture credit',
        publisher='Fixture', license_name='Fixture licence', license_url='https://example.org/licence')]
    return value


class SetupImportingTests(unittest.TestCase):
    setUp = contracts.StatblockStage2ContractTests.setUp
    tearDown = contracts.StatblockStage2ContractTests.tearDown
    encounter = contracts.StatblockStage2ContractTests.encounter
    stored = contracts.StatblockStage2ContractTests.stored
    seed = contracts.StatblockStage2ContractTests.seed
    assert_content = contracts.StatblockStage2ContractTests.assert_content

    def run_import(self, campaign=None, name='default', life_filter='all'):
        handler = AdminSetupsMixin(); handler.context = self.c
        payload = SimpleNamespace(name=name, campaign=campaign or self.c.active_campaign(),
                                  kind='monsters', life_filter=life_filter)
        return asyncio.run(transactional_handler(self.c, handler.import_setup)(payload))

    def dump(self):
        return list(self.c.STORAGE.connection.iterdump())

    def source(self):
        self.seed('Earlier')
        api = PrivateEncounterStorage(self.c.STORAGE); state = api.load(self.encounter())
        state[PRIVATE_KEY]['m'] = graph('Source graph')
        value = api.save(self.encounter(), state)[PRIVATE_KEY]['m']
        self.c.load_state()
        return value

    def assert_unchanged(self, dump, state):
        self.assertEqual(self.dump(), dump)
        self.assertEqual(dict(self.c.STATE), dict(state))
        self.assertEqual(self.c.STATE._statblocks, state._statblocks)
        self.assertFalse(self.c.STORAGE.connection.in_transaction)

    def observe(self):
        events = []
        async def broadcast():
            if getattr(self.c, '_defer_database_broadcast', False):
                self.c._database_broadcast_pending = True
            else:
                events.append((self.c.STORAGE.connection.in_transaction,
                               self.f.store.revision(), copy.deepcopy(self.c.STATE._statblocks)))
        self.c.broadcast = broadcast
        return events

    def test_same_setup_independent_rows_revision_graph_reload_and_privacy(self):
        before = self.source(); db = self.c.STORAGE; owner = self.encounter()
        bindings = restore_bindings(db, owner); events = self.observe(); revision = self.f.store.revision()
        result = self.run_import()
        self.assertEqual(result['monsters'], 1)
        ident = next(item['id'] for item in self.c.STATE['monsters'] if item['id'] != 'm')
        saved = self.stored(); self.assert_content(saved[ident], before)
        self.assertEqual(saved['m'], before); self.assertGreater(before['revision'], 1)
        self.assertEqual(saved[ident]['revision'], 1)
        self.assertNotEqual(saved[ident]['prepared_at'], before['prepared_at'])
        after = restore_bindings(db, owner)
        self.assertEqual(after['m'], bindings['m']); self.assertNotEqual(after['m'][0], after[ident][0])
        headers = list(db.connection.execute(
            'SELECT id,monster_id FROM monster_statblocks WHERE monster_id IN (?,?)',
            (after['m'][0], after[ident][0])))
        self.assertEqual(len(headers), 2); self.assertNotEqual(headers[0][0], headers[1][0])
        self.assertEqual(len(events), 1); self.assertFalse(events[0][0])
        self.assertGreater(events[0][1], revision); self.assertEqual(events[0][2], saved)
        self.assertNotIn(PRIVATE_KEY, json.dumps(self.c.STATE))
        self.assertNotIn('Private fixture credit', json.dumps(self.c.public_state()))
        self.assertNotIn('Private import warning', json.dumps(self.c.display_state()))
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, saved)
        async def edit_clone():
            value = self.c.STATE._statblocks[ident]
            value.pop('content_digest', None); value['source_label'] = 'Clone edit'
        asyncio.run(transactional_handler(self.c, edit_clone)())
        self.assertEqual(self.stored()['m'], before)
        self.assertEqual(self.stored()[ident]['revision'], 2)
        self.assertEqual(list(db.connection.execute('PRAGMA foreign_key_check')), [])

    def test_cross_campaign_life_filters_preserve_both_sides_and_effect_remapping(self):
        destination = self.source(); db = self.c.STORAGE
        campaign = db.create_campaign('Import source', '', 'now'); db.save_characters(campaign, [])
        monsters = []
        for ident, hp in (('a', 8), ('d', 0)):
            item = copy.deepcopy(self.c.STATE['monsters'][0])
            item.update(id=ident, hp=hp, alive=hp > 0, life_state='standing' if hp else 'dead')
            item['effects'] = [dict(id='effect-'+ident, name='Link', source_id=ident,
                anchor_id=ident, public=False, concentration=False, timing='end', turns=2, notes='')]
            monsters.append(item)
        db.save_setup(campaign, 'source', {'monsters':monsters})
        owner = self.encounter(campaign, 'source'); api = PrivateEncounterStorage(db)
        state = api.load(owner); state[PRIVATE_KEY] = {ident:graph(ident) for ident in ('a','d')}
        source = api.save(owner, state)[PRIVATE_KEY]; bindings = restore_bindings(db, owner)
        for life_filter, expected in (('alive', {'a'}), ('dead', {'d'}), ('all', {'a','d'})):
            with self.subTest(life_filter=life_filter):
                ids = {item['id'] for item in self.c.STATE['monsters']}
                self.run_import(campaign, 'source', life_filter)
                clones = [item for item in self.c.STATE['monsters'] if item['id'] not in ids]
                self.assertEqual(len(clones), len(expected))
                self.assertEqual({self.c.STATE._statblocks[item['id']]['source_label'] for item in clones}, expected)
                for item in clones:
                    value = self.c.STATE._statblocks[item['id']]
                    self.assert_content(value, source[value['source_label']]); self.assertEqual(value['revision'], 1)
                    self.assertFalse(item['active']); self.assertFalse(item['in_turn'])
                    self.assertEqual(item['effects'][0]['source_id'], item['id'])
                    self.assertEqual(item['effects'][0]['anchor_id'], item['id'])
                    self.assertNotEqual(item['effects'][0]['id'], 'effect-'+value['source_label'])
                self.assertEqual(self.stored()['m'], destination)
                self.assertEqual(api.load(owner)[PRIVATE_KEY], source)
                self.assertEqual(restore_bindings(db, owner), bindings)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, self.stored())

    def test_unsaved_runtime_destination_has_independent_graphs_and_reload(self):
        before = self.source(); db = self.c.STORAGE; source_bindings = restore_bindings(db, self.encounter())
        async def detach(): detach_loaded_setup(self.c)
        asyncio.run(transactional_handler(self.c, detach)())
        existing = copy.deepcopy(self.c.STATE._statblocks)
        self.run_import(); self.assertIsNone(self.c.active_setup_reference())
        owner = db.connection.execute('SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()[0]
        saved = PrivateEncounterStorage(db).load(owner)[PRIVATE_KEY]
        ident = next(key for key in saved if key != 'm')
        self.assertEqual(saved['m'], existing['m']); self.assert_content(saved[ident], before)
        self.assertEqual(saved[ident]['revision'], 1); self.assertEqual(self.stored()['m'], before)
        self.assertEqual(restore_bindings(db, self.encounter()), source_bindings)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, saved)

    def test_lowered_import_limit_rejects_atomically_but_stored_reads_survive(self):
        before = self.source(); self.c.CONFIG['statblocks'] = {'limits': {'content_nodes':1}}
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks['m'], before)
        dump = self.dump(); state = copy.deepcopy(self.c.STATE); events = self.observe()
        with self.assertRaises(ValueError): self.run_import()
        self.assert_unchanged(dump, state); self.assertEqual(events, [])
        merged = prepare_setup_import(self.c, state, [], {})
        self.assertEqual(merged._statblocks, state._statblocks)

    def test_failure_after_tracker_save_rolls_back_sql_and_live_metadata(self):
        self.source(); dump = self.dump(); state = copy.deepcopy(self.c.STATE); save = self.c.save_state
        events = self.observe()
        def fail():
            save()
            raise OSError('after tracker saving')
        with patch.object(self.c, 'save_state', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'after tracker'): self.run_import()
        self.assert_unchanged(dump, state); self.assertEqual(events, [])

    def test_failure_after_private_flush_rolls_back_graphs_counters_history_and_notification(self):
        self.source()
        asyncio.run(transactional_handler(self.c, self.f.edit_features)('m', {'temp_hp':3}))
        self.assertIsNotNone(self.f.store.latest_undo(self.c.active_campaign()))
        dump = self.dump(); state = copy.deepcopy(self.c.STATE); events = self.observe()
        revision = self.f.store.revision(); after = self.f.after_transaction
        def fail(*args):
            self.assertEqual(len(self.c.STATE._statblocks), 2)
            self.assertEqual(self.c.STATE._statblocks, self.stored())
            after(*args)
            raise OSError('after private flush and history')
        with patch.object(self.f, 'after_transaction', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'after private flush'): self.run_import()
        self.assert_unchanged(dump, state); self.assertEqual(self.f.store.revision(), revision)
        self.assertEqual(events, [])

    def test_serialized_private_source_rejects_and_plain_attributes_gain_no_authority(self):
        self.source(); dump = self.dump(); state = copy.deepcopy(self.c.STATE)
        source = dict(state); source[PRIVATE_KEY] = copy.deepcopy(state._statblocks)
        with patch.object(self.c, 'load_setup_state', return_value=source):
            with self.assertRaises(ValueError): self.run_import()
        self.assert_unchanged(dump, state)
        class Untrusted(dict): pass
        source = Untrusted(state); source._statblocks = copy.deepcopy(state._statblocks)
        with patch.object(self.c, 'load_setup_state', return_value=source): self.run_import()
        self.assertEqual(self.c.STATE._statblocks, state._statblocks)
        self.assertEqual(len(self.c.STATE['monsters']), 2)
        self.assertEqual(self.stored(), state._statblocks)

    def test_bad_allocations_or_missing_source_leave_destination_unchanged(self):
        self.source(); dump = self.dump(); state = copy.deepcopy(self.c.STATE)
        cases = [([{'id':'x'}], {'absent':'x'}), ([{'id':'m'}], {'m':'m'}),
            ([{'id':'c'}], {'m':'c'}), ([{'id':'x'}, {'id':'x'}], {'m':'x'}),
            ([{'id':'x'}], {}), ([], {'m':'x'}), ([{'id':' '}], {'m':' '}),
            ([{'id':'x'}], {'m':True})]
        for clones, mapping in cases:
            with self.subTest(mapping=mapping):
                with self.assertRaises(ValueError): prepare_setup_import(self.c, state, clones, mapping)
                self.assert_unchanged(dump, state)
        with patch.object(self.c, 'reset_imported_monster', return_value={'id':'m'}):
            with self.assertRaises(ValueError): self.run_import()
        self.assert_unchanged(dump, state)
        with self.assertRaises(self.c.HTTPException): self.run_import(name='missing')
        self.assert_unchanged(dump, state)

    def test_counter_only_source_history_is_not_exported_to_clone(self):
        self.source(); db = self.c.STORAGE; owner = self.encounter()
        absent = PrivateEncounterState(self.c.STATE, {})
        restore_encounter(db, owner, absent, expected_bindings=restore_bindings(db, owner))
        self.c.load_state(); bindings = restore_bindings(db, owner)
        self.assertGreater(bindings['m'][1], 1); self.assertEqual(self.stored(), {})
        self.run_import(); after = restore_bindings(db, owner)
        ident = next(key for key in after if key != 'm')
        self.assertEqual(after['m'], bindings['m']); self.assertEqual(after[ident][1], 0)
        self.assertEqual(self.c.STATE._statblocks, {}); self.assertEqual(self.stored(), {})

    def test_subset_and_empty_maps_preserve_existing_and_omit_unselected_graphs(self):
        before = self.source(); original = copy.deepcopy(self.c.STATE)
        source = PrivateEncounterState({'monsters':[{'id':'a'}, {'id':'b'}]},
                                       {'a':graph('Selected'), 'b':graph('Unselected')})
        merged = prepare_setup_import(self.c, source, [{'id':'x'}], {'a':'x'})
        self.assertEqual(set(merged._statblocks), {'m','x'}); self.assertEqual(merged._statblocks['m'], before)
        self.assertEqual(merged._statblocks['x']['source_label'], 'Selected')
        self.assertNotIn('revision', merged._statblocks['x']); self.assertNotIn('prepared_at', merged._statblocks['x'])
        merged._statblocks['x']['source_label'] = 'Changed'; self.assertEqual(source._statblocks['a']['source_label'], 'Selected')
        empty = prepare_setup_import(self.c, source, [], {})
        self.assertEqual(empty._statblocks, original._statblocks); self.assertEqual(dict(empty), dict(original))
        self.assertEqual(self.c.STATE._statblocks, original._statblocks)

    def test_operator_model_limits_defaults_overrides_and_invalid_configuration(self):
        self.assertEqual(import_limits(SimpleNamespace(CONFIG={})), ModelLimits())
        config = {'statblocks': {'limits': {'content_nodes':17, 'active_jobs':2}}}
        limits = import_limits(SimpleNamespace(CONFIG=config))
        self.assertEqual(limits.content_nodes, 17); self.assertEqual(limits.snapshot_bytes, ModelLimits().snapshot_bytes)
        for config in (None, {'statblocks':None}, {'statblocks':{'limits':None}},
                       {'statblocks':{'limits':{'content_nodes':True}}},
                       {'statblocks':{'limits':{'snapshot_bytes':0}}}):
            with self.subTest(config=config):
                with self.assertRaises(ValueError): import_limits(SimpleNamespace(CONFIG=config))


if __name__ == '__main__': unittest.main()
