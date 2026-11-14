"""Character and monster rosters against a real server (SG-TODO-021 Stage 2)."""
import re

from playwright.sync_api import expect

from helpers import (add_character, add_monster, admin, roster_names, roster_state, row,
                     show_character_input)


def test_add_edit_and_remove_character(sessions):
    """Add, edit and remove a character; changes survive reload."""
    session, page = admin(sessions)
    add_character(page, "Aelwyn", hp=24, initiative=15)
    aelwyn = row(page, "characters", "Aelwyn")
    expect(aelwyn.locator(".sg-character-hp")).to_have_text("24/24")
    expect(roster_state(page, "characters", "Aelwyn")).to_contain_text("Not in battle")

    aelwyn.locator("button[data-edit]").click()
    expect(page.locator("#editModal")).to_be_visible()
    expect(page.locator("#editTitle")).to_have_text("Edit character: Aelwyn")
    form = page.locator("#editForm")
    expect(form.locator("[name=initiative]")).to_have_value("15")
    form.locator("[name=name]").fill("Aelwyn the Bold")
    form.locator("[name=hp]").fill("18")
    form.locator("[name=max_hp]").fill("30")
    form.get_by_role("button", name="Save character").click()
    expect(page.locator("#editModal")).to_be_hidden()
    expect(row(page, "characters", "Aelwyn the Bold").locator(".sg-character-hp")).to_have_text("18/30")

    page.reload()
    page.wait_for_function("document.body.dataset.workflowNavigation === 'ready'")
    expect(row(page, "characters", "Aelwyn the Bold").locator(".sg-character-hp")).to_have_text("18/30")

    row(page, "characters", "Aelwyn the Bold").locator("button[data-remove-kind]").click()
    expect(page.locator("#characters input.bulk-selection-checkbox")).to_have_count(0)
    assert session.dialogs[-1] == ("confirm", "Remove character “Aelwyn the Bold” from the active campaign?")


def test_character_form_requires_name_and_hp(sessions):
    """The character form requires a name and a starting HP."""
    _, page = admin(sessions)
    show_character_input(page)
    page.fill("#characterHp", "")
    page.click("#characterForm button")
    assert page.locator("#characterName").evaluate("input => !input.validity.valid")
    assert page.locator("#characterHp").evaluate("input => !input.validity.valid")
    expect(page.locator("#characters input.bulk-selection-checkbox")).to_have_count(0)


def test_add_edit_and_remove_monsters(sessions):
    """Add numbered monsters, edit one and remove another."""
    session, page = admin(sessions, "preparation")
    add_monster(page, "Goblin", species="goblin", ac=15, hp=7, bonus=2, quantity=3)
    assert roster_names(page, "monsters") == ["Goblin - 1", "Goblin - 2", "Goblin - 3"]
    goblin = row(page, "monsters", "Goblin - 1")
    expect(goblin.locator("td").nth(2)).to_have_text("15")
    expect(goblin.locator("td").nth(3)).to_have_text("7/7")
    expect(goblin.locator(".sg-monster-initiative-bonus")).to_have_text("+2")
    expect(goblin.locator("small")).to_have_text("goblin")

    goblin.locator("button[data-edit]").click()
    expect(page.locator("#editTitle")).to_have_text("Edit monster: Goblin - 1")
    form = page.locator("#editForm")
    form.locator("[name=name]").fill("Goblin Boss")
    form.locator("[name=ac]").fill("17")
    form.get_by_role("button", name="Save monster").click()
    expect(page.locator("#editModal")).to_be_hidden()
    expect(row(page, "monsters", "Goblin Boss").locator("td").nth(2)).to_have_text("17")

    row(page, "monsters", "Goblin - 3").locator("button[data-remove-kind]").click()
    expect(page.locator("#monsters input.bulk-selection-checkbox")).to_have_count(2)
    assert sorted(roster_names(page, "monsters")) == ["Goblin - 2", "Goblin Boss"]
    assert session.dialogs[-1] == ("confirm", "Remove monster “Goblin - 3” from the current battle setup?")


def test_monster_hp_from_dice_expression(sessions):
    """A dice expression in HP Range start rolls HP within its range."""
    _, page = admin(sessions, "preparation")
    add_monster(page, "Ogre", hp="2d6+3", quantity=2)
    for name in ("Ogre - 1", "Ogre - 2"):
        text = row(page, "monsters", name).locator("td").nth(3).inner_text()
        current, maximum = map(int, re.fullmatch(r"(\d+)/(\d+)", text.strip()).groups())
        assert current == maximum and 5 <= maximum <= 15


