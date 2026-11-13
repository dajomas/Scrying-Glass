"""Client Display content and live updates against a real server (SG-TODO-021 Stage 3)."""
from playwright.sync_api import expect

from conftest import ACCOUNTS
from helpers import admin, grant_viewer, open_workflow, prepare_battle, row, show_rosters, start_battle

LIVE = 15000  # The display updates over a WebSocket; allow for reconnects and polling.


def viewer(sessions):
    page = sessions("viewer").login("client", portal="client")
    expect(page.locator("#displaySync")).to_contain_text("Live", timeout=LIVE)
    return page


def test_display_without_campaign_access(sessions):
    """A viewer without campaign access sees the no-access message and an empty display."""
    page = viewer(sessions)
    expect(page.locator("#clientCampaign")).to_have_text("No campaign access has been granted. Ask an administrator.")
    expect(page.locator("#initiative")).to_have_text("")
    expect(page.locator("#stage article")).to_have_count(0)


def test_display_shows_campaign_and_active_monsters(sessions):
    """The display names the campaign and shows a card for each monster in battle."""
    _, dm = admin(sessions)
    grant_viewer(dm, ACCOUNTS["client"][0])
    prepare_battle(dm, monsters=(("Orc", 10, 15), ("Wolf", 8, 11)))
    display = viewer(sessions)
    expect(display.locator("#clientCampaign")).to_have_text("Campaign: Default")
    cards = display.locator("#stage article.monster")
    expect(cards).to_have_count(2, timeout=LIVE)
    expect(cards.locator("h1")).to_have_text(["Orc", "Wolf"])
    expect(cards.first.locator(".type")).to_have_text("humanoid")
    expect(cards.first.locator(".stats")).to_have_text("")


def test_display_battle_order_follows_visibility(sessions):
    """Only visible combatants appear in the display's battle order, with the round shown."""
    _, dm = admin(sessions)
    grant_viewer(dm, ACCOUNTS["client"][0])
    prepare_battle(dm)
    display = viewer(sessions)
    start_battle(dm)
    order = display.locator("#initiative")
    expect(order.locator(".round-indicator")).to_have_text("Round 1", timeout=LIVE)
    expect(order.locator(".token")).to_have_text(["Borin"])
    expect(order.locator(".token.turn")).to_have_text("Borin")

    open_workflow(dm, "preparation")
    show_rosters(dm)
    row(dm, "monsters", "Orc").locator("button[data-mv]").click()
    expect(row(dm, "monsters", "Orc").locator("button[data-mv]")).to_have_attribute("aria-pressed", "true")
    expect(order.locator(".token")).to_have_text(["Borin", "Orc"], timeout=LIVE)


def test_display_live_updates_from_admin_actions(sessions):
    """HP display, turn changes and ending the battle reach the display without a reload."""
    _, dm = admin(sessions)
    grant_viewer(dm, ACCOUNTS["client"][0])
    prepare_battle(dm)
    display = viewer(sessions)
    start_battle(dm)
    card = display.locator("#stage article.monster", has_text="Orc")
    expect(card).to_be_visible(timeout=LIVE)

    open_workflow(dm, "preparation")
    show_rosters(dm)
    row(dm, "monsters", "Orc").locator("button[data-mv]").click()
    row(dm, "monsters", "Orc").locator("button[data-f=show_hp]").click()
    expect(card.locator(".stats")).to_have_text("HP 15/15", timeout=LIVE)

    open_workflow(dm, "live")
    dm.click("#nextBattle")
    expect(display.locator("#initiative .token.turn")).to_have_text("Orc", timeout=LIVE)
    expect(card.locator("h1")).to_have_text("Orc ◀", timeout=LIVE)

    dm.click("#endBattle")
    expect(dm.locator("#battleState")).to_have_text("Inactive")
    expect(display.locator("#initiative .round-indicator")).to_have_count(0, timeout=LIVE)


def test_display_connection_reported_to_admin(sessions):
    """The admin's Encounter tools report the connected display."""
    _, dm = admin(sessions)
    grant_viewer(dm, ACCOUNTS["client"][0])
    viewer(sessions)
    open_workflow(dm, "live")
    dm.click("#toggleEncounterTools")
    expect(dm.locator("#displayConnections")).to_have_text(
        f"1 display(s) connected: {ACCOUNTS['client'][0]} (live)", timeout=LIVE)
