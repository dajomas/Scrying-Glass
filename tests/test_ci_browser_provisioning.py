"""Chromium provisioning control flow and workflow prerequisites, without downloads."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch
from types import ModuleType
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('prepare_ci_browser', ROOT / 'tools/prepare_ci_browser.py')
BROWSER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BROWSER)


class BrowserProvisioningTests(unittest.TestCase):
    def test_download_then_verify_without_unnecessary_apt(self):
        order = []
        with patch.object(BROWSER.subprocess, 'run', side_effect=lambda cmd, **kw: order.append((cmd, kw))), \
             patch.object(BROWSER, 'verify_chromium', side_effect=lambda: order.append('verify')):
            self.assertEqual(BROWSER.main(), 0)
        self.assertEqual(order, [([sys.executable, '-m', 'playwright', 'install', 'chromium'], {'check': True}), 'verify'])

    def test_failed_launch_installs_native_dependencies_then_rechecks(self):
        with patch.object(BROWSER.subprocess, 'run') as run, \
             patch.object(BROWSER, 'verify_chromium', side_effect=[RuntimeError('missing library'), None]) as verify:
            self.assertEqual(BROWSER.main(), 0)
        self.assertEqual([call.args[0] for call in run.call_args_list], [
            [sys.executable, '-m', 'playwright', 'install', 'chromium'],
            [sys.executable, '-m', 'playwright', 'install-deps', 'chromium']])
        self.assertTrue(all(call.kwargs == {'check': True} for call in run.call_args_list))
        self.assertEqual(verify.call_count, 2)

    def test_download_failure_is_not_success_or_an_apt_fallback(self):
        with patch.object(BROWSER.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'download')) as run, \
             patch.object(BROWSER, 'verify_chromium') as verify:
            self.assertEqual(BROWSER.main(), 1)
        self.assertEqual(run.call_count, 1)
        verify.assert_not_called()

    def test_native_dependency_failure_remains_failure(self):
        with patch.object(BROWSER.subprocess, 'run', side_effect=[None, subprocess.CalledProcessError(100, 'apt')]), \
             patch.object(BROWSER, 'verify_chromium', side_effect=RuntimeError('missing library')) as verify:
            self.assertEqual(BROWSER.main(), 1)
        self.assertEqual(verify.call_count, 1)

    def test_failed_second_launch_remains_failure(self):
        with patch.object(BROWSER.subprocess, 'run') as run, \
             patch.object(BROWSER, 'verify_chromium', side_effect=RuntimeError('cannot launch')) as verify:
            self.assertEqual(BROWSER.main(), 1)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(verify.call_count, 2)


    def test_preflight_launches_headless_renders_and_closes(self):
        self.check_preflight('Chromium ready', False)

    def test_render_failure_still_closes_browser_and_context(self):
        self.check_preflight('wrong content', True)

    def check_preflight(self, content, fails):
        api = ModuleType('playwright.sync_api')
        manager = MagicMock()
        api.sync_playwright = MagicMock(return_value=manager)
        browser = manager.__enter__.return_value.chromium.launch.return_value
        page = browser.new_page.return_value
        page.locator.return_value.inner_text.return_value = content
        with patch.dict(sys.modules, {'playwright.sync_api': api}):
            if fails:
                with self.assertRaisesRegex(RuntimeError, 'rendering preflight failed'):
                    BROWSER.verify_chromium()
            else:
                BROWSER.verify_chromium()
        manager.__enter__.return_value.chromium.launch.assert_called_once_with(headless=True)
        page.set_content.assert_called_once_with('<p id="ready">Chromium ready</p>')
        browser.close.assert_called_once()
        manager.__exit__.assert_called_once()


class WorkflowPrerequisiteTests(unittest.TestCase):
    def setUp(self):
        self.steps = yaml.safe_load((ROOT / '.github/workflows/tests.yml').read_text())['jobs']['tests']['steps']
        self.by_name = {step.get('name'): step for step in self.steps}

    def test_browser_preflight_is_a_required_separate_step(self):
        step = self.by_name['Provision and verify Chromium']
        self.assertEqual(step['id'], 'chromium')
        self.assertEqual(step['run'], 'python tools/prepare_ci_browser.py')
        self.assertNotIn('continue-on-error', step)
        self.assertIn("steps.python_dependencies.conclusion == 'success'", step['if'])
        python = self.by_name['Install Python test dependencies']
        self.assertEqual(python['id'], 'python_dependencies')
        self.assertNotIn('playwright install', python['run'])
        self.assertLess(self.steps.index(python), self.steps.index(step))

    def test_mixed_browser_suites_require_verified_browser_not_previous_suite_success(self):
        for name in ['Python test suite (including browser fixtures)', 'Standalone Python browser and audit checks']:
            condition = self.by_name[name]['if']
            self.assertIn('!cancelled()', condition)
            self.assertIn("steps.chromium.conclusion == 'success'", condition)
            self.assertIn("steps.python_dependencies.conclusion == 'success'", condition)
            self.assertNotIn('success()', condition)
            self.assertNotIn('continue-on-error', self.by_name[name])

    def test_independent_groups_do_not_depend_on_chromium(self):
        for name in ['Python syntax and server import checks', 'Pytest regression modules', 'JavaScript tests']:
            self.assertNotIn('steps.chromium', self.by_name[name]['if'])
        self.assertIn('node --test', self.by_name['JavaScript tests']['run'])
        self.assertIn('args=(patched)', self.by_name['Standalone Python browser and audit checks']['run'])


if __name__ == '__main__':
    unittest.main()
