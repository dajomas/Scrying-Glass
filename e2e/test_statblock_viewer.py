"""Statblock listener against a real server (SG-TODO-022.09-022.12), Chromium and Firefox.

Providers are off in the e2e configuration, so tiles show "No statblock"; statblock
rendering itself is covered with fixtures in tests/test_statblock_viewer_browser.py.
"""
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import expect

from helpers import admin, prepare_battle

OVERFLOW = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"


def viewer(sessions, server):
    page = sessions("statblocks").login("admin", portal="statblocks")
    expect(page).to_have_url(server.statblocks + "/")
    return page


def test_only_regular_admins_sign_in(sessions, server):
    for role in ("superadmin", "client"):
        page = sessions(role).login(role, portal="statblocks")
        expect(page.locator("form")).to_contain_text("regular admin")
        page.goto(server.statblocks + "/")
        expect(page).to_have_url(server.statblocks + "/login")


def test_live_tiles_keyboard_and_axe(sessions, server):
    _, page = admin(sessions)
    view = viewer(sessions, server)
    expect(view.locator("#status")).to_have_text("No monsters in battle.", timeout=15000)
    prepare_battle(page, monsters=(("Orc", 10, 15), ("Goblin", 8, 7)))
    expect(view.locator(".sb-toggle .sb-name")).to_have_text(["Orc", "Goblin"], timeout=15000)
    first, second = view.locator(".sb-toggle").nth(0), view.locator(".sb-toggle").nth(1)
    first.focus()
    view.keyboard.press("ArrowRight")
    expect(second).to_be_focused()
    view.keyboard.press("Enter")
    expect(second).to_have_attribute("aria-expanded", "true")
    expect(view.locator(".sb-expanded .sb-panel")).to_contain_text("No statblock is saved")
    view.keyboard.press("Escape")
    expect(second).to_have_attribute("aria-expanded", "false")
    expect(second).to_be_focused()
    axe = Axe()
    for width in (360, 1440):
        view.set_viewport_size({"width": width, "height": 900})
        second.click()
        assert view.evaluate(OVERFLOW) <= 0, f"statblocks page scrolls horizontally at {width}px"
        violations = axe.run(view).response["violations"]
        assert not violations, f"axe violations at {width}px: {sorted(v['id'] for v in violations)}"
        second.click()


def test_sign_out_clears_the_page(sessions, server):
    view = viewer(sessions, server)
    expect(view.locator("#status")).not_to_have_text("Connecting…", timeout=15000)
    view.click(".sb-signout")
    expect(view).to_have_url(server.statblocks + "/login")
