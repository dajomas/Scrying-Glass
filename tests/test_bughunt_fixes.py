"""Regression coverage for the 72504c1 bug-hunt fixes (real SQLite)."""
import ast
import asyncio
import copy
import io
import json
import types
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import test_encounter_features as fixture
from test_sqlite_storage import HTTPError
from python.scrying_glass_admin_setups import AdminSetupsMixin
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_feature_rules import apply_hp
from python.scrying_glass_turn_rules import permanently_dead, can_take_turn


def load_class(path, name, scope=None):
    tree = ast.parse(path.read_text())
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == name)
    namespace = dict(scope or {})
    future = ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)
    module = ast.fix_missing_locations(ast.Module(body=[future, cls], type_ignores=[]))
    exec(compile(module, str(path), 'exec'), namespace)
    return namespace[name]


class BugHuntFixTests(unittest.TestCase):
    setUp = fixture.FeatureTests.setUp
    tearDown = fixture.FeatureTests.tearDown
    call = fixture.FeatureTests.call
    item = fixture.FeatureTests.item
    effect = fixture.FeatureTests.effect

    def rename(self, old='default', new='renamed'):
        handler = AdminSetupsMixin()
        handler.context = self.c
        payload = types.SimpleNamespace(campaign=self.c.active_campaign(), name=old, new_name=new)
        return asyncio.run(transactional_handler(self.c, handler.rename_setup)(payload))

    def restore(self, ident):
        preview = self.f.preview_checkpoint(ident)
        return self.call('restore_checkpoint', ident, {'confirm': True, 'revision': preview['revision']})

    def test_checkpoint_restores_after_rename(self):
        ident = self.call('save_checkpoint', {'name': 'Recovery'})['id']
        self.rename()
        self.assertEqual(self.f.preview_checkpoint(ident)['active_setup']['name'], 'renamed')
        self.restore(ident)
        self.assertEqual(self.c.STATE['active_setup']['name'], 'renamed')

    def test_checkpoint_rename_is_campaign_scoped(self):
        ident = self.call('save_checkpoint', {'name': 'Recovery'})['id']
        other = self.c.STORAGE.create_campaign('Other', '', self.c.now_iso())
        self.c.STORAGE.save_setup(other, 'default', self.c.setup_snapshot(self.c.STATE))
        other_id = self.f.store.save_snapshot(other, self.c.STATE, 'checkpoint', 'Other recovery')
        self.rename()
        self.assertEqual(self.f.store.load(ident, self.c.active_campaign(), 'checkpoint')['active_setup']['name'], 'renamed')
        self.assertEqual(self.f.store.load(other_id, other, 'checkpoint')['active_setup']['name'], 'default')

    def test_checkpoint_rename_rolls_back_with_transaction(self):
        ident = self.call('save_checkpoint', {'name': 'Recovery'})['id']
        with self.assertRaises(RuntimeError):
            with self.c.STORAGE.transaction():
                self.c.STORAGE.rename_setup(self.c.active_campaign(), 'default', 'renamed')
                raise RuntimeError('abort')
        self.assertTrue(self.c.STORAGE.setup_exists(self.c.active_campaign(), 'default'))
        self.assertEqual(self.f.preview_checkpoint(ident)['active_setup']['name'], 'default')
        self.restore(ident)

    def test_checkpoint_rename_survives_restart(self):
        ident = self.call('save_checkpoint', {'name': 'Recovery'})['id']
        self.rename()
        cls = type(self.c.STORAGE)
        self.c.STORAGE.close()
        self.c.STORAGE = cls(Path(self.tmp.name)/'scrying-glass.sqlite3')
        self.c.load_state()
        self.restore(ident)
        self.assertEqual(self.c.STATE['active_setup']['name'], 'renamed')

    def batch(self, damage, heal):
        self.c.datetime = datetime
        self.c.timezone = timezone
        directory = Path(__file__).resolve().parents[1]/'python'
        activity = load_class(directory/'scrying_glass_service_activity.py', 'ActivityService')
        self.c.log_battle_action = activity(self.c).log_battle_action
        battle = load_class(directory/'scrying_glass_admin_battle.py', 'AdminBattleMixin',
                            dict(apply_hp=apply_hp, permanently_dead=permanently_dead, can_take_turn=can_take_turn))
        handler = battle()
        handler.context = self.c
        payload = types.SimpleNamespace(actor_id='c', actions=[
            types.SimpleNamespace(target_id='c', action='damage', amount=damage, critical_hit=False),
            types.SimpleNamespace(target_id='c', action='heal', amount=heal, critical_hit=False),
        ])
        return asyncio.run(transactional_handler(self.c, handler.apply_battle_actions)(payload))

    def test_batch_down_then_heal_ends_concentration(self):
        self.call('add_effect', 'm', {**self.effect(), 'concentration': True})
        self.batch(20, 5)
        self.assertEqual(self.item('c')['hp'], 5)
        self.assertFalse(self.item('c')['concentrating'])
        self.assertEqual(self.item()['effects'], [])
        self.assertFalse(self.c.STORAGE.load_characters(self.c.active_campaign())[0]['concentrating'])
        self.assertEqual(self.c.STORAGE.load_setup(self.c.active_campaign(), 'default')['monsters'][0]['effects'], [])

    def test_non_downing_batch_keeps_concentration(self):
        self.call('add_effect', 'm', {**self.effect(), 'concentration': True})
        self.batch(1, 5)
        self.assertTrue(self.item('c')['concentrating'])
        self.assertEqual(len(self.item()['effects']), 1)

    def test_batch_undo_restores_concentration_and_effects(self):
        self.call('add_effect', 'm', {**self.effect(), 'concentration': True})
        self.batch(20, 5)
        self.call('undo', {'id': self.f.summary()['undo']['id']})
        self.assertEqual(self.item('c')['hp'], 20)
        self.assertTrue(self.item('c')['concentrating'])
        self.assertEqual(len(self.item()['effects']), 1)

    def manifest(self, raw):
        with zipfile.ZipFile(io.BytesIO(raw)) as bundle:
            return json.loads(bundle.read('campaign.json')), bundle.namelist()

    def test_free_text_does_not_require_media(self):
        text = 'Goblin /media/not-a-file.png'
        self.item()['name'] = text
        self.call('add_effect', 'm', {**self.effect(), 'notes': text})
        raw = self.f.export_bundle()
        manifest, names = self.manifest(raw)
        self.assertEqual(names, ['campaign.json'])
        self.assertEqual(manifest['encounter']['monsters'][0]['name'], text)
        result = self.call('import_bundle', raw)
        checkpoint = self.f.store.load(result['checkpoint_id'], result['campaign_id'], 'checkpoint')
        self.assertEqual(checkpoint['monsters'][0]['name'], text)
        self.assertEqual(checkpoint['monsters'][0]['effects'][0]['notes'], text)

    def test_media_rewritten_but_matching_text_preserved(self):
        url = '/media/goblin.png'
        (self.c.UPLOAD_DIR/'goblin.png').write_bytes(b'image fixture')
        self.item()['image_url'] = url
        self.item()['name'] = 'See '+url
        self.c.STATE['display']['background'] = 'url("'+url+'") center / cover'
        self.call('add_effect', 'm', {**self.effect(), 'notes': url})
        raw = self.f.export_bundle()
        _, names = self.manifest(raw)
        self.assertIn('media/goblin.png', names)
        result = self.call('import_bundle', raw)
        checkpoint = self.f.store.load(result['checkpoint_id'], result['campaign_id'], 'checkpoint')
        monster = checkpoint['monsters'][0]
        self.assertNotEqual(monster['image_url'], url)
        self.assertEqual(monster['name'], 'See '+url)
        self.assertEqual(monster['effects'][0]['notes'], url)
        self.assertIn(monster['image_url'], checkpoint['display']['background'])

    def test_external_media_urls_are_not_local_dependencies(self):
        external = 'https://example.invalid/media/remote.png'
        self.item()['image_url'] = external
        self.c.STATE['display']['background'] = 'url("'+external+'")'
        self.c.save_active_setup_monsters()
        raw = self.f.export_bundle()
        manifest, names = self.manifest(raw)
        self.assertEqual(names, ['campaign.json'])
        self.assertEqual(manifest['encounter']['monsters'][0]['image_url'], external)
        result = self.call('import_bundle', raw)
        checkpoint = self.f.store.load(result['checkpoint_id'], result['campaign_id'], 'checkpoint')
        self.assertEqual(checkpoint['monsters'][0]['image_url'], external)
        self.assertIn(external, checkpoint['display']['background'])


if __name__ == '__main__':
    unittest.main()
