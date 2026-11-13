"""Shared page helpers for the end-to-end tests (SG-TODO-021)."""
from playwright.sync_api import expect


def admin(sessions, workflow="campaign"):
    """Log in as the DM account and open one admin workflow tab."""
    session = sessions("dm")
    page = session.login("admin")
    page.wait_for_function("document.body.dataset.workflowNavigation === 'ready'")
    open_workflow(page, workflow)
    return session, page


def open_workflow(page, workflow):
    page.click(f"#adminWorkflow-{workflow}")
    if workflow == "campaign" and page.locator("#campaignInputPane").is_hidden():
        page.click("#toggleCampaignPane")


def show_character_input(page):
    open_workflow(page, "campaign")
    if page.locator("#characterInputPane").is_hidden():
        page.click("#toggleCharacterPane")


def add_character(page, name, hp=20, initiative=""):
    show_character_input(page)
    page.fill("#characterName", name)
    page.fill("#characterHp", str(hp))
    page.fill("#characterInitiative", str(initiative))
    page.click("#characterForm button")
    expect(page.locator("#characterAddNotification")).to_contain_text(f"Character “{name}” added")
    expect(row(page, "characters", name)).to_have_count(1)


def add_monster(page, name, species="humanoid", ac=12, hp="7", bonus="", quantity=1):
    open_workflow(page, "preparation")
    page.fill("#monsterName", name)
    page.fill("#monsterSpecies", species)
    page.fill("#monsterAc", str(ac))
    page.fill("#monsterHpRangeStart", str(hp))
    page.fill("#monsterInitiativeBonus", str(bonus))
    page.fill("#monsterQuantity", str(quantity))
    page.click("#monsterForm button")
    text = f"Monster {name} added" if quantity == 1 else f"{quantity} monsters added"
    expect(page.locator("#monsterAddNotification")).to_contain_text(text)


def row(page, kind, name):
    """The roster row whose name cell is exactly ``name``."""
    return page.locator(f"#{kind} tr").filter(has=page.get_by_label(f"Select {name}", exact=True))


def roster_names(page, kind):
    cells = page.locator(f"#{kind} tr td:nth-child(2)")
    return [text.split("\n")[0].strip() for text in cells.all_inner_texts()]


def initiative_input(page, kind, name):
    label = f"{name} initiative" + (" raw roll" if kind == "monsters" else "")
    return page.get_by_label(label, exact=True)


def set_initiative(page, kind, name, value):
    field = initiative_input(page, kind, name)
    field.fill(str(value))
    field.press("Enter")
    if kind == "monsters":
        expect(row(page, kind, name).locator("output")).not_to_have_text("Total: unset")
    expect(field).to_have_value(str(value))


def roster_state(page, kind, name):
    return row(page, kind, name).locator(".sg-roster-state")
