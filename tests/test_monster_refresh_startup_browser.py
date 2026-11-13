"""Chromium startup regression with delayed roster state; not full-server acceptance."""
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class RefreshStartupBrowserTests(unittest.TestCase):
    def test_unready_states_do_not_prune_selection_or_dispatch_requests(self):
        runtime = sync_playwright().start()
        self.addCleanup(runtime.stop)
        browser = runtime.chromium.launch(headless=True)
        self.addCleanup(browser.close)
        page = browser.new_page()
        page.set_default_timeout(5000)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content('<select id="monsterBulkAction"></select><div id="monsters"></div>')
        page.add_script_tag(content="""
            let latest;
            const chosen = new Set(['a']);
            window.selectionReads = 0;
            window.requests = 0;
            function selectedIds() {
                window.selectionReads++;
                const valid = new Set(latest.monsters.map(item => item.id));
                return [...chosen].filter(id => valid.has(id));
            }
            function updateRowSelection(kind,id,value) {if(value) chosen.add(id); else chosen.delete(id);}
            function setAllSelected(kind,value) {chosen.clear(); if(value) chosen.add('a');}
            async function runBulkAction() {throw new Error('Unexpected bulk dispatch');}
            async function request() {window.requests++; throw new Error('Unexpected network request');}
        """)
        for file in ('monster-refresh-selection.js', 'monster-refresh-review.js'):
            page.add_script_tag(content=(ROOT/'static'/file).read_text())
        option = page.locator('option[value="refresh-source-review"]')
        self.assertTrue(option.is_disabled())
        for value in ('undefined', 'null', '{}'):
            with self.subTest(value=value):
                page.evaluate(f"latest={value}; document.querySelector('#monsters').replaceChildren(document.createElement('span'))")
                page.evaluate("runBulkAction('monsters','refresh-source-review')")
                self.assertTrue(option.is_disabled())
        self.assertEqual(page.evaluate('window.selectionReads'), 0)
        self.assertEqual(page.evaluate('window.requests'), 0)
        page.evaluate("latest={monsters:[{id:'a',name:'Alpha'}]}; document.querySelector('#monsters').replaceChildren(document.createElement('span'))")
        page.wait_for_function("!document.querySelector('option[value=\"refresh-source-review\"]').disabled")
        page.evaluate("updateRowSelection('monsters','a',false)")
        self.assertTrue(option.is_disabled())
        page.evaluate("updateRowSelection('monsters','a',true)")
        self.assertFalse(option.is_disabled())
        self.assertEqual(page.evaluate('window.requests'), 0)
        self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
