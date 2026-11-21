"""SG-TODO-029: distinct default monster colors (palette rule and CSV import)."""
import asyncio
import re
import types
import unittest
from pathlib import Path

import test_bughunt_round11 as csv_fixture
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_monster_palette import PALETTE, fill_missing_colors, next_monster_color, spread_copy_colors

ROOT = Path(__file__).resolve().parents[1]


def contrast_with_white(color):
    def channel(value):
        value /= 255
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(int(color[i:i + 2], 16)) for i in (1, 3, 5))
    return 1.05 / (0.2126 * r + 0.7152 * g + 0.0722 * b + 0.05)


class PaletteRuleTests(unittest.TestCase):
    def test_palette_is_twelve_distinct_colors_readable_with_white_text(self):
        self.assertEqual(len(PALETTE), 12)
        self.assertEqual(len(set(PALETTE)), 12)
        for color in PALETTE:
            self.assertRegex(color, r'^#[0-9a-f]{6}$')
            self.assertGreaterEqual(contrast_with_white(color), 4.5, color)

    def test_empty_setup_starts_with_the_first_color(self):
        self.assertEqual(next_monster_color([]), PALETTE[0])

    def test_first_unused_color_and_case_insensitive_matching(self):
        self.assertEqual(next_monster_color([PALETTE[0].upper(), PALETTE[2]]), PALETTE[1])
        self.assertEqual(next_monster_color(['#000000', None, '']), PALETTE[0])

    def test_least_used_when_the_palette_is_full(self):
        used = list(PALETTE) * 2 + [c for c in PALETTE if c != PALETTE[5]]
        self.assertEqual(next_monster_color(used), PALETTE[5])
        self.assertEqual(next_monster_color(list(PALETTE)), PALETTE[0])

    def test_rows_without_a_color_each_get_the_next_default(self):
        rows = [{'color': ''}, {'color': PALETTE[2]}, {'color': ''}, {}]
        fill_missing_colors(rows, [{'color': PALETTE[0]}])
        self.assertEqual([row['color'] for row in rows], [PALETTE[1], PALETTE[2], PALETTE[3], PALETTE[4]])

    def test_copies_each_get_the_next_color_only_with_the_computed_default(self):
        existing = [{'color': PALETTE[0]}, {'color': PALETTE[2]}]
        copies = [{'color': PALETTE[1]} for _ in range(4)]
        spread_copy_colors(copies, existing, 'true')
        self.assertEqual([c['color'] for c in copies], [PALETTE[1], PALETTE[3], PALETTE[4], PALETTE[5]])
        for auto in ('', None, 'false'):
            picked = [{'color': '#00ff00'} for _ in range(3)]
            spread_copy_colors(picked, existing, auto)
            self.assertEqual({c['color'] for c in picked}, {'#00ff00'}, auto)

    def test_browser_copy_uses_the_same_palette(self):
        source = (ROOT / 'static/monster-default-color.js').read_text(encoding='utf-8')
        self.assertEqual(tuple(re.findall(r"'(#[0-9a-f]{6})'", source)), PALETTE)
        end = (ROOT / 'templates/admin/190_document_end.html').read_text(encoding='utf-8')
        self.assertEqual(end.count('/static/monster-default-color.js?v=2'), 1)
        self.assertIn('window.scryingMonsterColorState?.(latest);',
                      (ROOT / 'static/admin/030-source.js').read_text(encoding='utf-8'))


def fake_fastapi():
    """Minimal fastapi stand-in so the handlers import where FastAPI is not installed."""
    import importlib.util
    if importlib.util.find_spec('fastapi') is not None:
        return {}
    class FormParameter:
        def __init__(self, default=None, **_):
            self.default = default
    class HTTPException(Exception):
        def __init__(self, status_code, detail=None):
            super().__init__(detail)
            self.status_code, self.detail = status_code, detail
    fastapi = types.ModuleType('fastapi')
    params = types.ModuleType('fastapi.params')
    fastapi.Form = FormParameter
    fastapi.File = FormParameter
    fastapi.UploadFile = fastapi.Request = object
    fastapi.HTTPException = HTTPException
    fastapi.params = params
    params.Form = FormParameter
    return {'fastapi': fastapi, 'fastapi.params': params}


