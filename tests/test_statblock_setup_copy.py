"""2C.2a native stored-setup copy tests; not service/HTTP or Save As coverage."""
import copy
import unittest
from unittest.mock import patch
import test_statblock_encounters as fixtures
from test_statblock_clone_kernel import reference_snapshot
from python.scrying_glass_identity_rules import ParticipantIdentityConflict
from python.scrying_glass_statblock_encounters import PRIVATE_KEY
from python.scrying_glass_statblock_storage import StatblockStorage


class SetupPrivateCopyTests(unittest.TestCase):
    setUp = fixtures.EncounterAdapterTests.setUp

    def owner(self, campaign, name):
        return self.storage.connection.execute(
            'SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',
            (campaign, name)).fetchone()[0]

    def monster(self, owner):
        return self.storage.connection.execute('SELECT id FROM monsters WHERE encounter_id=?', (owner,)).fetchone()[0]

    def seed(self, label='Source'):
        state = self.api.load(self.encounter)
        state[PRIVATE_KEY]['m'] = reference_snapshot(label)
        return self.api.save(self.encounter, state)

    def dump(self):
        return '\n'.join(self.storage.connection.iterdump())

    def test_same_and_cross_campaign_copies_are_independent(self):
        self.seed(); self.seed('Latest')
        plain = self.storage.load_setup(self.campaign, 'one')
        plain['active_setup'] = {'campaign_id':self.campaign,'name':'one'}
        self.storage.save_setup(self.campaign, 'one', plain)
        before = self.api.load(self.encounter)
        original = before[PRIVATE_KEY]['m']
        source_head = self.storage._statblock_revision_head(self.monster(self.encounter))
        other = self.storage.create_campaign('Other', '', 'now')
        for target in (self.campaign, other):
            with self.subTest(target=target):
                name = self.storage.transfer_setup(self.campaign, target, 'one', 'copy')
                owner = self.owner(target, name); result = self.api.load(owner)[PRIVATE_KEY]['m']
                self.assertNotEqual(owner, self.encounter)
                self.assertNotEqual(self.monster(owner), self.monster(self.encounter))
                self.assertGreater(original['revision'], 1); self.assertEqual(result['revision'], 1)
                self.assertEqual(self.storage._statblock_revision_head(self.monster(owner)), 1)
                self.assertNotEqual(result['prepared_at'], original['prepared_at'])
                for key in ('content_digest','definitions','nodes','facts','warnings','provenance'):
                    self.assertEqual(result[key], original[key])
                self.assertIsNone(self.storage.load_setup(target, name).get('active_setup'))
                value = self.api.load(owner); value[PRIVATE_KEY]['m'] = reference_snapshot('Copy changed')
                self.api.save(owner, value)
                self.assertEqual(self.api.load(self.encounter), before)
                self.assertEqual(self.storage._statblock_revision_head(self.monster(self.encounter)), source_head)

    def test_failure_after_graph_writes_rolls_back_entire_destination(self):
        state = self.seed(); state['monsters'].append({'id':'n','hp':2})
        state[PRIVATE_KEY]['n'] = reference_snapshot('Second'); self.api.save(self.encounter, state)
        target = self.storage.create_campaign('Other', '', 'now'); before = self.dump()
        save = StatblockStorage.save; calls = []
        def fail_second(writer, *args, **kwargs):
            calls.append(args[0]); result = save(writer, *args, **kwargs)
            if len(calls) == 2: raise OSError('injected after second graph write')
            return result
        with patch.object(StatblockStorage, 'save', new=fail_second):
            with self.assertRaises(OSError): self.storage.transfer_setup(self.campaign, target, 'one', 'copy')
        self.assertEqual(len(calls), 2); self.assertEqual(self.dump(), before)
        self.assertFalse(self.storage.setup_exists(target, 'one'))
        self.assertFalse(self.storage.connection.in_transaction)

    def test_destination_roster_conflict_remains_atomic(self):
        self.seed(); target = self.storage.create_campaign('Other', '', 'now')
        self.storage.save_characters(target, [{'id':'m','hp':4}]); before = self.dump()
        with self.assertRaises(ParticipantIdentityConflict):
            self.storage.transfer_setup(self.campaign, target, 'one', 'copy')
        self.assertEqual(self.dump(), before)

    def test_plain_and_counter_only_sources_do_not_copy_history(self):
        for head in (0, 9):
            with self.subTest(head=head):
                if head:
                    with self.storage.transaction():
                        self.storage._record_statblock_revision(self.monster(self.encounter), head)
                before = copy.deepcopy(self.api.load(self.encounter))
                name = self.storage.transfer_setup(self.campaign, self.campaign, 'one', 'copy')
                owner = self.owner(self.campaign, name)
                self.assertEqual(self.api.load(owner)[PRIVATE_KEY], {})
                self.assertEqual(self.storage._statblock_revision_head(self.monster(owner)), 0)
                self.assertEqual(self.storage._statblock_revision_head(self.monster(self.encounter)), head)
                self.assertEqual(self.api.load(self.encounter), before)

    def test_missing_or_wrong_campaign_source_does_not_write(self):
        self.seed(); other = self.storage.create_campaign('Other', '', 'now'); before = self.dump()
        for source, name in ((other, 'one'), (self.campaign, 'missing')):
            with self.subTest(source=source, name=name):
                with self.assertRaises(FileNotFoundError):
                    self.storage.transfer_setup(source, other, name, 'copy')
                self.assertEqual(self.dump(), before)

    def test_cross_campaign_cleanup_and_collision_name_are_preserved(self):
        state = self.seed()
        state['monsters'][0]['effects'] = [
            dict(id='normal',name='Normal',source_id='external',notes='',public=False,concentration=False,timing='manual',turns=None,anchor_id=None),
            dict(id='concentration',name='Concentration',source_id='external',notes='',public=False,concentration=True,timing='manual',turns=None,anchor_id=None),
        ]
        self.api.save(self.encounter, state); before = self.api.load(self.encounter)
        target = self.storage.create_campaign('Other', '', 'now')
        self.storage.save_setup(target, 'one', {'monsters':[{'id':'existing','hp':1}]})
        existing = self.storage.load_setup(target, 'one')
        name = self.storage.transfer_setup(self.campaign, target, 'one', 'copy')
        self.assertEqual(name, 'one-2'); self.assertEqual(self.storage.load_setup(target, 'one'), existing)
        copied = self.api.load(self.owner(target, name))
        self.assertEqual([effect['id'] for effect in copied['monsters'][0]['effects']], ['normal'])
        self.assertIsNone(copied['monsters'][0]['effects'][0]['source_id'])
        self.assertEqual(copied[PRIVATE_KEY]['m']['content_digest'], before[PRIVATE_KEY]['m']['content_digest'])
        self.assertEqual(self.api.load(self.encounter), before)


if __name__ == '__main__': unittest.main()
