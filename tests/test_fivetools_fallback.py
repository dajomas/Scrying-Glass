"""Offline tests for provider ordering, parsing and image fallback."""
import ast
import asyncio
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from python import scrying_glass_fivetools as ft

ROOT = Path(__file__).resolve().parents[1]
def method(path, cls, name):
    tree = ast.parse((ROOT / path).read_text())
    node = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == cls)
    fn = next(x for x in node.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x.name == name)
    m = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), fn], type_ignores=[])
    ns = {"__name__": "python.test_provider", "__package__": "python"}
    exec(compile(ast.fix_missing_locations(m), path, "exec"), ns)
    return ns[name]

class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.mon = {"name": "Crawling Claw", "source": "MM", "ac": [{"ac": 12}], "hp": {"formula": "1d4", "average": 2}, "hasToken": True}
    def test_dice(self):
        self.assertEqual(ft.stats(self.mon), (12, "1d4", "dice"))
    def test_average(self):
        self.mon["hp"].pop("formula")
        self.assertEqual(ft.stats(self.mon), (12, "2", "average"))
    def test_special(self):
        self.assertEqual(ft.stats({"ac": [{"special": "varies"}], "hp": {"special": "varies"}}), (None, None, None))
    def test_exact_and_source_order(self):
        with patch.object(ft, "load_json", side_effect=[{"MM": "bestiary-mm.json"}, {"monster": [self.mon]}]):
            self.assertEqual(ft.lookup(" crawling CLAW ", {})["source"], "MM")
    def test_no_fuzzy(self):
        with patch.object(ft, "load_json", side_effect=[{"MM": "bestiary-mm.json"}, {"monster": [self.mon]}]):
            self.assertIsNone(ft.lookup("Claw", {}))
    def test_disabled(self):
        with patch.object(ft, "load_json") as get:
            self.assertIsNone(ft.lookup("Claw", {"fivetools_fallback": False}))
            get.assert_not_called()
    def test_token(self):
        self.assertEqual(ft.image_url(self.mon, {}), "https://5e.tools/img/bestiary/tokens/MM/Crawling%20Claw.webp")
    def test_explicit_token(self):
        self.mon["tokenUrl"] = "https://example.org/token.webp"
        self.assertEqual(ft.image_url(self.mon, {}), self.mon["tokenUrl"])
    def test_no_token(self):
        self.mon["hasToken"] = False
        self.assertIsNone(ft.image_url(self.mon, {}))
    def test_unresolved_copy(self):
        with patch.object(ft, "load_json", side_effect=[{"MM": "bestiary-mm.json"}, {"monster": [{"name": "Claw", "_copy": {}}]}]):
            self.assertIsNone(ft.lookup("Claw", {}))
    def test_cache(self):
        ft._CACHE.clear()
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.geturl.return_value = "https://5e.tools/data/test.json"
        response.read.return_value = b'{"monster": []}'
        with patch.object(ft, "urlopen", return_value=response) as get:
            ft.load_json("https://5e.tools/data/test.json")
            ft.load_json("https://5e.tools/data/test.json")
            self.assertEqual(get.call_count, 1)
    def test_image_fallback(self):
        fn = method("python/scrying_glass_service_images.py", "ImagesService", "dnd_image")
        obj = SimpleNamespace(context=SimpleNamespace(CONFIG={"display": {}}), _dndbeyond_image=Mock(return_value=None))
        with patch.object(ft, "lookup", return_value={"image_url": "https://example.org/token.webp"}) as fallback:
            self.assertEqual(fn(obj, "Claw"), "https://example.org/token.webp")
            self.assertTrue(fallback.call_args.kwargs["want_image"])
    def test_image_primary_wins(self):
        fn = method("python/scrying_glass_service_images.py", "ImagesService", "dnd_image")
        obj = SimpleNamespace(_dndbeyond_image=Mock(return_value="primary"))
        with patch.object(ft, "lookup") as fallback:
            self.assertEqual(fn(obj, "Claw"), "primary")
            fallback.assert_not_called()

class HandlerTests(unittest.IsolatedAsyncioTestCase):
    async def test_stats_fallback_after_search_failure(self):
        fn = method("python/scrying_glass_admin_display.py", "AdminDisplayMixin", "dndbeyond_monster_stats")
        ctx = SimpleNamespace(CONFIG={"display": {}}, dnd_monster_candidates=Mock(side_effect=OSError("offline")))
        with patch.object(ft, "lookup", return_value={"found": True, "provider": "5e.tools"}), self.assertLogs(level="WARNING"):
            result = await fn(SimpleNamespace(context=ctx), "Claw")
        self.assertEqual(result["provider"], "5e.tools")
    async def test_stats_primary_wins(self):
        fn = method("python/scrying_glass_admin_display.py", "AdminDisplayMixin", "dndbeyond_monster_stats")
        ctx = SimpleNamespace(CONFIG={"display": {}}, dnd_monster_candidates=Mock(return_value=[(True, "/monsters/claw")]), dnd_monster_detail_html=Mock(return_value="html"), dnd_monster_stats_from_html=Mock(return_value=(12, "1d4", "dice")))
        with patch.object(ft, "lookup") as fallback:
            result = await fn(SimpleNamespace(context=ctx), "Claw")
            fallback.assert_not_called()
        self.assertEqual(result["provider"], "D&D Beyond")

if __name__ == "__main__":
    unittest.main()
