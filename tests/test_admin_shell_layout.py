"""Headless Chromium layout checks; requires Playwright and its Chromium browser."""
import re
import runpy
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def fixture():
    html = runpy.run_path(str(ROOT / 'web_html/admin_html.py'))['build_admin_html']()
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S)
    def inline_style(match):
        tag = match.group(0)
        href = re.search(r'href="([^"]+)"', tag)
        if 'stylesheet' not in tag or not href:
            return ''
        source = ROOT / href.group(1).split('?', 1)[0].lstrip('/')
        return '<style>' + source.read_text() + '</style>'
    return re.sub(r'<link\b[^>]*>', inline_style, html)

class AdminShellLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        cls.html = fixture()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={'width': 1440, 'height': 900})
        self.page.set_content(self.html)

    def tearDown(self):
        self.page.close()

    def bounds(self, selector):
        return self.page.locator(selector).bounding_box()

    def set_message(self, text):
        source = (ROOT / 'static/admin.js').read_text()
        setter = re.search(r'const message = text => \{.*?\n\};', source, re.S)
        self.assertIsNotNone(setter)
        self.page.evaluate('(text) => {' + setter.group(0) + 'message(text);}', text)

    def assert_scroll_boundary(self):
        header = self.bounds('#adminHeader')
        scroll = self.bounds('#adminScroll')
        self.assertAlmostEqual(header['y'] + header['height'], scroll['y'], delta=1)
        self.assertGreater(scroll['height'], 0)

    def test_title_and_toolbar_have_no_intervening_gap(self):
        title = self.bounds('#adminHeader h1')
        toolbar = self.bounds('#adminButtonBar')
        self.assertAlmostEqual(title['y'] + title['height'], toolbar['y'], delta=1)
        self.assertEqual(self.page.locator('#message').count(), 1)
        self.assertEqual(self.page.locator('#adminHeader #message').count(), 1)
        self.assertEqual(self.page.locator('#adminScroll #message').count(), 0)
        self.assertFalse(self.page.locator('#message').is_visible())

    def test_header_stays_stationary_while_all_panes_scroll(self):
        before = self.bounds('#adminButtonBar')
        self.page.locator('#adminScroll').evaluate('(node) => node.scrollTop = node.scrollHeight')
        self.assertEqual(before, self.bounds('#adminButtonBar'))
        self.assertGreater(self.page.locator('#adminScroll').evaluate('(node) => node.scrollTop'), 0)
        self.assertEqual(self.page.evaluate('document.scrollingElement.scrollTop'), 0)
        self.assertEqual(self.page.locator('#adminScroll #activityLog').count(), 1)

    def test_scroll_region_starts_below_header_after_resizing(self):
        for width in (1440, 800, 390):
            self.page.set_viewport_size({'width': width, 'height': 900})
            self.assert_scroll_boundary()
            scroll = self.bounds('#adminScroll')
            self.assertAlmostEqual(scroll['y'] + scroll['height'], 900, delta=1)

    def test_dynamic_button_visibility_reflows_without_offsets(self):
        self.page.locator('#toggleLairPane').evaluate('(node) => {node.dataset.setupHasLair="true";node.hidden=false;}')
        self.page.set_viewport_size({'width': 800, 'height': 900})
        self.assert_scroll_boundary()

    def test_activity_log_expands_in_shared_scroll_region(self):
        self.page.locator('#activityLog').evaluate("(node) => {const filler=document.createElement('div');filler.style.height='1800px';node.replaceChildren(filler);}")
        log = self.page.locator('#activityLog')
        self.assertGreater(log.bounding_box()['height'], 1800)
        self.assertLessEqual(log.evaluate('(node) => node.scrollHeight - node.clientHeight'), 1)

    def test_modal_still_covers_header_and_scroll_region(self):
        self.page.locator('#tieModal').evaluate('(node) => node.hidden=false')
        modal = self.bounds('#tieModal')
        self.assertEqual(modal['y'], 0)
        self.assertEqual(modal['height'], 900)
        self.assertTrue(self.page.evaluate('document.elementFromPoint(5,5).id === "tieModal"'))

    def test_message_remains_visible_after_scrolling_and_uses_existing_setter(self):
        self.page.locator('#adminScroll').evaluate('(node) => node.scrollTop = node.scrollHeight')
        self.set_message('The battle could not be started.')
        message = self.bounds('#message')
        bar = self.bounds('#adminButtonBar')
        self.assertTrue(self.page.locator('#message').is_visible())
        self.assertGreaterEqual(message['y'], bar['y'] + bar['height'])
        self.assertLess(message['y'] + message['height'], 900)
        self.assert_scroll_boundary()
        self.page.locator('#adminScroll').evaluate('(node) => node.scrollTop = 0')
        self.assertEqual(message, self.bounds('#message'))

    def test_clearing_message_removes_reserved_height(self):
        original = self.bounds('#adminHeader')['height']
        self.set_message('An error occurred.')
        self.assertGreater(self.bounds('#adminHeader')['height'], original)
        self.set_message('')
        self.assertFalse(self.page.locator('#message').is_visible())
        self.assertAlmostEqual(self.bounds('#adminHeader')['height'], original, delta=1)
        self.assert_scroll_boundary()

    def test_wrapped_message_resizes_header_without_overlap(self):
        self.page.set_viewport_size({'width': 390, 'height': 900})
        self.set_message('Long message: ' + 'encounter-data-' * 20)
        self.assert_scroll_boundary()
        message = self.bounds('#message')
        scroll = self.bounds('#adminScroll')
        self.assertLessEqual(message['y'] + message['height'], scroll['y'])
        self.assertLessEqual(message['x'] + message['width'], 390)

if __name__ == '__main__':
    unittest.main()
