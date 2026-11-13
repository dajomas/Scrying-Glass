"""Combat flow against a real server (SG-TODO-021 Stage 3)."""
from playwright.sync_api import expect

from helpers import (admin, hp_cell, open_workflow, option_value, prepare_battle, row, show_rosters,
                     start_battle)


def open_actions(page, actor):
    page.locator("#battleInfo button[data-battle-actor]").click()
    expect(page.locator("#battleActionModal")).to_be_visible()
    expect(page.locator("#battleActionTitle")).to_have_text(f"Battle actions: {actor}")


def action_row(page, index=0):
    return page.locator("#battleActionRows .battle-action-row").nth(index)


def fill_action(page, row_locator, target, kind="damage", amount=None):
    select = row_locator.locator("[data-action-target]")
    select.select_option(option_value(select, target))
    row_locator.locator("[data-action-kind]").select_option(kind)
    if amount is not None:
        row_locator.locator("[data-action-amount]").fill(str(amount))


def apply_actions(page):
    page.click("#battleActionForm button[type=submit]")
    expect(page.locator("#battleActionNotice")).to_contain_text("Applied")


def test_start_and_end_need_a_battle(sessions):
    """Start needs a turn-eligible participant and End needs an active battle."""
    _, page = admin(sessions, "live")
    page.click("#startBattle")
    expect(page.locator("#message")).to_contain_text("Error: Activate at least one turn-eligible participant first")
    page.click("#endBattle")
    expect(page.locator("#message")).to_contain_text("Error: There is no active battle to end.")
    expect(page.locator("#battleState")).to_have_text("Inactive")
    expect(page.locator("#battleRound")).to_be_hidden()


def test_start_battle_marks_first_turn(sessions):
    """Starting a battle shows round 1 with the highest initiative on turn."""
    _, page = admin(sessions)
    prepare_battle(page, characters=(("Borin", 20), ("Cara", 5)))
    start_battle(page)
    expect(page.locator("#battleRound")).to_have_text("Round 1")
    expect(page.locator("#battleInfo")).to_have_text("Order: Borin ⇒ Orc ⇒ Cara")
    expect(page.locator("#battleInfo button[data-battle-actor]")).to_have_text("Borin")


def test_turn_actions_apply_damage_and_healing(sessions):
    """Battle actions apply damage and healing, lock applied rows and update HP."""
    _, page = admin(sessions)
    prepare_battle(page, characters=(("Borin", 20), ("Cara", 15)))
    start_battle(page)
    open_actions(page, "Borin")
    expect(page.locator("#battleTurnCombatant")).to_have_text("Borin: HP 20/20 · Temporary HP 0")
    fill_action(page, action_row(page), "Orc", amount=4)
    page.click("#addBattleActionTarget")
    fill_action(page, action_row(page, 1), "Orc", kind="heal", amount=1)
    apply_actions(page)
    expect(page.locator("#battleActionNotice")).to_contain_text("Applied 2 battle actions.")
    expect(page.locator(".battle-action-applied-status")).to_have_count(2)
    expect(action_row(page).locator("[data-action-target]")).to_be_disabled()
    page.click("#closeBattleActions")
    expect(page.locator("#battleActionModal")).to_be_hidden()
    show_rosters(page)
    expect(hp_cell(page, "monsters", "Orc")).to_have_text("12/15")


def test_start_of_turn_damage_and_healing(sessions):
    """Start-of-turn damage is applied before healing to the current combatant."""
    _, page = admin(sessions)
    prepare_battle(page)
    start_battle(page)
    open_actions(page, "Borin")
    page.fill("#battleTurnDamage", "6")
    page.fill("#battleTurnHealing", "2")
    page.get_by_role("button", name="Apply start of turn").click()
    expect(page.locator("#battleTurnCombatant")).to_have_text("Borin: HP 16/20 · Temporary HP 0")
    page.click("#closeBattleActions")
    show_rosters(page)
    expect(hp_cell(page, "characters", "Borin")).to_have_text("16/20")


def test_next_advances_turns_and_rounds(sessions):
    """Next in the action dialog opens the next combatant, and the round advances after the last."""
    _, page = admin(sessions)
    prepare_battle(page)
    start_battle(page)
    open_actions(page, "Borin")
    page.click("#nextBattleActions")
    expect(page.locator("#battleActionTitle")).to_have_text("Battle actions: Orc")
    expect(page.locator("#battleInfo button[data-battle-actor]")).to_have_text("Orc")
    page.click("#closeBattleActions")
    page.click("#nextBattle")
    expect(page.locator("#battleRound")).to_have_text("Round 2")
    expect(page.locator("#battleInfo button[data-battle-actor]")).to_have_text("Borin")


