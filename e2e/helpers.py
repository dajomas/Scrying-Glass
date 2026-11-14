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
    # The save re-renders the row; wait until its Join button is no longer gated.
    expect(join_button(page, kind, name)).not_to_have_attribute("data-initiative-blocked", "true")


def join_button(page, kind, name):
    return row(page, kind, name).locator("button[data-ca]" if kind == "characters" else "button[data-ma]")


def join(page, kind, name):
    """Click Join Battle; force is needed because a gated button is aria-disabled."""
    button = join_button(page, kind, name)
    expect(button).to_be_visible()
    button.click(force=True)


def roster_state(page, kind, name):
    return row(page, kind, name).locator(".sg-roster-state")


def show_rosters(page):
    """Open both roster display panes; a running battle collapses them in the live workflow."""
    for pane, toggle in (("#characterDisplayPane", "#toggleCharacterDisplayPane"),
                         ("#monsterDisplayPane", "#toggleMonsterDisplayPane")):
        if page.locator(pane).is_hidden():
            page.click(toggle)
        expect(page.locator(pane)).to_be_visible()


def grant_viewer(page, username):
    """Give a client account viewer access to the active campaign."""
    open_workflow(page, "campaign")
    page.locator("#campaignViewerAccessTitle").click()
    page.locator("#campaignViewerUsers label", has_text=username).locator("input").check()
    page.click("#saveCampaignViewers")
    expect(page.locator("#campaignViewerFeedback")).to_be_visible()


def prepare_battle(page, characters=(("Borin", 20),), monsters=(("Orc", 10, 15),)):
    """Add joined characters (name, initiative) and monsters (name, raw roll, HP; bonus 0)."""
    for name, initiative in characters:
        add_character(page, name, initiative=initiative)
        join(page, "characters", name)
        expect(roster_state(page, "characters", name)).to_contain_text("In battle")
    for name, roll, hp in monsters:
        add_monster(page, name, ac=13, hp=hp, bonus=0)
        set_initiative(page, "monsters", name, roll)
        join(page, "monsters", name)
        expect(roster_state(page, "monsters", name)).to_contain_text("In battle")


def start_battle(page):
    open_workflow(page, "live")
    page.click("#startBattle")
    expect(page.locator("#battleState")).to_have_text("Active")


def hp_cell(page, kind, name):
    if kind == "characters":
        return row(page, kind, name).locator(".sg-character-hp")
    return row(page, kind, name).locator("td").nth(3)


def option_value(select, text):
    """Value of the first option in ``select`` whose label contains ``text``."""
    for option in select.locator("option").all():
        if text in option.inner_text():
            return option.get_attribute("value")
    raise AssertionError(f"No option containing {text!r}")


def wait_ready(page):
    page.wait_for_function("document.body.dataset.workflowNavigation === 'ready'")
