"""Initiative entry, the join gate and battle order against a real server (SG-TODO-021 Stage 2)."""
import re

from playwright.sync_api import expect

from helpers import (add_character, add_monster, admin, initiative_input, open_workflow, roster_state,
                     row, set_initiative)


def join(page, kind, name):
    attribute = "data-ca" if kind == "characters" else "data-ma"
    row(page, kind, name).locator(f"button[{attribute}]").click(force=True)


def raw_and_total(page, name):
    raw = initiative_input(page, "monsters", name).input_value()
    total = row(page, "monsters", name).locator("output").inner_text()
    return int(raw), int(re.fullmatch(r"Total: (-?\d+)", total.strip()).group(1))


def test_join_gate_requires_initiative(sessions):
    """Join Battle is refused until initiative is set, with the error linked to the field."""
    _, page = admin(sessions)
    add_character(page, "Borin")
    field = initiative_input(page, "characters", "Borin")
    expect(row(page, "characters", "Borin").locator("button[data-ca]")).to_have_attribute("aria-disabled", "true")
    join(page, "characters", "Borin")
    message = "Enter initiative before joining battle: Borin"
    expect(page.get_by_text(f"Error: {message}")).to_be_visible()
    expect(field).to_have_attribute("aria-invalid", "true")
    described = field.get_attribute("aria-describedby")
    expect(page.locator(f"#{described}")).to_have_text(message)
    expect(roster_state(page, "characters", "Borin")).to_contain_text("Not in battle")

    set_initiative(page, "characters", "Borin", 14)
    join(page, "characters", "Borin")
    expect(roster_state(page, "characters", "Borin")).to_contain_text("In battle")
    expect(row(page, "characters", "Borin").locator("button[data-ca]")).to_have_attribute("aria-pressed", "true")


def test_monster_join_gate_requires_raw_roll(sessions):
    """A monster without a raw roll cannot join; with a roll it can."""
    _, page = admin(sessions, "preparation")
    add_monster(page, "Goblin", bonus=2)
    join(page, "monsters", "Goblin")
    expect(page.get_by_text("Error: Enter initiative before joining battle: Goblin")).to_be_visible()
    expect(roster_state(page, "monsters", "Goblin")).to_contain_text("Not in battle")
    set_initiative(page, "monsters", "Goblin", 9)
    join(page, "monsters", "Goblin")
    expect(roster_state(page, "monsters", "Goblin")).to_contain_text("In battle")


def test_monster_raw_roll_bonus_and_total(sessions):
    """A monster's total is the raw roll plus its bonus, also after editing the bonus."""
    _, page = admin(sessions, "preparation")
    add_monster(page, "Goblin", bonus=2, quantity=2)
    total = row(page, "monsters", "Goblin - 1").locator("output")
    expect(total).to_have_text("Total: unset")
    set_initiative(page, "monsters", "Goblin - 1", 11)
    expect(total).to_have_text("Total: 13")
    expect(row(page, "monsters", "Goblin - 2").locator("output")).to_have_text("Total: unset")

    row(page, "monsters", "Goblin - 1").locator("button[data-edit]").click()
    form = page.locator("#editForm")
    expect(form.locator("[name=initiative_bonus]")).to_have_value("2")
    form.locator("[name=initiative_bonus]").fill("-1")
    form.get_by_role("button", name="Save monster").click()
    expect(page.locator("#editModal")).to_be_hidden()
    expect(row(page, "monsters", "Goblin - 1").locator(".sg-monster-initiative-bonus")).to_have_text("-1")
    expect(total).to_have_text("Total: 10")
    expect(initiative_input(page, "monsters", "Goblin - 1")).to_have_value("11")

    page.reload()
    page.wait_for_function("document.body.dataset.workflowNavigation === 'ready'")
    expect(row(page, "monsters", "Goblin - 1").locator("output")).to_have_text("Total: 10")


def test_roll_monster_initiatives(sessions):
    """Roll monster initiatives asks first, then rolls a d20 for every monster."""
    session, page = admin(sessions, "preparation")
    add_monster(page, "Wolf", bonus=3, quantity=3)
    page.click("#rollMonsterInitiative")
    assert session.dialogs[-1] == ("confirm", "Overwrite initiative for all 3 monster(s) with a random d20 roll?")
    for name in ("Wolf - 1", "Wolf - 2", "Wolf - 3"):
        expect(row(page, "monsters", name).locator("output")).not_to_have_text("Total: unset")
        raw, total = raw_and_total(page, name)
        assert 1 <= raw <= 20 and total == raw + 3


