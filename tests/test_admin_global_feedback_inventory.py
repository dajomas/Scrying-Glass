"""Bounded literal-core/override audit; not proof of all effective callers."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GlobalFeedbackCoreInventoryTests(unittest.TestCase):
    def test_core_has_no_untyped_message_or_pane_notification_calls(self):
        # Stage 4: the superseded 070 handlers were removed and untyped delivery is retired.
        parts = sorted((ROOT / "static/admin").glob("*-source.js"))
        self.assertEqual(len(parts), 8)
        calls, pane = {}, {}
        for part in parts:
            text = part.read_text(encoding="utf-8")
            matches = list(re.finditer(r"(?<![\w$.])message\s*\(", text))
            if matches:
                calls[part.name] = len(matches)
            # Every remaining paneNotification call passes a third (ticket/severity) argument.
            for match in re.finditer(r"(?<![\w$.])paneNotification\(([^;]*)\);", text):
                if match.group(0).startswith("paneNotification(kind, text, options)"):
                    continue
                if "{ticket" not in match.group(1) and "options" not in match.group(1):
                    pane.setdefault(part.name, []).append(match.group(0)[:80])
        self.assertEqual(calls, {})
        self.assertEqual(pane, {})
        for asset in ("setup-switch.js", "features.js", "lairs.js", "campaign-viewer-admin.js"):
            self.assertNotRegex((ROOT / "static" / asset).read_text(encoding="utf-8"), r"(?<![\w$.])paneNotification\(")

    def test_feedback_and_replacement_assets_keep_their_relative_template_order(self):
        directory = ROOT / "templates/admin"
        markup = (directory / "010_pane_controls.html").read_text(encoding="utf-8")
        markup += (directory / "190_document_end.html").read_text(encoding="utf-8")
        names = ["admin-feedback-controller.js", "admin-feedback-view.js", "admin-feedback-admin.js",
                 "initiative-join-gate.js", 'src="/static/admin.js"', "battle-actions-next.js",
                 "admin-initial-visibility.js", "admin-start-validation.js", "admin-end-feedback.js",
                 "admin-reset-all-feedback.js"]
        positions = [markup.index(name) for name in names]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(len(positions), len(set(positions)))

    def test_known_replacement_assignments_remain_explicit(self):
        contracts = {
            "admin-initial-visibility.js": ["startBattle = async function(order)"],
            "admin-start-validation.js": ["document.querySelector('#startBattle').onclick =",
                                          "document.querySelector('#confirmOrder').onclick ="],
            "battle-actions-next.js": ["main.onclick = () => next(false)", "button.onclick = () => next(true)"],
            "admin-end-feedback.js": ["const button = document.getElementById('endBattle')", "button.onclick = async () =>"],
            "admin-reset-all-feedback.js": ["const button = document.getElementById('resetAll')", "button.onclick = async () =>"],
        }
        for name, assignments in contracts.items():
            source = (ROOT / "static" / name).read_text(encoding="utf-8")
            for assignment in assignments:
                with self.subTest(asset=name, assignment=assignment):
                    self.assertIn(assignment, source)


if __name__ == "__main__":
    unittest.main()
