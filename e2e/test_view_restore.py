"""Admin view kept across a page reload: workflow tab, open panels and closed dialogs."""
from playwright.sync_api import expect

from helpers import add_character, admin, prepare_battle, start_battle, wait_ready


def test_reload_keeps_workflow_tab_and_panels(sessions):
    """A reload keeps the selected workflow tab and which panels are open or closed."""
    _, page = admin(sessions, "preparation")
    add_character(page, "Borin")  # Opens the character input in the Campaign tab.
    page.click("#adminWorkflow-preparation")
    for toggle, state in (("#toggleBattleSetupPane", "true"), ("#toggleMonsterPane", "true"),
                          ("#toggleCharacterDisplayPane", "false")):
        button = page.locator(toggle)
        if button.get_attribute("aria-expanded") != state:
            button.click()
        expect(button).to_have_attribute("aria-expanded", state)
    page.reload()
    wait_ready(page)
    expect(page.locator("#adminWorkflow-preparation")).to_have_attribute("aria-selected", "true")
    expect(page.locator("#toggleBattleSetupPane")).to_have_attribute("aria-expanded", "true")
    expect(page.locator("#toggleMonsterPane")).to_have_attribute("aria-expanded", "true")
    expect(page.locator("#toggleCharacterDisplayPane")).to_have_attribute("aria-expanded", "false")
    expect(page.locator("#battleSetupInputPane")).to_be_visible()
    expect(page.locator("#monsterInputPane")).to_be_visible()
    expect(page.locator("#characterDisplayPane")).to_be_hidden()


def test_reload_during_battle_keeps_reopened_panels_and_closes_dialogs(sessions):
    """During a battle a reload keeps the Live tab and reopened panels, and closes open dialogs."""
    _, page = admin(sessions)
    prepare_battle(page)
    start_battle(page)
    page.click("#toggleCharacterDisplayPane")
    expect(page.locator("#characterDisplayPane")).to_be_visible()
    page.click("#toggleEncounterTools")
    expect(page.locator("#encounterFeatures")).to_be_visible()
    page.reload()
    wait_ready(page)
    expect(page.locator("#adminWorkflow-live")).to_have_attribute("aria-selected", "true")
    expect(page.locator("#toggleCharacterDisplayPane")).to_have_attribute("aria-expanded", "true")
    expect(page.locator("#characterDisplayPane")).to_be_visible()
    expect(page.locator("#toggleMonsterDisplayPane")).to_have_attribute("aria-expanded", "false")
    expect(page.locator("#encounterFeatures")).to_be_hidden()
    expect(page.locator("#battleState")).to_have_text("Active")


def test_new_navigation_starts_with_default_view(sessions, server):
    """Opening the Admin page again (not a reload) starts with the default view."""
    _, page = admin(sessions, "live")
    page.click("#toggleMonsterDisplayPane")
    expect(page.locator("#toggleMonsterDisplayPane")).to_have_attribute("aria-expanded", "false")
    page.goto(server.admin + "/")
    wait_ready(page)
    expect(page.locator("#adminWorkflow-campaign")).to_have_attribute("aria-selected", "true")
    page.click("#adminWorkflow-live")
    expect(page.locator("#toggleMonsterDisplayPane")).to_have_attribute("aria-expanded", "true")
