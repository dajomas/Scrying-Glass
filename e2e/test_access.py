"""Login, roles, user management, campaign ownership and viewer access."""
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from playwright.sync_api import expect

from conftest import ACCOUNTS


def status(url):
    try:
        with urlopen(Request(url), timeout=10) as response:
            return response.status
    except HTTPError as error:
        return error.code


def test_admin_login_logout_and_redirects(sessions, server, browser_name):
    """Admin login (wrong and correct password), logout and login redirects."""
    page = sessions().page()
    page.goto(server.admin + "/")
    expect(page).to_have_url(server.admin + "/login")
    page.fill("[name=username]", ACCOUNTS["admin"][0])
    page.fill("[name=password]", "wrong-password")
    page.click("form button")
    expect(page.locator(".error")).to_have_text("Invalid admin credentials")
    page.fill("[name=username]", ACCOUNTS["admin"][0])
    page.fill("[name=password]", ACCOUNTS["admin"][1])
    page.click("form button")
    expect(page).to_have_url(server.admin + "/")
    expect(page).to_have_title("Scrying Glass Admin")
    expect(page.locator("#adminWorkflow-campaign")).to_have_attribute("aria-selected", "true")
    page.goto(server.admin + "/login")
    expect(page).to_have_url(server.admin + "/")
    page.click("#adminMore > summary")
    page.click("#adminLogout")
    expect(page).to_have_url(server.admin + "/login")
    page.goto(server.admin + "/")
    expect(page).to_have_url(server.admin + "/login")


def test_role_routing(sessions, server):
    """Role routing: superadmin to Users, admin denied Users, client denied Admin."""
    superadmin = sessions("super").login("superadmin")
    expect(superadmin).to_have_url(server.admin + "/users")
    superadmin.goto(server.admin + "/")
    expect(superadmin).to_have_url(server.admin + "/users")
    admin = sessions("dm").login("admin")
    response = admin.goto(server.admin + "/users")
    assert response.status == 403
    client = sessions("viewer").login("client")
    expect(client.locator(".error")).to_have_text("Invalid admin credentials")


def test_unauthenticated_requests_are_rejected(server):
    """Unauthenticated API requests are rejected on both portals."""
    assert status(server.admin + "/api/state") == 401
    assert status(server.admin + "/api/users") == 401
    assert status(server.client + "/api/state") == 401


def test_superadmin_creates_user_who_can_sign_in(sessions, server):
    """Superadmin creates a client user who can sign in to the display."""
    page = sessions("super").login("superadmin")
    rows = page.locator("#userRows tr")
    expect(rows).to_have_count(3)
    page.fill("#username", "e2e-new-viewer")
    page.select_option("#role", "client")
    page.fill("#password", "new-viewer-pass")
    page.click("#userForm button[type=submit]")
    expect(rows).to_have_count(4)
    expect(page.locator("#userRows")).to_contain_text("e2e-new-viewer")
    viewer = sessions("new-viewer").page()
    viewer.goto(server.client + "/login")
    viewer.fill("[name=username]", "e2e-new-viewer")
    viewer.fill("[name=password]", "new-viewer-pass")
    viewer.click("form button")
    expect(viewer).to_have_url(server.client + "/display")


def test_campaign_ownership_controls_admin_visibility(sessions, server):
    """Campaign ownership: unassign hides, reassign restores the campaign."""
    dm = sessions("dm").login("admin")
    dm.click("#toggleCampaignPane")
    options = dm.locator("#campaignSelect option")
    expect(options).to_have_count(1)
    owned = options.first.inner_text()
    superadmin = sessions("super").login("superadmin")
    row = superadmin.locator("#campaignOwnerRows tr").first
    expect(row).to_be_visible()
    row.locator("select").select_option("")
    row.get_by_role("button", name="Save owner").click()
    expect(superadmin.locator("#campaignOwnerNotice")).to_have_text("Campaign owner saved.")
    dm.reload()
    dm.wait_for_load_state("networkidle")
    expect(dm.locator("#campaignSelect option:not([value=''])")).to_have_count(0)
    row = superadmin.locator("#campaignOwnerRows tr").first
    row.locator("select").select_option(label=ACCOUNTS["admin"][0])
    row.get_by_role("button", name="Save owner").click()
    expect(superadmin.locator("#campaignOwnerNotice")).to_have_text("Campaign owner saved.")
    dm.reload()
    dm.wait_for_load_state("networkidle")
    expect(dm.locator("#campaignSelect option")).to_have_text([owned])


def test_viewer_access_grant_and_revoke(sessions, server):
    """Viewer access grant and revoke update the Client display."""
    viewer = sessions("viewer").login("client", portal="client")
    expect(viewer).to_have_url(server.client + "/display")
    campaign = viewer.locator("#clientCampaign")
    expect(campaign).not_to_contain_text("Default")
    dm = sessions("dm").login("admin")
    dm.click("#toggleCampaignPane")
    dm.locator("#campaignViewerAccessTitle").click()
    grant = dm.locator("#campaignViewerUsers label", has_text=ACCOUNTS["client"][0]).locator("input")
    grant.check()
    dm.click("#saveCampaignViewers")
    expect(dm.locator("#campaignViewerFeedback")).to_be_visible()
    viewer.reload()
    expect(campaign).to_contain_text("Default")
    grant.uncheck()
    dm.click("#saveCampaignViewers")
    expect(grant).not_to_be_checked()
    viewer.reload()
    expect(campaign).not_to_contain_text("Default", timeout=10000)
