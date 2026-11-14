"""Image-picking lookups keep working providers; stats lookups stay fail-closed."""
import unittest
from unittest.mock import Mock
from python.scrying_glass_combined_lookup import combined_candidates


def candidate(provider):
    return dict(provider=provider, source="MM", species="Shadow", image_url="https://img.test/" + provider)


def timeout():
    try:
        raise TimeoutError("The read operation timed out")
    except TimeoutError as exc:
        raise RuntimeError("Open5e did not respond") from exc


class ImageLookupPartialTests(unittest.TestCase):
    def lookup(self, **options):
        return combined_candidates(Mock(return_value=[candidate("D&D Beyond")]),
                                   Mock(return_value=[candidate("5e.tools")]),
                                   extra=(("Open5e", True, timeout),), **options)

    def test_stats_lookup_still_offers_nothing_when_a_provider_fails(self):
        """Without partial mode one failed provider suppresses every candidate."""
        result = self.lookup()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["candidates"], [])

    def test_image_lookup_returns_working_providers_with_a_warning(self):
        """Partial mode returns the providers that answered and names the failed one."""
        result = self.lookup(partial=True)
        self.assertEqual(result["status"], "ok")
        self.assertEqual([c["provider"] for c in result["candidates"]], ["D&D Beyond", "5e.tools"])
        self.assertEqual(result["failed"], ["Open5e"])
        self.assertIn("Open5e", result["warning"])

    def test_image_lookup_is_an_error_when_every_provider_fails(self):
        """Partial mode still reports an error when no enabled provider answered."""
        result = combined_candidates(timeout, timeout, partial=True)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["candidates"], [])

    def test_timeouts_are_logged_as_one_line_without_a_traceback(self):
        """A network timeout is logged once as a short warning, not a traceback."""
        with self.assertLogs("python.scrying_glass_combined_lookup", "WARNING") as logs:
            self.lookup(partial=True)
        self.assertEqual(len(logs.records), 1)
        self.assertIsNone(logs.records[0].exc_info)
        self.assertIn("Open5e did not respond (The read operation timed out)", logs.output[0])
