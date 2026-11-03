"""Offline handler tests; no FastAPI installation or network required."""
import ast
import asyncio
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from python import scrying_glass_fivetools as ft

SOURCE = Path(__file__).resolve().parents[1] / "python/scrying_glass_admin_display.py"
tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "AdminDisplayMixin")
method = next(n for n in cls.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "dndbeyond_monster_stats")
module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), method], type_ignores=[])
namespace = {"__name__": "lookup_diagnostics_test", "__package__": "python"}
exec(compile(ast.fix_missing_locations(module), str(SOURCE), "exec"), namespace)
lookup = namespace["dndbeyond_monster_stats"]

class HTTPError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

class LookupTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ctx = SimpleNamespace(
            CONFIG={"display": {"fivetools_fallback": False}},
            HTTPException=HTTPError,
            dnd_monster_candidates=Mock(return_value=[(True, "/monsters/legacy"), (False, "/monsters/current")]),
            dnd_monster_detail_html=Mock(return_value="html"),
            dnd_monster_stats_from_html=Mock(return_value=(12, "1d4", "dice")),
        )
        self.handler = SimpleNamespace(context=self.ctx)
        fallback_patch = patch.object(ft, "lookup", return_value=None)
        self.fallback = fallback_patch.start()
        self.addCleanup(fallback_patch.stop)
        network_patch = patch.object(ft, "urlopen", side_effect=AssertionError("Network forbidden in offline diagnostics"))
        network = network_patch.start()
        self.addCleanup(network_patch.stop)
        self.addCleanup(network.assert_not_called)

    async def call(self):
        return await lookup(self.handler, " Crawling Claw ")

    async def test_success(self):
        result = await self.call()
        self.assertTrue(result["found"])
        self.assertEqual(result["species"], "Crawling Claw")
        self.assertEqual(result["hp"], "1d4")
        self.assertNotIn("reason", result)

    async def test_empty_search(self):
        self.ctx.dnd_monster_candidates.return_value = []
        result = await self.call()
        self.assertIn("No exact", result["reason"])
        self.ctx.dnd_monster_detail_html.assert_not_called()

    async def test_candidate_failure_falls_back(self):
        self.ctx.dnd_monster_detail_html.side_effect = [ValueError("redirected to private destination"), "html"]
        with self.assertLogs("lookup_diagnostics_test", level="WARNING"):
            result = await self.call()
        self.assertTrue(result["found"])
        self.assertFalse(result["legacy"])
        self.assertEqual(self.ctx.dnd_monster_detail_html.call_count, 2)

    async def test_all_retrieval_failures(self):
        self.ctx.dnd_monster_detail_html.side_effect = ValueError("secret remote detail")
        with self.assertLogs("lookup_diagnostics_test", level="WARNING") as logs:
            result = await self.call()
        self.assertFalse(result["found"])
        self.assertIn("legacy:", result["reason"])
        self.assertIn("current:", result["reason"])
        self.assertNotIn("secret", result["reason"])
        self.assertIn("secret remote detail", "\n".join(logs.output))

    async def test_unparsed_pages(self):
        self.ctx.dnd_monster_stats_from_html.return_value = (None, None, None)
        with self.assertLogs("lookup_diagnostics_test", level="WARNING"):
            result = await self.call()
        self.assertIn("AC/HP could not be parsed", result["reason"])

    async def test_search_exception(self):
        self.ctx.dnd_monster_candidates.side_effect = OSError("secret search failure")
        with self.assertLogs("lookup_diagnostics_test", level="WARNING"):
            result = await self.call()
        self.assertIn("could not be completed", result["reason"])
        self.assertNotIn("secret", result["reason"])

    async def test_disabled(self):
        self.ctx.CONFIG["display"]["dndbeyond_image_lookup"] = False
        result = await self.call()
        self.assertIn("disabled", result["reason"])
        self.ctx.dnd_monster_candidates.assert_not_called()

    async def test_partial_stats(self):
        self.ctx.dnd_monster_stats_from_html.return_value = (12, None, None)
        self.assertTrue((await self.call())["found"])

    async def test_cancellation(self):
        self.ctx.dnd_monster_candidates.side_effect = asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            await self.call()

    async def test_primary_success_does_not_call_fallback(self):
        self.ctx.CONFIG["display"]["fivetools_fallback"] = True
        result = await self.call()
        self.assertEqual(result["provider"], "D&D Beyond")
        self.fallback.assert_not_called()

    async def test_disabled_primary_can_still_use_fallback(self):
        self.ctx.CONFIG["display"].update(dndbeyond_image_lookup=False, fivetools_fallback=True)
        self.fallback.return_value = {"found": True, "provider": "5e.tools"}
        self.assertEqual((await self.call())["provider"], "5e.tools")
        self.ctx.dnd_monster_candidates.assert_not_called()
        self.fallback.assert_called_once_with("Crawling Claw", self.ctx.CONFIG["display"])

    async def test_empty_primary_search_can_still_use_fallback(self):
        self.ctx.CONFIG["display"]["fivetools_fallback"] = True
        self.ctx.dnd_monster_candidates.return_value = []
        self.fallback.return_value = {"found": True, "provider": "5e.tools"}
        result = await self.call()
        self.assertEqual(result, self.fallback.return_value)
        self.assertNotIn("reason", result)

    async def test_both_providers_disabled_do_no_lookup(self):
        self.ctx.CONFIG["display"].update(dndbeyond_image_lookup=False, fivetools_fallback=False)
        result = await self.call()
        self.assertFalse(result["found"])
        self.assertIn("all providers disabled", result["reason"])
        self.ctx.dnd_monster_candidates.assert_not_called()
        self.fallback.assert_not_called()

    async def test_fallback_exception_is_sanitized(self):
        self.ctx.CONFIG["display"].update(dndbeyond_image_lookup=False, fivetools_fallback=True)
        self.fallback.side_effect = OSError("secret fallback detail")
        with self.assertLogs("lookup_diagnostics_test", level="WARNING") as logs:
            result = await self.call()
        self.assertFalse(result["found"])
        self.assertNotIn("secret", result["reason"])
        self.assertIn("5e.tools", result["reason"])
        self.assertIn("secret fallback detail", "\n".join(logs.output))

    async def test_blank_species_is_rejected_before_providers(self):
        with self.assertRaises(HTTPError) as error:
            await lookup(self.handler, "  ")
        self.assertEqual(error.exception.status_code, 400)
        self.ctx.dnd_monster_candidates.assert_not_called()
        self.fallback.assert_not_called()

    async def test_fallback_runs_after_all_primary_candidates(self):
        self.ctx.CONFIG["display"]["fivetools_fallback"] = True
        events = []
        def detail(href):
            events.append(href)
            raise OSError("secret page detail")
        def fallback(*args):
            events.append("fallback")
            return {"found": True, "provider": "5e.tools"}
        self.ctx.dnd_monster_detail_html.side_effect = detail
        self.fallback.side_effect = fallback
        with self.assertLogs("lookup_diagnostics_test", level="WARNING"):
            result = await self.call()
        self.assertEqual(result["provider"], "5e.tools")
        self.assertEqual(events, ["/monsters/legacy", "/monsters/current", "fallback"])

    async def test_parser_exception_is_sanitized(self):
        self.ctx.dnd_monster_stats_from_html.side_effect = ValueError("secret parser detail")
        with self.assertLogs("lookup_diagnostics_test", level="WARNING") as logs:
            result = await self.call()
        self.assertFalse(result["found"])
        self.assertIn("legacy:", result["reason"])
        self.assertIn("current:", result["reason"])
        self.assertNotIn("secret", result["reason"])
        self.assertIn("secret parser detail", "\n".join(logs.output))

if __name__ == "__main__":
    unittest.main()