def test_bulk_select_all_and_remove(sessions):
    """Bulk select-all, unselect-all and remove for characters and monsters."""
    session, page = admin(sessions)
    for name in ("Aelwyn", "Borin", "Cara"):
        add_character(page, name)
    boxes = page.locator("#characters input.bulk-selection-checkbox")
    page.click("#selectAllCharacters")
    for box in boxes.all():
        expect(box).to_be_checked()
    page.select_option("#characterBulkAction", "unselect-all")
    for box in boxes.all():
        expect(box).not_to_be_checked()
    row(page, "characters", "Borin").locator("input.bulk-selection-checkbox").check()
    page.select_option("#characterBulkAction", "remove")
    expect(boxes).to_have_count(2)
    assert roster_names(page, "characters") == ["Aelwyn", "Cara"]
    assert session.dialogs[-1] == ("confirm", "Remove 1 selected character from the active campaign?\n\nBorin")

    add_monster(page, "Wolf", quantity=4)
    page.click("#selectAllMonsters")
    page.select_option("#monsterBulkAction", "remove")
    expect(page.locator("#monsters input.bulk-selection-checkbox")).to_have_count(0)
    assert session.dialogs[-1][1].startswith("Remove 4 selected monsters from the current battle setup?")


def test_bulk_actions_need_a_selection(sessions):
    """Bulk actions stay disabled until a combatant is selected."""
    _, page = admin(sessions)
    add_character(page, "Aelwyn")
    remove = page.locator("#characterBulkAction option[value=remove]")
    clear = page.get_by_role("button", name="Clear selection").first
    expect(remove).to_be_disabled()
    expect(clear).to_be_disabled()
    row(page, "characters", "Aelwyn").locator("input.bulk-selection-checkbox").check()
    expect(remove).to_be_enabled()
    expect(page.locator("#charactersSelectedCount")).to_contain_text("1")
    clear.click()
    expect(remove).to_be_disabled()
    expect(page.locator("#characters input.bulk-selection-checkbox")).not_to_be_checked()


def test_compact_initiative_inputs(sessions):
    """Inline initiative inputs in both rosters use the compact 7.5ch width."""
    _, page = admin(sessions)
    add_character(page, "Aelwyn", initiative=12)
    add_monster(page, "Goblin")
    for selector in ("#characters input[data-ci]", "#monsters input[data-mi]"):
        width, reference = page.locator(selector).first.evaluate("""node => {
            const probe = document.createElement('span');
            probe.style.cssText = 'display:inline-block;width:7.5ch;font:inherit';
            node.after(probe);
            const sizes = [node.getBoundingClientRect().width, probe.getBoundingClientRect().width];
            probe.remove();
            return sizes;
        }""")
        assert abs(width - reference) < 1, (selector, width, reference)
        assert width < 120


def test_monster_refresh_review_without_sources(sessions):
    """Refresh from source reviews only the selected monsters and applies nothing when no source exists."""
    _, page = admin(sessions, "preparation")
    add_monster(page, "Goblin", ac=15, hp=7, bonus=2, quantity=3)
    refresh = page.locator("#monsterBulkAction option[value=refresh-source-review]")
    expect(refresh).to_be_disabled()
    row(page, "monsters", "Goblin - 1").locator("input.bulk-selection-checkbox").check()
    row(page, "monsters", "Goblin - 3").locator("input.bulk-selection-checkbox").check()
    expect(refresh).to_be_enabled()
    page.select_option("#monsterBulkAction", "refresh-source-review")
    dialog = page.locator("dialog.sg-refresh-review")
    expect(dialog).to_be_visible()
    expect(dialog.get_by_role("heading")).to_have_text("Refresh selected monsters from source")
    expect(dialog).to_contain_text("Review ready")
    expect(dialog).to_contain_text("Goblin - 1")
    expect(dialog).to_contain_text("Goblin - 3")
    expect(dialog).not_to_contain_text("Goblin - 2")
    expect(dialog).to_contain_text("No usable source candidates found")
    expect(dialog.get_by_role("button", name="Apply selected changes")).to_be_disabled()
    dialog.get_by_role("button", name="Cancel").click()
    expect(page.locator("dialog.sg-refresh-review")).to_have_count(0)
    goblin = row(page, "monsters", "Goblin - 1")
    expect(goblin.locator("td").nth(2)).to_have_text("15")
    expect(goblin.locator(".sg-monster-initiative-bonus")).to_have_text("+2")