def test_only_current_combatant_can_act(sessions):
    """Battle actions for a combatant that is not on turn are refused."""
    _, page = admin(sessions)
    prepare_battle(page)
    start_battle(page)
    orc = page.evaluate("latest.monsters.find(m => m.name === 'Orc').id")
    page.evaluate("id => openBattleActions(id)", orc)
    expect(page.locator("#message")).to_contain_text(
        "Error: Only the current active combatant can perform battle actions.")
    expect(page.locator("#battleActionModal")).to_be_hidden()


def test_statistics_reduction_and_restore(sessions):
    """A Max HP reduction lowers maximum HP; restoring it does not heal current HP."""
    session, page = admin(sessions)
    prepare_battle(page)
    start_battle(page)
    open_actions(page, "Borin")
    fill_action(page, action_row(page), "Orc", amount=4)
    page.click("#addStatisticsReduction")
    reduction = page.locator("#battleActionRows .statistics-reduction-row")
    reduction.locator("[data-action-target]").select_option(option_value(reduction.locator("[data-action-target]"), "Orc"))
    reduction.locator("[data-action-stat]").select_option("max_hp")
    reduction.locator("[data-action-amount]").fill("3")
    apply_actions(page)
    page.click("#closeBattleActions")
    show_rosters(page)
    expect(hp_cell(page, "monsters", "Orc")).to_have_text("11/12")

    open_workflow(page, "preparation")
    show_rosters(page)
    row(page, "monsters", "Orc").locator("button[data-statistics]").click()
    modal = page.locator("#statisticsModal")
    expect(modal).to_be_visible()
    expect(page.locator("#statisticsFields")).to_contain_text("Max HP")
    expect(page.locator("#statisticsFields tr", has_text="Max HP")).to_contain_text("15")
    page.click("#statisticsRestore")
    expect(page.locator("#statisticsNotice")).to_have_text("Saved.")
    assert session.dialogs[-1] == ("confirm", "Restore selected statistics of “Orc” to their original/base values? "
                                              "Current HP will not heal.")
    page.click("#statisticsClose")
    expect(hp_cell(page, "monsters", "Orc")).to_have_text("11/15")


def test_damage_preview_with_temporary_hp(sessions):
    """Encounter tools preview damage, absorb it with temporary HP first and update HP."""
    session, page = admin(sessions)
    prepare_battle(page)
    start_battle(page)
    page.click("#toggleEncounterTools")
    expect(page.locator("#featureTarget option", has_text="Orc")).to_have_count(1)
    page.select_option("#featureTarget", option_value(page.locator("#featureTarget"), "Orc"))
    expect(page.locator("#featureHealth")).to_contain_text("Orc: standing · HP 15/15 · Temporary HP 0")
    page.click(".et-health-panel > summary")
    page.fill("#featureTempHp", "3")
    page.click("#setTempHp")
    expect(page.locator("#featureHealth")).to_contain_text("Temporary HP 3")
    page.fill("#featureHpDelta", "-5")
    page.click("#applyFeatureHp")
    expect(page.locator("#featureHealth")).to_contain_text("HP 13/15 · Temporary HP 0")
    assert ("confirm", "Orc: HP 15 → 13; temporary HP 3 → 0. Apply?") in session.dialogs


def test_end_battle_keeps_combatants(sessions):
    """Ending a battle asks first and keeps combatant HP and roster state."""
    session, page = admin(sessions)
    prepare_battle(page)
    start_battle(page)
    open_actions(page, "Borin")
    fill_action(page, action_row(page), "Orc", amount=5)
    apply_actions(page)
    page.click("#closeBattleActions")
    page.click("#endBattle")
    expect(page.locator("#message")).to_contain_text("Success: Battle ended. Combatants were not reset.")
    kind, text = session.dialogs[-1]
    assert kind == "confirm" and text.startswith("End the battle in ") and text.endswith(
        " without resetting combatants?"), text
    expect(page.locator("#battleState")).to_have_text("Inactive")
    show_rosters(page)
    expect(hp_cell(page, "monsters", "Orc")).to_have_text("10/15")