def test_roll_shared_initiative(sessions):
    """Roll shared initiative gives the selected monsters one common roll."""
    _, page = admin(sessions, "preparation")
    add_monster(page, "Wolf", bonus=1, quantity=3)
    add_monster(page, "Bear", bonus=0)
    for name in ("Wolf - 1", "Wolf - 2", "Wolf - 3"):
        row(page, "monsters", name).locator("input.bulk-selection-checkbox").check()
    page.select_option("#monsterBulkAction", "roll-shared-initiative")
    for name in ("Wolf - 1", "Wolf - 2", "Wolf - 3"):
        expect(row(page, "monsters", name).locator("output")).not_to_have_text("Total: unset")
    rolls = {raw_and_total(page, name) for name in ("Wolf - 1", "Wolf - 2", "Wolf - 3")}
    assert len(rolls) == 1
    raw, total = rolls.pop()
    assert 1 <= raw <= 20 and total == raw + 1
    expect(row(page, "monsters", "Bear").locator("output")).to_have_text("Total: unset")


def test_manual_character_initiative_edits(sessions):
    """Inline and dialog initiative edits for a character are saved."""
    _, page = admin(sessions)
    add_character(page, "Cara", initiative=10)
    set_initiative(page, "characters", "Cara", 17)
    page.reload()
    page.wait_for_function("document.body.dataset.workflowNavigation === 'ready'")
    expect(initiative_input(page, "characters", "Cara")).to_have_value("17")
    row(page, "characters", "Cara").locator("button[data-edit]").click()
    form = page.locator("#editForm")
    expect(form.locator("[name=initiative]")).to_have_value("17")
    form.locator("[name=initiative]").fill("4")
    form.get_by_role("button", name="Save character").click()
    expect(page.locator("#editModal")).to_be_hidden()
    expect(initiative_input(page, "characters", "Cara")).to_have_value("4")


def test_battle_order_follows_initiative_and_tie_choice(sessions):
    """Battle order sorts by initiative, and the tie dialog decides equal totals."""
    _, page = admin(sessions)
    for name, initiative in (("Aelwyn", 12), ("Borin", 20), ("Cara", 13)):
        add_character(page, name, initiative=initiative)
    page.click("#selectAllCharacters")
    page.select_option("#characterBulkAction", "join-battle")
    for name in ("Aelwyn", "Borin", "Cara"):
        expect(roster_state(page, "characters", name)).to_contain_text("In battle")
    add_monster(page, "Orc", bonus=1)
    set_initiative(page, "monsters", "Orc", 11)
    join(page, "monsters", "Orc")
    expect(roster_state(page, "monsters", "Orc")).to_contain_text("In battle")

    open_workflow(page, "live")
    page.click("#startBattle")
    tie = page.locator("#tieModal")
    expect(tie).to_be_visible()
    expect(page.locator("#tieGroups .tie-title")).to_have_text("Initiative 12")
    expect(page.locator("#tieGroups label.tie")).to_have_count(2)
    page.locator("#tieGroups label.tie", has_text="Orc").locator("select").select_option("1")
    page.locator("#tieGroups label.tie", has_text="Aelwyn").locator("select").select_option("2")
    page.click("#confirmOrder")
    expect(tie).to_be_hidden()
    expect(page.locator("#battleState")).to_have_text("Active")
    expect(page.locator("#battleInfo")).to_have_text("Order: Borin ⇒ Cara ⇒ Orc ⇒ Aelwyn")


def test_tie_dialog_cancel_keeps_battle_inactive(sessions):
    """Cancelling the tie dialog does not start the battle."""
    _, page = admin(sessions)
    for name in ("Aelwyn", "Borin"):
        add_character(page, name, initiative=12)
    page.click("#selectAllCharacters")
    page.select_option("#characterBulkAction", "join-battle")
    expect(roster_state(page, "characters", "Borin")).to_contain_text("In battle")
    open_workflow(page, "live")
    page.click("#startBattle")
    expect(page.locator("#tieModal")).to_be_visible()
    page.click("#cancelOrder")
    expect(page.locator("#tieModal")).to_be_hidden()
    expect(page.locator("#battleState")).to_have_text("Inactive")


def test_keyboard_navigation_between_initiative_fields(sessions):
    """Tab and Shift+Tab move between initiative fields, save typed values, and Escape leaves the roster."""
    _, page = admin(sessions, "preparation")
    add_monster(page, "Goblin", bonus=0, quantity=3)
    first = initiative_input(page, "monsters", "Goblin - 1")
    second = initiative_input(page, "monsters", "Goblin - 2")
    third = initiative_input(page, "monsters", "Goblin - 3")
    first.focus()
    page.keyboard.type("7")
    page.keyboard.press("Tab")
    expect(second).to_be_focused()
    expect(row(page, "monsters", "Goblin - 1").locator("output")).to_have_text("Total: 7")
    page.keyboard.type("5")
    page.keyboard.press("Tab")
    expect(third).to_be_focused()
    expect(row(page, "monsters", "Goblin - 2").locator("output")).to_have_text("Total: 5")
    page.keyboard.press("Tab")
    expect(first).to_be_focused()
    page.keyboard.press("Shift+Tab")
    expect(third).to_be_focused()
    page.keyboard.press("Escape")
    expect(page.locator("#monsters")).to_be_focused()
