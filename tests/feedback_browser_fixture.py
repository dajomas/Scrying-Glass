"""Load real feedback dependencies for isolated browser fixtures."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def install_feedback(page):
    for name in ("admin-feedback-controller.js", "admin-feedback-view.js", "admin-feedback-admin.js"):
        page.add_script_tag(content=(ROOT / "static" / name).read_text(encoding="utf-8"))
    if not page.evaluate("Boolean(window.scryingAdminFeedback)"):
        raise AssertionError("Production feedback bootstrap did not initialize")
