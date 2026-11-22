"""tools/run_e2e.sh: the results push survives a commit that reached the branch meanwhile.

The push loop is taken from the script itself and run against throwaway git repositories:
a bare "remote" and a clone that holds the results commit.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def push_section():
    script = (ROOT / 'tools/run_e2e.sh').read_text(encoding='utf-8')
    match = re.search(r'^attempt=1\n.*?^echo "Pushed .*?$', script, re.S | re.M)
    assert match, 'push loop not found in tools/run_e2e.sh'
    return match.group(0)


@unittest.skipIf(shutil.which('git') is None or shutil.which('bash') is None, 'needs git and bash')
class E2EPushTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@e', GIT_COMMITTER_NAME='t',
                        GIT_COMMITTER_EMAIL='t@e', GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        self.git('init', '-q', '--bare', '-b', 'main', str(self.tmp / 'remote.git'), cwd=self.tmp)
        self.git('clone', '-q', str(self.tmp / 'remote.git'), 'runner', cwd=self.tmp)
        self.git('clone', '-q', str(self.tmp / 'remote.git'), 'ci', cwd=self.tmp)
        self.commit('runner', 'app.txt', 'code', 'code')
        self.git('push', '-q', 'origin', 'HEAD:refs/heads/main', cwd=self.tmp / 'runner')
        self.git('pull', '-q', 'origin', 'main', cwd=self.tmp / 'ci')

    def git(self, *args, cwd):
        return subprocess.run(['git', *args], cwd=cwd, env=self.env, check=True, capture_output=True, text=True).stdout

    def commit(self, clone, path, text, message):
        target = self.tmp / clone / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        self.git('add', '-A', cwd=self.tmp / clone)
        self.git('commit', '-q', '-m', message, cwd=self.tmp / clone)

    def run_push(self):
        script = 'set -euo pipefail\nfail() { echo "ERROR: $*" >&2; exit 1; }\nREMOTE=origin BRANCH=main STATUS=0\n' + push_section()
        return subprocess.run(['bash', '-c', script], cwd=self.tmp / 'runner', env=self.env, capture_output=True, text=True)

    def remote_log(self):
        return self.git('log', '--format=%s', 'main', cwd=self.tmp / 'remote.git').split('\n')[:-1]

    def test_push_when_nothing_changed(self):
        self.commit('runner', 'e2e-results/1/summary.md', 'green', 'E2E results 1')
        result = self.run_push()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.remote_log(), ['E2E results 1', 'code'])

    def test_rebases_onto_a_ci_results_commit_and_pushes(self):
        self.commit('ci', 'ci-results-main/run.txt', 'ok', 'ci: publish run [skip ci]')
        self.git('push', '-q', 'origin', 'HEAD:refs/heads/main', cwd=self.tmp / 'ci')
        self.commit('runner', 'e2e-results/1/summary.md', 'green', 'E2E results 1')
        result = self.run_push()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Rebased the results commit', result.stdout)
        self.assertEqual(self.remote_log(), ['E2E results 1', 'ci: publish run [skip ci]', 'code'])

    def test_refuses_when_the_remote_changed_e2e_results(self):
        self.commit('ci', 'e2e-results/0/summary.md', 'other run', 'E2E results 0')
        self.git('push', '-q', 'origin', 'HEAD:refs/heads/main', cwd=self.tmp / 'ci')
        self.commit('runner', 'e2e-results/1/summary.md', 'green', 'E2E results 1')
        result = self.run_push()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('changed e2e-results/ meanwhile', result.stderr)
        self.assertEqual(self.git('log', '-1', '--format=%s', cwd=self.tmp / 'runner').strip(), 'E2E results 1')
        self.assertEqual(self.remote_log(), ['E2E results 0', 'code'])


if __name__ == '__main__':
    unittest.main()
