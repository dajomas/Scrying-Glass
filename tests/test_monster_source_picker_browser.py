"""Chromium fixture for SG-TODO-016 source/monster dropdowns with intercepted HTTP."""
import json
import unittest
import test_monster_candidate_browser as base

ROOT = base.ROOT

SOURCES = {"status": "ok", "unavailable": [], "sources": [
    {"provider": "5e.tools", "source": "MM", "legacy": True},
    {"provider": "Open5e", "source": "srd-2014", "label": "5e 2014 Rules", "legacy": True}]}
GOBLIN = dict(found=True, name="Goblin", species="Goblin", provider="5e.tools", source="MM", legacy=True,
              ac=15, hp="2d6", selection_token="pick-token", image_url=None)


class SourcePickerTests(unittest.TestCase):
    def setUp(self):
        base.CandidateBrowserTests.setUp(self)
        self.lists = {}
        self.page.route("**/api/monsters/catalog/sources", lambda r: r.fulfill(json=SOURCES))
        self.page.route("**/api/monsters/catalog/monsters?*", self.serve_list)
        self.page.route("**/api/monsters/catalog/monster?*", lambda r: r.fulfill(json={"status": "ok", "candidate": GOBLIN}))
        self.page.evaluate("""() => {
            const name = document.createElement('input'); name.id = 'monsterName';
            document.querySelector('#monsterForm').prepend(name);
            const species = document.querySelector('#monsterSpecies'); species.value = '';
            const label = document.createElement('label'); label.className = 'field';
            species.before(label); label.append(species);
            document.querySelector('#monsterSpeciesLookupOverwrite').checked = false;
        }""")
        self.page.add_script_tag(content=(ROOT / "static/monster-source-picker.js").read_text())
        self.page.locator("#monsterSourceSelect option").nth(2).wait_for(state="attached")

    def serve_list(self, route):
        source = route.request.url.split("source=")[1]
        self.lists[source] = self.lists.get(source, 0) + 1
        if source == "srd-2014":
            route.fulfill(json={"status": "error", "reason": "Incomplete Open5e listing"})
        else:
            route.fulfill(json={"status": "ok", "complete": True,
                                "monsters": [{"id": "Aboleth", "name": "Aboleth"}, {"id": "Goblin", "name": "Goblin"}]})

    def test_none_default_sources_and_hidden_monster_list(self):
        source = self.page.get_by_label("Source", exact=True)
        self.assertEqual(source.input_value(), "")
        self.assertEqual(source.locator("option").all_inner_texts(),
                         ["None", "5e.tools / Monster Manuals 2014", "Open5e / 5e 2014 Rules / legacy"])
        self.assertFalse(self.page.locator("#monsterSourceMonster").is_visible())
        self.assertEqual(self.errors, [])

    def test_pick_fills_species_name_and_stats_with_signed_token(self):
        self.page.get_by_label("Source", exact=True).select_option(label="5e.tools / Monster Manuals 2014")
        monster = self.page.locator("#monsterSourceMonster")
        self.page.wait_for_function("!document.querySelector('#monsterSourceMonster').disabled")
        self.assertEqual(monster.locator("option").all_inner_texts(), ["Choose a monster (2)", "Aboleth", "Goblin"])
        self.assertIn("complete list", self.page.locator("#monsterSourceStatus").inner_text())
        self.page.evaluate("document.querySelector('#monsterAc').value = '9'")
        monster.select_option("Goblin")
        self.page.wait_for_function("new FormData(document.querySelector('#monsterForm')).get('selection_token') === 'pick-token'")
        self.assertEqual(self.page.locator("#monsterSpecies").input_value(), "Goblin")
        self.assertEqual(self.page.locator("#monsterName").input_value(), "Goblin")
        self.assertEqual(self.page.locator("#monsterAc").input_value(), "9")  # Overwrite off keeps entered AC.
        self.assertEqual(self.page.locator("#monsterHpRangeStart").input_value(), "2d6")
        self.assertEqual(self.page.locator("dialog").count(), 0)
        self.assertEqual(self.errors, [])

    def test_failed_list_is_not_shown_as_complete_and_none_hides_it(self):
        source = self.page.get_by_label("Source", exact=True)
        source.select_option(label="Open5e / 5e 2014 Rules / legacy")
        self.page.wait_for_function("document.querySelector('#monsterSourceStatus').textContent.includes('Could not load')")
        self.assertTrue(self.page.locator("#monsterSourceMonster").is_disabled())
        self.assertEqual(self.page.locator("#monsterSourceMonster option").all_inner_texts(), ["Monster list unavailable"])
        source.select_option("")
        self.assertFalse(self.page.locator("#monsterSourceMonster").is_visible())
        self.assertTrue(self.page.locator("#monsterSpecies").is_editable())
        self.assertEqual(self.errors, [])


if __name__ == "__main__":
    unittest.main()
