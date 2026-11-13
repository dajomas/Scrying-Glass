"""Provision the installed Python Playwright's Chromium and verify headless rendering."""
import subprocess
import sys


def verify_chromium():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content('<p id="ready">Chromium ready</p>')
            if page.locator('#ready').inner_text() != 'Chromium ready':
                raise RuntimeError('Chromium rendering preflight failed')
        finally:
            browser.close()


def main():
    try:
        # Download browser + default headless shell before any optional APT work.
        subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=True)
        try:
            verify_chromium()
        except Exception as error:
            print(f'Chromium preflight failed: {error}', file=sys.stderr, flush=True)
            print('Attempting native dependency installation, then rechecking Chromium.', flush=True)
            subprocess.run([sys.executable, '-m', 'playwright', 'install-deps', 'chromium'], check=True)
            verify_chromium()
    except Exception as error:
        print(f'Chromium provisioning failed: {error}', file=sys.stderr, flush=True)
        return 1
    print('Chromium headless launch/render preflight passed.', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
