"""Bounded literal-core/override audit; not proof of all effective callers."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GlobalFeedbackCoreInventoryTests(unittest.TestCase):
    def test_literal_core_message_calls_are_confined_to_known_replaced_handlers(self):
        parts = sorted((ROOT / "static/admin").glob("*-source.js"))
        self.assertEqual(len(parts), 8)
        calls = {}
        for part in parts:
            matches = list(re.finditer(r"(?<![\w$.])message\s*\(", part.read_text(encoding="utf-8")))
            if matches:
                calls[part.name] = len(matches)
        self.assertEqual(calls, {"070-source.js": 8})
        source = (ROOT / "static/admin/070-source.js").read_text(encoding="utf-8")
        boundaries = [
            ("async function startBattle(", "document.querySelector('#startBattle').onclick", 1),
            ("document.querySelector('#startBattle').onclick", "document.querySelector('#confirmOrder').onclick", 1),
            ("document.querySelector('#confirmOrder').onclick", "document.querySelector('#cancelOrder').onclick", 1),
            ("document.querySelector('#nextBattle').onclick", "document.querySelector('#endBattle').onclick", 1),
            ("document.querySelector('#endBattle').onclick", "document.querySelector('#resetAll').onclick", 3),
            ("document.querySelector('#resetAll').onclick", "let battleOrderFontAdjustmentPending", 1),
        ]
        for start, end, count in boundaries:
            with self.subTest(handler=start):
                first = source.index(start)
                last = source.index(end, first)
                self.assertEqual(len(re.findall(r"(?<![\w$.])message\s*\(", source[first:last])), count)

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