class QuantityColorTests(unittest.IsolatedAsyncioTestCase):
    """Add Monster and Import .monster with quantity > 1 (user finding 2026-11-21)."""

    def setUp(self):
        import sys
        import uuid
        from unittest.mock import AsyncMock, Mock, patch
        patcher = patch.dict(sys.modules, fake_fastapi())
        patcher.start()
        self.addCleanup(patcher.stop)
        from python.scrying_glass_monster_selection import CandidateMonstersMixin
        from python.scrying_glass_admin_monsters import AdminMonstersMixin
        from python.scrying_glass_service_images import ImagesService
        self.context = types.SimpleNamespace(
            uuid=uuid, HTTPException=sys.modules['fastapi'].HTTPException,
            STATE=dict(monsters=[{'id': 'old', 'color': PALETTE[0]}], characters=[{'id': 'pc', 'color': PALETTE[1]}],
                       battle_order=[]),
            hp_value_factory=Mock(return_value=Mock(return_value=20)), dnd_image=Mock(return_value=None),
            save_image=Mock(return_value=None), combatants_changed=AsyncMock(),
            parse_monster=Mock(return_value={'name': 'Spider', 'monster_species': 'spider', 'ac': 13, 'hp': 26,
                                             'max_hp': 26, 'original_hp': 26}))
        images = ImagesService(self.context)
        self.context.make_monster = images.make_monster
        self.context.make_monsters = images.make_monsters
        self.create = CandidateMonstersMixin()
        self.create.context = self.context
        self.importer = AdminMonstersMixin()
        self.importer.context = self.context
        self.arguments = dict(name='Goblin', monster_species='goblin', ac=12, hprangestart='7', hprangeend='',
                              quantity=3, image=None, selection_token='manual')

    def colors(self, created):
        return [monster['color'] for monster in created]

    async def test_add_monster_copies_get_distinct_colors_with_the_default(self):
        created = await self.create.create_monster(**self.arguments, color=PALETTE[1], color_auto='true')
        self.assertEqual(self.colors(created), [PALETTE[1], PALETTE[2], PALETTE[3]])  # characters do not count

    async def test_add_monster_hand_picked_color_stays_on_every_copy(self):
        created = await self.create.create_monster(**self.arguments, color='#00ff00')
        self.assertEqual(self.colors(created), ['#00ff00'] * 3)

    async def test_import_monster_copies_get_distinct_colors_with_the_default(self):
        from unittest.mock import patch
        async def read(size=-1):
            return b'{}'
        upload = types.SimpleNamespace(filename='spider.monster', read=read)
        with patch('python.scrying_glass_statblock_collecting.collect_after_add'):
            created = await self.importer.import_monster(monster_file=upload, color=PALETTE[1], quantity=3,
                                                         image=None, color_auto='true')
            picked = await self.importer.import_monster(monster_file=upload, color='#00ff00', quantity=2,
                                                        image=None, color_auto='')
        self.assertEqual(self.colors(created), [PALETTE[1], PALETTE[2], PALETTE[3]])
        self.assertEqual(self.colors(picked), ['#00ff00'] * 2)


class CsvDefaultColorTests(unittest.TestCase):
    setUp = csv_fixture.CsvLairIdentityTests.setUp
    tearDown = csv_fixture.CsvLairIdentityTests.tearDown

    def test_csv_rows_without_a_color_get_distinct_defaults(self):
        used = [monster.get('color') for monster in self.c.STATE['monsters']]
        raw = ('id,name,monster_species,ac,hp,color\n'
               'csv-a,A,goblin,12,7,\ncsv-b,B,goblin,12,7,#123456\ncsv-c,C,goblin,12,7,\n').encode()

        async def read(size=-1):
            return raw if size < 0 else raw[:size]
        handler = csv_fixture.load_class('scrying_glass_admin_monsters.py', 'AdminMonstersMixin')()
        handler.context = self.c
        asyncio.run(transactional_handler(self.c, handler.import_monsters_csv)(
            types.SimpleNamespace(filename='import.csv', read=read)))
        first = next_monster_color(used)
        second = next_monster_color(used + [first, '#123456'])
        self.assertEqual(self.c.entity('csv-a')['color'], first)
        self.assertEqual(self.c.entity('csv-b')['color'], '#123456')
        self.assertEqual(self.c.entity('csv-c')['color'], second)
        self.assertNotEqual(first, second)


if __name__ == '__main__':
    unittest.main()
