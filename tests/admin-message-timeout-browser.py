from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_content('<style>#message:empty{display:none}</style><p id="message"></p>')
    page.add_script_tag(content=(Path(__file__).resolve().parents[1] / 'static/admin-message-timeout.js').read_text())
    page.evaluate("document.querySelector('#message').textContent='Test message'")
    assert page.locator('#message').is_visible()
    page.wait_for_timeout(5100)
    assert page.locator('#message').text_content() == ''
    assert not page.locator('#message').is_visible()
    browser.close()
