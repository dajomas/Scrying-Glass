"""Runtime-preflight contracts with mocked dependencies/import subprocess."""
from contextlib import redirect_stdout, redirect_stderr
import io
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch
from deployment import check


class RuntimePreflightTests(unittest.TestCase):
    def test_default_and_legacy_flag_are_equivalent(self):
        with patch.object(check, 'runtime_preflight', return_value=7) as run:
            self.assertEqual(check.main([]), 7)
            self.assertEqual(check.main(['--runtime']), 7)
            self.assertEqual(run.call_args_list[0], run.call_args_list[1])

    def test_no_manifest_needed_and_stale_manifest_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for present in (False, True):
                if present:
                    (root / 'package-manifest.json').write_text('not valid JSON')
                out = io.StringIO()
                with patch.object(check.importlib.metadata, 'version', return_value='fixture'), \
                     patch.object(check.importlib.util, 'find_spec', return_value=object()), \
                     patch.object(check.subprocess, 'run', return_value=types.SimpleNamespace(returncode=0)) as run, \
                     redirect_stdout(out):
                    self.assertEqual(check.runtime_preflight(root), 0)
                self.assertEqual(run.call_args.kwargs['cwd'], str(root))
                self.assertIn('package integrity is not verified', out.getvalue())
                self.assertIn('Storage, listeners, browser workflows and authentication are not exercised', out.getvalue())

    def test_missing_dependencies_stop_before_server_import(self):
        with patch.object(check.importlib.metadata, 'version', side_effect=check.importlib.metadata.PackageNotFoundError('fixture')), \
             patch.object(check.subprocess, 'run') as run, \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(check.runtime_preflight(Path('.')), 1)
            run.assert_not_called()

    def test_server_import_failure_is_propagated(self):
        with patch.object(check.importlib.metadata, 'version', return_value='fixture'), \
             patch.object(check.importlib.util, 'find_spec', return_value=object()), \
             patch.object(check.subprocess, 'run', return_value=types.SimpleNamespace(returncode=3)), \
             redirect_stdout(io.StringIO()):
            self.assertEqual(check.runtime_preflight(Path('.')), 3)


if __name__ == '__main__':
    unittest.main()
