"""Responsive widths, dialog focus handling and automated accessibility scans (SG-TODO-021 Stage 4).

The axe scans must find no violations; the earlier baseline findings (docs/handover/610) are fixed
(docs/handover/640).
"""
import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import expect

from conftest import ACCOUNTS
from helpers import add_character, add_monster, admin, grant_viewer, open_workflow, row

WIDTHS = (360, 768, 1024, 1440)
WORKFLOWS = ("campaign", "preparation", "live")
OVERFLOW = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
# Workflow tabs and panel toggles must wrap inside the viewport, not run past its edge.
CLIPPED = """() => [...document.querySelectorAll('#adminWorkflowTabs button, .sg-pane-strip button')]
    .filter(node => node.getClientRects().length)
    .filter(node => { const box = node.getBoundingClientRect(); return box.left < -0.5 || box.right > innerWidth + 0.5; })
    .map(node => node.id || node.textContent.trim())"""

# Every scanned page must be free of axe violations (the Stage 4 baseline is fixed).
PAGES = ("login", "admin-campaign", "admin-preparation", "admin-live", "users", "client")


def no_horizontal_scroll(page, label):
    overflow = page.evaluate(OVERFLOW)
    assert overflow <= 0, f"{label}: page scrolls horizontally by {overflow}px"


@pytest.mark.parametrize("width", WIDTHS)
def test_pages_fit_viewport_width(sessions, server, width):
    """Admin, Client Display, login and Users pages fit the viewport width; header tabs and toggles wrap inside it."""
    size = {"width": width, "height": 900}
    login = sessions("anonymous").page()
    login.set_viewport_size(size)
    login.goto(server.admin + "/login")
    no_horizontal_scroll(login, "login")

    _, page = admin(sessions)
    page.set_viewport_size(size)
    add_character(page, "Aelwyn the Unusually Long-Named", initiative=12)
    add_monster(page, "Orc", quantity=2)
    for workflow in WORKFLOWS:
        open_workflow(page, workflow)  # Clicking the tab proves it is reachable at this width.
        page.wait_for_timeout(200)
        no_horizontal_scroll(page, f"admin {workflow}")
        clipped = page.evaluate(CLIPPED)
        assert not clipped, f"admin {workflow}: header controls outside the viewport: {clipped}"
        for toggle in page.locator("[aria-label='Panel visibility'] button:not([aria-haspopup]):visible").all():
            toggle.click()
            toggle.click()

    users = sessions("super").login("superadmin")
    users.set_viewport_size(size)
    expect(users).to_have_url(server.admin + "/users")
    no_horizontal_scroll(users, "users")

    display = sessions("viewer").login("client", portal="client")
    display.set_viewport_size(size)
    expect(display.locator("#displaySync")).to_contain_text("Live", timeout=15000)
    no_horizontal_scroll(display, "client")


def assert_focus_trapped(page, modal_id):
    inside = f"() => document.getElementById('{modal_id}').contains(document.activeElement)"
    assert page.evaluate(inside), "focus did not move into the dialog"
    for key in ["Tab"] * 12 + ["Shift+Tab"] * 12:
        page.keyboard.press(key)
        assert page.evaluate(inside), f"focus left the dialog after {key}"


def test_dialog_traps_focus_and_returns_it(sessions):
    """The statistics dialog takes focus, keeps Tab inside, closes on Escape and returns focus to its opener."""
    _, page = admin(sessions)
    add_character(page, "Borin", initiative=12)
    open_workflow(page, "preparation")
    opener = row(page, "characters", "Borin").locator("button[data-statistics]")
    opener.click()
    expect(page.locator("#statisticsModal")).to_be_visible()
    assert_focus_trapped(page, "statisticsModal")
    page.keyboard.press("Escape")
    expect(page.locator("#statisticsModal")).to_be_hidden()
    expect(opener).to_be_focused()


def test_campaign_dialog_traps_focus_and_closes_on_escape(sessions):
    """The New campaign dialog takes focus, keeps Tab inside and closes on Escape."""
    _, page = admin(sessions)
    page.click("#newCampaign")
    expect(page.locator("#campaignModal")).to_be_visible()
    assert_focus_trapped(page, "campaignModal")
    page.keyboard.press("Escape")
    expect(page.locator("#campaignModal")).to_be_hidden()


def test_campaign_dialog_returns_focus_to_opener(sessions):
    """Closing the New campaign dialog returns focus to the New campaign button."""
    _, page = admin(sessions)
    opener = page.locator("#newCampaign")
    opener.click()
    expect(page.locator("#campaignModal")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator("#campaignModal")).to_be_hidden()
    expect(opener).to_be_focused(timeout=2000)


def test_axe_scan_finds_no_violations(sessions, server):
    """Automated axe scans of login, Admin, Users and Client Display find no violations."""
    axe = Axe()
    found = {}

    def scan(page, label):
        violations = axe.run(page).response["violations"]
        found[label] = {item["id"] for item in violations}

    login = sessions("anonymous").page()
    login.goto(server.admin + "/login")
    scan(login, "login")
    _, page = admin(sessions)
    grant_viewer(page, ACCOUNTS["client"][0])
    add_character(page, "Borin", initiative=12)
    add_monster(page, "Orc")
    for workflow in WORKFLOWS:
        open_workflow(page, workflow)
        page.wait_for_timeout(300)
        scan(page, "admin-" + workflow)
    scan(sessions("super").login("superadmin"), "users")
    display = sessions("viewer").login("client", portal="client")
    expect(display.locator("#displaySync")).to_contain_text("Live", timeout=15000)
    scan(display, "client")

    assert set(found) == set(PAGES)
    violations = {label: sorted(rules) for label, rules in found.items() if rules}
    assert not violations, f"axe violations: {violations}"
