"""Real local Git publication lifecycle; test commands are stubbed, no network."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('git') and shutil.which('bash'), 'Git and Bash required')
class LocalRunnerPublicationTests(unittest.TestCase):
    def git(self, *args, cwd=None):
        result = subprocess.run(['git', *args], cwd=cwd or self.repo,
                                env=self.env, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='sg-runner-publication-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.remote = self.base / 'remote.git'
        self.scratch = self.base / 'scratch'
        self.scratch.mkdir()
        self.env = os.environ.copy()
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
                        SG_LOCAL_TEST_TMPDIR=str(self.scratch), SG_RUNNER_FIXTURE_EXIT='0')
        self.git('init', '--bare', str(self.remote), cwd=self.base)
        self.git('init', '-b', 'features/perplexity')
        self.git('config', 'user.name', 'Runner Fixture')
        self.git('config', 'user.email', 'runner-fixture@example.invalid')
        shutil.copyfile(ROOT / 'runlocaltests.sh', self.repo / 'runlocaltests.sh')
        (self.repo / 'tools').mkdir()
        (self.repo / 'tools/run_split_tests.py').write_text('', encoding='utf-8')
        (self.repo / 'tests').mkdir()
        (self.repo / 'tests/fixture.txt').write_text('fixture', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-m', 'fixture seed')
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', 'origin', 'HEAD:refs/heads/features/perplexity')
        self.original = self.git('rev-parse', 'HEAD')
        self.old_log = self.repo / 'local-tests-0000000/publication-run-20000101T000000Z-older0.log'
        self.old_log.parent.mkdir()
        self.old_log.write_text('retain unrelated log', encoding='utf-8')
        self.python = self.base / 'fixture-python'
        self.python.write_text('#!/usr/bin/env bash\n'
                               'if [[ "${1:-}" == --version ]]; then echo "Python fixture"; exit 0; fi\n'
                               'exit "${SG_RUNNER_FIXTURE_EXIT:-0}"\n', encoding='utf-8')
        self.python.chmod(0o755)

    def run_runner(self, *args):
        result = subprocess.run(['bash', 'runlocaltests.sh', '--suite', 'syntax',
                                 '--python', str(self.python), *args], cwd=self.repo,
                                env=self.env, capture_output=True, text=True, timeout=30)
        runs = list(self.repo.glob('local-tests-*/run-*'))
        self.assertEqual(len(runs), 1, result.stdout + result.stderr)
        self.run = runs[0]
        self.log = self.run.parent / ('publication-' + self.run.name + '.log')
        self.assertEqual(self.old_log.read_text(encoding='utf-8'), 'retain unrelated log')
        self.assertIn('completed=1', (self.run / 'environment.txt').read_text(encoding='utf-8'))
        return result

    def assert_pushed(self):
        head = self.git('rev-parse', 'HEAD')
        remote = self.git('--git-dir', str(self.remote), 'rev-parse', 'refs/heads/features/perplexity')
        self.assertNotEqual(head, self.original)
        self.assertEqual(head, remote)
        changed = self.git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').splitlines()
        relative = self.run.relative_to(self.repo).as_posix() + '/'
        self.assertTrue(changed)
        self.assertTrue(all(name.startswith(relative) for name in changed), changed)
        self.assertIn('[skip ci]', self.git('log', '-1', '--format=%s'))

    def test_successful_push_removes_only_current_publication_log(self):
        result = self.run_runner()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_pushed()
        self.assertFalse(self.log.exists())
        self.assertEqual((self.run / 'exit-code.txt').read_text().strip(), '0')

    def test_failed_tests_still_remove_log_when_publication_succeeds(self):
        self.env['SG_RUNNER_FIXTURE_EXIT'] = '1'
        result = self.run_runner()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assert_pushed()
        self.assertFalse(self.log.exists())
        self.assertEqual((self.run / 'exit-code.txt').read_text().strip(), '1')

    def test_failed_push_preserves_publication_log_and_evidence(self):
        hook = self.remote / 'hooks/pre-receive'
        hook.write_text('#!/bin/sh\nexit 1\n', encoding='utf-8')
        hook.chmod(0o755)
        result = self.run_runner()
        self.assertEqual(result.returncode, 1)
        self.assertIn('publication_exit=1', self.log.read_text(encoding='utf-8'))
        self.assertEqual(self.git('--git-dir', str(self.remote), 'rev-parse',
                                  'refs/heads/features/perplexity'), self.original)
        self.assertEqual((self.run / 'exit-code.txt').read_text().strip(), '0')

    def test_no_publish_does_not_create_publication_log(self):
        result = self.run_runner('--no-publish')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.log.exists())
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.original)

    def test_staged_changes_refuse_publication_and_preserve_log(self):
        (self.repo / 'staged.txt').write_text('keep staged', encoding='utf-8')
        self.git('add', 'staged.txt')
        result = self.run_runner()
        self.assertEqual(result.returncode, 1)
        self.assertIn('Index has staged changes', self.log.read_text(encoding='utf-8'))
        self.assertIn('publication_exit=1', self.log.read_text(encoding='utf-8'))
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.original)
        self.assertEqual(self.git('diff', '--cached', '--name-only'), 'staged.txt')

    def test_cleanup_failure_reports_failure_after_successful_push(self):
        real_rm = shutil.which('rm')
        self.assertIsNotNone(real_rm)
        bin_dir = self.base / 'bin'
        bin_dir.mkdir()
        wrapper = bin_dir / 'rm'
        import shlex
        wrapper.write_text('#!/usr/bin/env bash\n'
                           'for arg in "$@"; do\n'
                           '  case "$arg" in */publication-run-*.log) exit 1 ;; esac\n'
                           'done\nexec ' + shlex.quote(real_rm) + ' "$@"\n', encoding='utf-8')
        wrapper.chmod(0o755)
        self.env['PATH'] = str(bin_dir) + os.pathsep + self.env['PATH']
        result = self.run_runner()
        self.assertEqual(result.returncode, 1)
        self.assert_pushed()
        self.assertTrue(self.log.exists())
        self.assertIn('publication_exit=0', self.log.read_text(encoding='utf-8'))
        self.assertIn('publication-log cleanup failed', result.stderr)
        self.assertEqual((self.run / 'exit-code.txt').read_text().strip(), '0')


if __name__ == '__main__':
    unittest.main()
