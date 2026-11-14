"""Feedback policy 097, connection loss and recovery, and setup switching under failures (SG-TODO-021 Stage 4).

Transient outages are simulated by failing the browser's API requests; one test restarts the real server.
"""
import time

from playwright.sync_api import expect

from conftest import ACCOUNTS
from helpers import (add_character, admin, grant_viewer, initiative_input, join, open_workflow,
                     prepare_battle, start_battle, wait_ready)

POLL = 15000  # Background refresh runs every 3 s; allow several cycles.


def lifetime(locator, limit=10):
    """Seconds from now until ``locator`` is hidden."""
    started = time.monotonic()
    expect(locator).to_be_hidden(timeout=limit * 1000)
    return time.monotonic() - started


def test_pane_success_clears_after_three_seconds(sessions):
    """A pane success message clears after about 3 seconds."""
    _, page = admin(sessions)
    add_character(page, "Aelwyn")
    note = page.locator("#characterAddNotification .sg-feedback-text")
    expect(note).to_have_text("Success: Character “Aelwyn” added to the active campaign.")
    assert 1.5 < lifetime(note) < 4.5


def test_global_success_clears_after_five_seconds(sessions):
    """A global success message clears after about 5 seconds."""
    _, page = admin(sessions)
    prepare_battle(page)
    start_battle(page)
    page.click("#endBattle")
    note = page.locator("#message .sg-feedback-text", has_text="Battle ended")
    expect(note).to_be_visible()
    assert 3.5 < lifetime(note) < 6.5


def test_errors_stay_until_dismissed(sessions):
    """Errors stay past the success timeouts until dismissed."""
    _, page = admin(sessions, "live")
    page.click("#startBattle")
    error = page.locator("#message .sg-feedback-text", has_text="Activate at least one turn-eligible participant")
    expect(error).to_be_visible()
    page.wait_for_timeout(6500)
    expect(error).to_be_visible()
    page.locator("#message").get_by_role("button", name="Dismiss").first.click()
    expect(error).to_have_count(0)


def test_field_error_link_clears_on_dismiss(sessions):
    """A field-linked error marks its field invalid until the error is dismissed."""
    _, page = admin(sessions)
    add_character(page, "Borin")
    join(page, "characters", "Borin")
    field = initiative_input(page, "characters", "Borin")
    expect(field).to_have_attribute("aria-invalid", "true")
    described = field.get_attribute("aria-describedby")
    expect(page.locator(f"#{described}")).to_have_text("Enter initiative before joining battle: Borin")
    page.locator("#message").get_by_role("button", name="Dismiss").first.click()
    expect(field).not_to_have_attribute("aria-invalid", "true")
    expect(page.locator(f"#{described}")).to_have_count(0)


def outage(page):
    """Make every API request from ``page`` fail as if the server were unreachable."""
    page.context.route("**/api/**", lambda route: route.abort("connectionrefused"))


def restore(page):
    page.context.unroute("**/api/**")


def test_connection_warning_and_recovery(sessions):
    """A lost connection shows a lasting warning; reconnecting shows recovery."""
    _, page = admin(sessions)
    add_character(page, "Aelwyn")
    outage(page)
    warning = page.locator("#message .sg-feedback-text",
                           has_text="Warning: Connection to the server was lost. Retrying automatically.")
    expect(warning).to_be_visible(timeout=POLL)
    page.wait_for_timeout(6000)
    expect(warning).to_be_visible()
    restore(page)
    expect(page.locator("#message")).to_contain_text("Success: Connection to the server restored.", timeout=POLL)
    expect(warning).to_have_count(0)
    expect(page.locator("#characters")).to_contain_text("Aelwyn")


def test_display_keeps_last_state_while_server_is_down(sessions, server):
    """During an outage the Client Display keeps its last state; after a restart it asks for sign-in and is live again."""
    _, dm = admin(sessions)
    grant_viewer(dm, ACCOUNTS["client"][0])
    prepare_battle(dm)
    start_battle(dm)
    viewer = sessions("viewer")
    display = viewer.login("client", portal="client")
    sync = display.locator("#displaySync")
    expect(sync).to_contain_text("Live", timeout=POLL)
    expect(display.locator("#stage article.monster")).to_have_count(1, timeout=POLL)
    server.stop()
    expect(sync).to_have_text("Reconnecting… (last display retained)", timeout=POLL)
    expect(display.locator("#stage article.monster")).to_have_count(1)
    expect(display.locator("#initiative .round-indicator")).to_have_text("Round 1")
    server.start()
    # Sessions live in server memory, so the display goes to the sign-in page by itself.
    expect(display).to_have_url(server.client + "/login", timeout=60000)
    display = viewer.login("client", portal="client")
    expect(display.locator("#displaySync")).to_contain_text("Live", timeout=POLL)
    expect(display.locator("#initiative .round-indicator")).to_have_text("Round 1")
    expect(display.locator("#stage article.monster")).to_have_count(1)


def test_setup_switch_fails_safely_and_retries(sessions):
    """Loading a setup during an outage keeps the active setup; retrying afterwards works."""
    _, page = admin(sessions, "preparation")
    page.fill("#setupName", "ambush")
    page.click("#saveSetup")
    context = page.locator("#adminContextSetup")
    expect(context).to_have_text("ambush")
    outage(page)
    page.select_option("#setupSelect", "default")  # Choosing a setup loads it immediately.
    expect(page.locator(".sg-feedback-text", has_text="Error:").first).to_be_visible(timeout=POLL)
    expect(context).to_have_text("ambush")
    expect(page.locator("#setupSelect")).to_have_value("ambush")
    restore(page)
    page.select_option("#setupSelect", "default")
    expect(context).to_have_text("default")
    page.reload()
    wait_ready(page)
    open_workflow(page, "preparation")
    expect(context).to_have_text("default")


def test_server_restart_keeps_data_and_requires_sign_in(sessions, server):
    """A server restart keeps campaign data and sends the signed-out Admin to the sign-in page."""
    session, page = admin(sessions)
    add_character(page, "Aelwyn")
    server.stop()
    expect(page.locator("#message")).to_contain_text("Connection to the server was lost", timeout=POLL)
    server.start()
    expect(page).to_have_url(server.admin + "/login", timeout=POLL)
    page = session.login("admin")
    expect(page.locator("#characters")).to_contain_text("Aelwyn")
