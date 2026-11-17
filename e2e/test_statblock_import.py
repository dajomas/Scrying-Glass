"""Statblock import in the Admin against a real server (SG-TODO-022.13/022.14), Chromium and Firefox.

Online providers are off in the e2e configuration, so these flows use Tetra-cube
.monster files (monsters_examples/tetra-cube) prepared in the isolated worker.
"""
from pathlib import Path

import pytest
from playwright.sync_api import expect

from helpers import add_monster, admin, prepare_battle, row

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "monsters_examples" / "tetra-cube").glob("*.monster"))
pytestmark = pytest.mark.skipif(not FILES, reason="monsters_examples/tetra-cube not present")


def test_edit_monster_imports_a_monster_file_with_the_save(sessions, server):
    _, page = admin(sessions, "preparation")
    add_monster(page, "Spider", species="giant ice spider")
    row(page, "monsters", "Spider").locator("button[data-edit]").click()
    form = page.locator("#editForm")
    expect(form.locator(".monster-statblock-status")).to_contain_text("No statblock")
    form.locator(".monster-statblock-upload input").set_input_files(str(FILES[0]))
    review = page.get_by_role("dialog", name=f"Statblock: {FILES[0].name}")
    review.get_by_role("button", name="Use this statblock").click(timeout=20000)
    expect(form.locator(".monster-statblock-status")).to_contain_text("Save monster to apply")
    form.locator("[name=ac]").fill("16")
    form.get_by_role("button", name="Save monster").click()
    expect(page.locator("#editModal")).to_be_hidden()
    row(page, "monsters", "Spider").locator("button[data-edit]").click()
    expect(form.locator(".monster-statblock-status")).to_contain_text("Statblock saved (revision 1)")
    form.get_by_role("button", name="Cancel").click()


def test_bulk_import_shows_in_the_statblock_viewer(sessions, server):
    _, page = admin(sessions, "preparation")
    prepare_battle(page, characters=(), monsters=(("Owlbear", 10, 30), ("Basilisk", 8, 20)))
    for name in ("Owlbear", "Basilisk"):
        row(page, "monsters", name).locator("input.bulk-selection-checkbox").check()
    page.select_option("#monsterBulkAction", "load-statblocks")
    dialog = page.locator("dialog.monster-statblock-bulk")
    for name, file in (("Owlbear", FILES[1]), ("Basilisk", FILES[2])):
        section = dialog.locator(".monster-statblock-row").filter(has_text=name)
        section.locator("select").select_option("file")
        section.locator("input[type=file]").set_input_files(str(file))
        expect(section).to_contain_text("Ready:", timeout=20000)
    dialog.get_by_role("button", name="Apply statblocks (2)").click()
    expect(dialog).to_be_hidden()
    view = sessions("statblocks").login("admin", portal="statblocks")
    toggle = view.get_by_role("button", name="Owlbear")
    toggle.click()
    expect(view.locator(".sb-expanded .sb-statblock")).to_be_visible(timeout=15000)
    expect(view.locator(".sb-expanded [data-live='name']")).to_have_text("Owlbear")
