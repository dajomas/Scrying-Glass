"""Campaigns, battle setups and campaign backups against a real server."""
import zipfile

from playwright.sync_api import expect

from helpers import admin, open_workflow


def create_campaign(page, name, description=""):
    page.click("#newCampaign")
    page.fill("#campaignForm [name=name]", name)
    page.fill("#campaignForm [name=description]", description)
    page.click("#campaignSubmit")
    expect(page.locator("#campaignModal")).to_be_hidden()
    expect(page.locator("#campaignNotification")).to_contain_text(f"Created and switched to campaign: {name}")


def selected_campaign(page):
    return page.locator("#campaignSelect option:checked")


def test_create_edit_and_switch_campaigns(sessions):
    """Create, edit and switch campaigns; choice survives reload."""
    _, page = admin(sessions)
    create_campaign(page, "Lost Mine", "Phandelver")
    expect(selected_campaign(page)).to_have_text("Lost Mine (1)")
    expect(page.locator("#adminContextCampaign")).to_have_text("Lost Mine")
    expect(page.locator("#activeCampaignInfo")).to_contain_text("Phandelver")

    page.click("#editCampaign")
    expect(page.locator("#campaignModalTitle")).to_have_text("Edit campaign: Lost Mine")
    expect(page.locator("#campaignForm [name=description]")).to_have_value("Phandelver")
    page.fill("#campaignForm [name=name]", "Lost Mine of Phandelver")
    page.click("#campaignSubmit")
    expect(page.locator("#campaignModal")).to_be_hidden()
    expect(selected_campaign(page)).to_have_text("Lost Mine of Phandelver (1)")

    page.select_option("#campaignSelect", label="Default (1)")
    page.click("#switchCampaign")
    expect(page.locator("#adminContextCampaign")).to_have_text("Default")
    page.reload()
    expect(page.locator("#adminContextCampaign")).to_have_text("Default")
    expect(page.locator("#campaignSelect option")).to_have_text(["Default (1)", "Lost Mine of Phandelver (1)"])


def test_campaign_name_is_required(sessions):
    """New campaign requires a name; cancel leaves campaigns unchanged."""
    _, page = admin(sessions)
    page.click("#newCampaign")
    page.click("#campaignSubmit")
    expect(page.locator("#campaignModal")).to_be_visible()
    assert page.locator("#campaignForm [name=name]").evaluate("input => !input.validity.valid")
    page.click("#cancelCampaign")
    expect(page.locator("#campaignModal")).to_be_hidden()
    expect(page.locator("#campaignSelect option")).to_have_count(1)


def test_last_campaign_cannot_be_deleted(sessions):
    """The last remaining campaign cannot be deleted."""
    _, page = admin(sessions)
    page.click("#deleteCampaign")
    expect(page.locator("#campaignDeleteModal")).to_be_hidden()
    expect(page.get_by_text("The last remaining campaign cannot be deleted").first).to_be_visible()
    expect(page.locator("#campaignSelect option")).to_have_count(1)


def test_delete_campaign_moving_its_setups(sessions):
    """Delete a campaign and move its setups to another campaign."""
    _, page = admin(sessions)
    create_campaign(page, "Doomed")
    page.click("#deleteCampaign")
    modal = page.locator("#campaignDeleteModal")
    expect(modal).to_be_visible()
    expect(page.locator("#campaignDeleteTarget option:checked")).to_have_text("Default")
    page.select_option("#campaignDeleteTarget", label="Doomed (active)")
    page.select_option("#campaignDeleteAction", "move")
    page.select_option("#campaignDeleteMoveTo", label="Default")
    modal.get_by_role("button", name="Delete").click()
    expect(modal).to_be_hidden()
    expect(page.locator("#campaignSelect option")).to_have_count(1)
    expect(page.locator("#campaignSelect option")).to_have_text("Default (2)")


def test_delete_campaign_with_its_setups(sessions):
    """Delete a campaign together with its setups."""
    _, page = admin(sessions)
    create_campaign(page, "Scratch")
    page.click("#deleteCampaign")
    modal = page.locator("#campaignDeleteModal")
    page.select_option("#campaignDeleteTarget", label="Scratch (active)")
    page.select_option("#campaignDeleteAction", "delete")
    expect(page.locator("#campaignDeleteMoveLabel")).to_be_hidden()
    modal.get_by_role("button", name="Delete").click()
    expect(modal).to_be_hidden()
    expect(page.locator("#campaignSelect option")).to_have_text("Default (1)")


def test_battle_setup_save_load_rename_and_delete(sessions):
    """Battle setup save, load, rename and delete."""
    session, page = admin(sessions, "preparation")
    setups = page.locator("#setupSelect option:not([value=''])")
    expect(setups).to_have_text(["default"])
    page.fill("#setupName", "goblin-ambush")
    page.click("#saveSetup")
    expect(setups).to_have_text(["default", "goblin-ambush"])
    expect(page.locator("#adminContextSetup")).to_have_text("goblin-ambush")

    page.select_option("#setupSelect", "default")
    page.click("#loadSetup")
    expect(page.locator("#adminContextSetup")).to_have_text("default")

    page.select_option("#setupSelect", "goblin-ambush")
    session.prompts.append("wolf-ambush")
    page.click("#renameSetup")
    expect(setups).to_have_text(["default", "wolf-ambush"])

    page.select_option("#setupSelect", "wolf-ambush")
    page.click("#deleteSetup")
    expect(setups).to_have_text(["default"])
    assert [kind for kind, _ in session.dialogs] == ["prompt", "confirm"]


def test_add_setup_copy_to_another_campaign(sessions):
    """Copy a saved setup to another campaign."""
    _, page = admin(sessions, "preparation")
    page.fill("#setupName", "ambush")
    page.click("#saveSetup")
    expect(page.locator("#setupSelect option:not([value=''])")).to_have_text(["ambush", "default"])
    open_workflow(page, "campaign")
    create_campaign(page, "Second")
    page.click("#openCampaignSetup")
    modal = page.locator("#campaignSetupModal")
    expect(modal).to_be_visible()
    page.select_option("#campaignSetupFrom", label="Default (2)")
    page.select_option("#campaignSetupName", "ambush")
    expect(page.locator("#campaignSetupTo option:checked")).to_have_text("Second (1)")
    page.select_option("#campaignSetupForm [name=mode]", "copy")
    modal.get_by_role("button", name="Add").click()
    expect(modal).to_be_hidden()
    expect(page.locator("#campaignSelect option")).to_have_text(["Default (2)", "Second (2)"])
    open_workflow(page, "preparation")
    expect(page.locator("#setupSelect option:not([value=''])")).to_have_text(["ambush", "default"])


def test_export_and_import_campaign_bundle(sessions, tmp_path):
    """Export a campaign bundle and import it as a new campaign."""
    _, page = admin(sessions)
    create_campaign(page, "Exported", "bundle round trip")
    page.click(".et-backup-panel > summary")
    with page.expect_download() as info:
        page.click("#exportBundle")
    bundle = tmp_path / info.value.suggested_filename
    info.value.save_as(bundle)
    with zipfile.ZipFile(bundle) as archive:
        assert archive.namelist()
    page.set_input_files("#importBundle", str(bundle))
    expect(page.locator("#campaignSelect option")).to_have_count(3)
    expect(page.locator("#campaignSelect")).to_contain_text("Exported")
    expect(selected_campaign(page)).to_contain_text("Exported")
