# Launcher orchestration tests; simulated versions, no network/server execution.
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ('python3', 'python3.14', 'python3.13', 'python3.12', 'python3.11', 'python3.10', 'python')

@unittest.skipUnless(shutil.which('bash'), 'Bash required')
class LauncherPython310Tests(unittest.TestCase):
    def run_launcher(self, version='3.10', existing=True, installed=False,
                     candidate_versions=None, sqlite_ok=True, pip_code=0, server_code=0):
        with tempfile.TemporaryDirectory(prefix='launcher paths ') as temporary:
            home = Path(temporary)
            tools = home / 'tools'; tools.mkdir()
            log = home / 'commands.jsonl'
            shim = home / 'shim.py'
            shim.write_text('''import json, os, pathlib, sys
args = sys.argv[1:]
with open(os.environ['COMMAND_LOG'], 'a') as stream:
    stream.write(json.dumps([sys.argv[0], args]) + '\\n')
if args[:1] == ['-c']:
    if 'version_info' in args[1]:
        name = pathlib.Path(sys.argv[0]).name
        version = (os.environ['VERSION'] if pathlib.Path(sys.argv[0]).parent.name == 'bin'
                   else json.loads(os.environ['VERSIONS']).get(name, os.environ['VERSION']))
        # Execute the real guard expression with a simulated sys.version_info.
        class SimulatedSys:
            version_info = tuple(map(int, version.split('.')))
            exit = staticmethod(sys.exit)
        exec(args[1].replace('import sys;', '').strip(), {'sys': SimulatedSys})
    sys.exit(0 if os.environ['SQLITE_OK'] == '1' else 7)
if args[:2] == ['-m', 'venv']:
    bindir = pathlib.Path(args[2]) / 'bin'
    bindir.mkdir(parents=True, exist_ok=True)
    target = bindir / 'python'
    target.write_text(pathlib.Path(sys.argv[0]).read_text())
    target.chmod(0o755)
    (bindir / 'activate').write_text('export PATH="' + str(bindir) + ':$PATH"\\n')
    sys.exit(0)
if args[:2] == ['-m', 'pip']:
    sys.exit(int(os.environ['PIP_CODE']))
sys.exit(int(os.environ['SERVER_CODE']))
''')
            wrapper = '#!/bin/sh\nexec ' + __import__('shlex').quote(sys.executable) + ' ' + __import__('shlex').quote(str(shim)) + ' "$0" "$@"\n'
            # The shim receives the invoked executable name as its first argument.
            shim.write_text(shim.read_text().replace('args = sys.argv[1:]', 'sys.argv = sys.argv[1:]\nargs = sys.argv[1:]'))
            for name in CANDIDATES:
                executable = tools / name; executable.write_text(wrapper); executable.chmod(0o755)
            vdir = home / 'dnd'
            if existing:
                bindir = vdir / 'bin'; bindir.mkdir(parents=True)
                executable = bindir / 'python'; executable.write_text(wrapper); executable.chmod(0o755)
                (bindir / 'activate').write_text('export PATH="' + str(bindir) + ':$PATH"\n')
            marker = vdir / '.scrying-glass-dependencies'
            if installed:
                vdir.mkdir(exist_ok=True)
                marker.write_text('fastapi>=0.115\nuvicorn[standard]>=0.30\nPyYAML>=6.0\npython-multipart')
            env = {**os.environ, 'HOME': str(home), 'PATH': str(tools) + os.pathsep + os.environ['PATH'],
                   'COMMAND_LOG': str(log), 'VERSION': version,
                   'VERSIONS': json.dumps(candidate_versions or {}), 'SQLITE_OK': str(int(sqlite_ok)),
                   'PIP_CODE': str(pip_code), 'SERVER_CODE': str(server_code)}
            result = subprocess.run(['bash', str(ROOT / 'run.sh')], env=env, capture_output=True, text=True, timeout=8)
            calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
            return result, calls, marker.exists()

    def test_existing_310_and_newer_environments_are_accepted(self):
        for version in ('3.10', '3.11', '3.12', '3.14', '3.15'):
            with self.subTest(version=version):
                result, calls, marker = self.run_launcher(version=version)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(marker)
                self.assertEqual(calls[-1][1], ['scrying_glass_server.py', '--config', 'config.yaml'])

    def test_39_is_rejected_before_sqlite_pip_or_server(self):
        result, calls, marker = self.run_launcher(version='3.9')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Python 3.10', result.stderr)
        self.assertEqual(len(calls), 1)
        self.assertFalse(marker)

    def test_fresh_environment_uses_compatible_python3(self):
        result, calls, marker = self.run_launcher(existing=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        creators = [call for call in calls if call[1][:2] == ['-m', 'venv']]
        self.assertEqual(Path(creators[0][0]).name, 'python3')
        self.assertTrue(marker)

    def test_old_default_falls_back_to_versioned_python310(self):
        versions = {name: '3.9' for name in CANDIDATES}; versions['python3.10'] = '3.10'
        result, calls, _ = self.run_launcher(existing=False, candidate_versions=versions)
        self.assertEqual(result.returncode, 0, result.stderr)
        creators = [call for call in calls if call[1][:2] == ['-m', 'venv']]
        self.assertEqual(Path(creators[0][0]).name, 'python3.10')

    def test_no_compatible_interpreter_fails_before_creation_or_pip(self):
        result, calls, marker = self.run_launcher(existing=False, version='3.9')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Python 3.10 or newer was not found', result.stderr)
        self.assertTrue(all(call[1][0] == '-c' for call in calls))
        self.assertFalse(marker)

    def test_valid_marker_skips_pip(self):
        result, calls, _ = self.run_launcher(installed=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(call[1][:2] == ['-m', 'pip'] for call in calls))

    def test_sqlite_failure_stops_before_pip(self):
        result, calls, marker = self.run_launcher(sqlite_ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('sqlite3', result.stderr)
        self.assertFalse(any(call[1][:2] == ['-m', 'pip'] for call in calls))
        self.assertFalse(marker)

    def test_pip_failure_does_not_mark_or_launch(self):
        result, calls, marker = self.run_launcher(pip_code=12)
        self.assertEqual(result.returncode, 12)
        self.assertFalse(marker)
        self.assertFalse(any(call[1][:1] == ['scrying_glass_server.py'] for call in calls))

    def test_server_exit_code_is_preserved(self):
        result, _, _ = self.run_launcher(installed=True, server_code=9)
        self.assertEqual(result.returncode, 9)

class WindowsLauncherContractTests(unittest.TestCase):
    def test_windows_selection_accepts_a_range_not_exact_310(self):
        for name in ('run.ps1', 'run.bat'):
            with self.subTest(name=name):
                text = (ROOT / name).read_text()
                self.assertIn('py -3 -c', text)
                self.assertIn('sys.version_info >= (3, 10)', text)
                self.assertNotIn('sys.version_info[:2] ==', text)
                self.assertNotIn('-3.14', text)
                self.assertIn('Python 3.10 or newer', text)
                self.assertLess(text.index('sys.version_info >= (3, 10)'), text.index('-m pip'))
                self.assertLess(text.index('import sqlite3'), text.index('-m pip'))
                self.assertIn('python -c', text)

if __name__ == '__main__':
    unittest.main()
