""".monster bonus parsing and existing construction/import-path checks."""
import copy
import io
import json
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException, UploadFile
from python.scrying_glass_admin_monsters import AdminMonstersMixin
from python.scrying_glass_monster_csv import parse_monster
from python.scrying_glass_monster_initiative import normalize_initiative
from python.scrying_glass_service_images import ImagesService


def file_data(**changes):
    data = dict(name="Dragon", type="dragon", ac=18, hp=20)
    data.update(changes)
    return json.dumps(data).encode()


class MonsterFileBonusTests(unittest.TestCase):
    def test_legacy_file_result_unchanged(self):
        self.assertEqual(parse_monster(file_data()), dict(name="Dragon", monster_species="dragon", ac=18, hp=20))

    def test_explicit_signed_bonus(self):
        for value in (12,-2,0):
            with self.subTest(value=value):
                result = parse_monster(file_data(initiative_bonus=value))
                self.assertEqual(result["initiative_bonus"], value)
                self.assertEqual(result["initiative_bonus_origin"], "import")

    def test_signed_integer_text(self):
        self.assertEqual(parse_monster(file_data(initiative_bonus="+12"))["initiative_bonus"], 12)

    def test_malformed_explicit_bonus_rejected(self):
        for value in (None,True,1.5,[],{},"12 bonus","2.0"):
            with self.subTest(value=value):
                with self.assertRaises(HTTPException) as error:
                    parse_monster(file_data(initiative_bonus=value))
                self.assertEqual(error.exception.status_code, 400)

    def test_no_dexterity_or_ambiguous_initiative_derivation(self):
        result = parse_monster(file_data(dex=30, dexterity=30, initiative=12))
        self.assertNotIn("initiative_bonus", result)

    def test_duplicate_bonus_key_rejected(self):
        raw = b'{"name":"Dragon","type":"dragon","ac":18,"hp":20,"initiative_bonus":2,"initiative_bonus":3}'
        with self.assertRaises(HTTPException):
            parse_monster(raw)

    def test_bom_and_blank_bonus(self):
        result = parse_monster(b"\xef\xbb\xbf"+file_data(initiative_bonus=""))
        self.assertEqual(result["initiative_bonus_origin"], "default")
        self.assertEqual(result["initiative_bonus"], 0)

    def test_zero_hp_and_ac_preserved(self):
        result = parse_monster(file_data(hp=0, ac=0, initiative_bonus=-2))
        self.assertEqual((result["hp"], result["ac"], result["initiative_bonus"]), (0,0,-2))

    def test_bonus_origin_in_file_cannot_spoof_provider(self):
        result = parse_monster(file_data(initiative_bonus=12, initiative_bonus_origin="source", initiative_roll=16))
        self.assertEqual(result["initiative_bonus_origin"], "import")
        self.assertNotIn("initiative_roll", result)


class ImportedConstructionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.context = SimpleNamespace(uuid=uuid, HTTPException=HTTPException,
            STATE=dict(monsters=[], characters=[], battle_order=[]),
            save_image=Mock(return_value="/media/new.png"), dnd_image=Mock(return_value=None),
            parse_monster=parse_monster, combatants_changed=AsyncMock())
        self.images = ImagesService(self.context)
        self.context.make_monster = self.images.make_monster
        self.context.make_monsters = self.images.make_monsters
        self.handler = AdminMonstersMixin()
        self.handler.context = self.context

    async def test_parsed_bonus_reaches_existing_constructor(self):
        for bonus in (-2,0,12):
            with self.subTest(bonus=bonus):
                fields = parse_monster(file_data(initiative_bonus=bonus))
                before = copy.deepcopy(fields)
                item = self.images.make_monster(fields, "#842029", None)
                self.assertEqual(item["initiative_bonus"], bonus)
                self.assertEqual(item["initiative_bonus_origin"], "import")
                self.assertIsNone(item["initiative"])
                self.assertIsNone(item.get("initiative_roll"))
                self.assertEqual(fields, before)

    async def test_quantity_import_path_preserves_bonus_and_unique_ids(self):
        upload = UploadFile(filename="dragon.monster", file=io.BytesIO(file_data(initiative_bonus=-2)))
        try:
            items = await self.handler.import_monster(monster_file=upload, color="#842029", quantity=3, image=None)
        finally:
            await upload.close()
        self.assertEqual([item["name"] for item in items], ["Dragon - 1","Dragon - 2","Dragon - 3"])
        self.assertEqual(len({item["id"] for item in items}), 3)
        self.assertTrue(all(item["initiative_bonus"] == -2 and item["initiative_bonus_origin"] == "import" for item in items))
        self.assertTrue(all(item["initiative"] is None and item.get("initiative_roll") is None for item in items))
        self.assertEqual(self.context.STATE["monsters"], items)
        self.context.combatants_changed.assert_awaited_once_with(monsters=True, characters=False)

    async def test_legacy_import_uses_existing_default_normalization(self):
        item = self.images.make_monster(parse_monster(file_data()), "#842029", None)
        normalized = normalize_initiative(item)
        self.assertEqual(normalized["initiative_bonus"], 0)
        self.assertEqual(normalized["initiative_bonus_origin"], "default")
        self.assertIsNone(normalized["initiative_roll"])
        self.assertIsNone(normalized["initiative"])

    async def test_invalid_import_rejected_before_media_lookup_or_append(self):
        upload = UploadFile(filename="dragon.monster", file=io.BytesIO(file_data(initiative_bonus=True)))
        image = SimpleNamespace(filename="new.png")
        try:
            with self.assertRaises(HTTPException) as error:
                await self.handler.import_monster(monster_file=upload, color="#842029", quantity=1, image=image)
        finally:
            await upload.close()
        self.assertEqual(error.exception.status_code, 400)
        self.context.save_image.assert_not_called()
        self.context.dnd_image.assert_not_called()
        self.context.combatants_changed.assert_not_awaited()
        self.assertEqual(self.context.STATE["monsters"], [])
