"""Responsive widths, dialog focus handling and automated accessibility scans (SG-TODO-021 Stage 4).

The axe scans compare against a documented baseline of known findings (docs/handover/610); a rule
that is not in the baseline fails the test. The baseline is a record for follow-up work, not an
acceptance of the findings.
"""
import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import expect

from conftest import ACCOUNTS
from helpers import add_character, add_monster, admin, grant_viewer, open_workflow, row

WIDTHS = (360, 768, 1024, 1440)
WORKFLOWS = ("campaign", "preparation", "live")
OVERFLOW = "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"

# Known axe findings per page (rule ids), recorded in docs/handover/610 for a follow-up.
AXE_BASELINE = {
    "login": {"html-has-lang", "landmark-one-main", "region"},
    "admin-campaign": set(),
    "admin-preparation": {"aria-allowed-role"},
    "admin-live": set(),
    "users": set(),
    "client": {"html-has-lang", "landmark-one-main", "page-has-heading-one"},
}


def no_horizontal_scroll(page, label):
    overflow = page.evaluate(OVERFLOW)
    assert overflow <= 0, f"{label}: page scrolls horizontally by {overflow}px"


@pytest.mark.parametrize("width", WIDTHS)
def test_pages_fit_viewport_width(sessions, server, width):
    """Admin, Client Display, login and Users pages fit the viewport width without horizontal scrolling."""
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


@pytest.mark.xfail(strict=True, reason="Known finding: focus falls to the page body when the campaign dialog closes")
def test_campaign_dialog_returns_focus_to_opener(sessions):
    """Closing the New campaign dialog returns focus to the New campaign button."""
    _, page = admin(sessions)
    opener = page.locator("#newCampaign")
    opener.click()
    expect(page.locator("#campaignModal")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator("#campaignModal")).to_be_hidden()
    expect(opener).to_be_focused(timeout=2000)


def test_axe_scan_finds_no_new_violations(sessions, server):
    """Automated axe scans of login, Admin, Users and Client Display find no violations beyond the baseline."""
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

    new = {label: sorted(rules - AXE_BASELINE[label]) for label, rules in found.items() if rules - AXE_BASELINE[label]}
    assert not new, f"New axe violations beyond the documented baseline: {new}"
