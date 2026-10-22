"""Chromium checks for scoped compact table editors. Requires Playwright/Chromium."""
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]

class CompactInputsTests(unittest.TestCase):
    def test_width_halved_without_height_or_unrelated_field_changes(self):
        base = (ROOT / 'static/admin.css').read_text()
        theme = ROOT / 'static/glass-theme.css'
        if theme.exists():
            base = theme.read_text() + base
        markup = """<div id="characters"><input type="number" class="hp-edit" data-chp="c" value="123"><input type="number" class="hp-edit" data-cmaxhp="c" value="999"><input type="number" class="initiative-edit" data-ci="c" value="-10"></div><div id="monsters"><input type="number" class="initiative-edit" data-mi="m" value="20"></div><div class="field-compact"><input id="setup" type="number"></div><div id="editModal"><input id="modal" type="number" name="initiative"></div>"""
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=['--no-sandbox'])
            page = browser.new_page()
            page.set_content('<style>' + base + '</style>' + markup)
            measure = """() => Array.from(document.querySelectorAll('input')).map(el => ({width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}))"""
            before = page.evaluate(measure)
            page.add_style_tag(content=(ROOT / 'static/compact-combatant-inputs.css').read_text())
            for width in (1440, 800, 390):
                page.set_viewport_size({'width': width, 'height':900})
                after = page.evaluate(measure)
                for i in range(4):
                    self.assertAlmostEqual(after[i]['width'], before[i]['width']/2, delta=.1)
                    self.assertEqual(after[i]['height'], before[i]['height'])
                for i in (4,5):
                    self.assertEqual(after[i], before[i])
            page.locator('[data-chp]').fill('42')
            self.assertEqual(page.locator('[data-chp]').input_value(), '42')
            browser.close()

if __name__ == '__main__':
    unittest.main()
