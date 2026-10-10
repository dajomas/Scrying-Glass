"""Regression checks for stored character HP and canonical bundle members."""
import ast
import asyncio
import io
import json
import types
import unittest
import zipfile
from pathlib import Path
import test_encounter_features as fixture
from test_sqlite_storage import HTTPError
from python.scrying_glass_classes import CharacterUpdate,MAX_STORED_HP
from python.scrying_glass_turn_rules import can_take_turn
from python.scrying_glass_database_transactions import transactional_handler

class CharacterHpCompatibilityTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown
    call=fixture.FeatureTests.call

    def test_edit_preserves_hp_produced_by_valid_healing(self):
        self.call('edit_features','c',{'hp_delta':99999})
        self.assertEqual(self.c.entity('c')['hp'],100019)
        update=CharacterUpdate(name='Renamed cleric',hp=100019,max_hp=20)
        path=Path(__file__).resolve().parents[1]/'python/scrying_glass_admin_characters.py'
        cls=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.ClassDef))
        future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
        scope=dict(Form=lambda *a,**kw:None,File=lambda *a,**kw:None,
                   can_take_turn=can_take_turn,__package__='python')
        exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),str(path),'exec'),scope)
        handler=scope['AdminCharactersMixin']();handler.context=self.c
        asyncio.run(transactional_handler(self.c,handler.update_character)('c',update))
        character=self.c.STORAGE.load_characters(self.c.active_campaign())[0]
        self.assertEqual(character['name'],'Renamed cleric')
        self.assertEqual(character['hp'],100019)

    def test_current_hp_accepts_storage_endpoint(self):CharacterUpdate(hp=MAX_STORED_HP)

    def test_invalid_current_hp_is_rejected(self):
        for value in (-1,MAX_STORED_HP+1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):CharacterUpdate(hp=value)

    def test_other_character_limits_remain_unchanged(self):
        for values in ({'max_hp':100000},{'hp_delta':100000}):
            with self.assertRaises(ValueError):CharacterUpdate(**values)

class BundleMemberPathTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown
    call=fixture.FeatureTests.call

    def bundle(self,paths):
        with zipfile.ZipFile(io.BytesIO(self.f.export_bundle())) as archive:
            payload=json.loads(archive.read('campaign.json'))
        payload['setups']['default']['monsters'][0]['image_url']='/media/portrait.png'
        payload['encounter']['monsters'][0]['image_url']='/media/portrait.png'
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('campaign.json',json.dumps(payload))
            for name,data in paths:archive.writestr(name,data)
        return out.getvalue()

    def reject(self,paths):
        before=self.c.read_campaigns();revision=self.f.store.revision()
        with self.assertRaises(HTTPError) as error:self.call('import_bundle',self.bundle(paths))
        self.assertEqual(error.exception.status_code,422)
        self.assertEqual(self.c.read_campaigns(),before)
        self.assertEqual(self.f.store.revision(),revision)
        self.assertEqual(list(self.c.UPLOAD_DIR.iterdir()),[])

    def test_repeated_separator_path_is_rejected(self):self.reject([('media//portrait.png',b'fixture')])
    def test_dot_segment_path_is_rejected(self):self.reject([('media/./portrait.png',b'fixture')])
    def test_directory_member_cannot_masquerade_as_image(self):self.reject([('media/portrait.png/',b'')])
    def test_aliased_duplicate_members_are_rejected(self):
        self.reject([('media/portrait.png',b'first'),('media//portrait.png',b'second')])

    def test_canonical_media_file_remains_supported(self):
        result=self.call('import_bundle',self.bundle([('media/portrait.png',b'fixture')]))
        monster=self.c.STORAGE.load_setup(result['campaign_id'],'default')['monsters'][0]
        path=self.c.UPLOAD_DIR/monster['image_url'].split('/')[-1]
        self.assertEqual(path.read_bytes(),b'fixture')
        self.assertNotEqual(monster['image_url'],'/media/portrait.png')

if __name__=='__main__':unittest.main()
