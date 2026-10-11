"""Launcher guards: execute Linux rejection path, inspect Windows contracts."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class LauncherGuardTests(unittest.TestCase):
    def test_existing_unsupported_environment_fails_before_pip(self):
        with tempfile.TemporaryDirectory() as temporary:
            home=Path(temporary);bindir=home/'dnd'/'bin';bindir.mkdir(parents=True)
            (bindir/'activate').write_text('export PATH="'+str(bindir)+':$PATH"\n')
            python=bindir/'python'
            python.write_text('#!/bin/sh\necho "$*" >> "$HOME/commands"\nexit 1\n')
            python.chmod(0o755)
            result=subprocess.run(['bash',str(ROOT/'run.sh')],env={**os.environ,'HOME':str(home)},capture_output=True,text=True,timeout=5)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Python 3.14',result.stderr)
            commands=(home/'commands').read_text()
            self.assertNotIn('pip',commands)
            self.assertNotIn('scrying_glass_server.py',commands)
            self.assertFalse((home/'dnd'/'.scrying-glass-dependencies').exists())

    def test_guards_precede_dependency_installation_on_all_platforms(self):
        for name in ('run.sh','run.ps1','run.bat'):
            with self.subTest(name=name):
                source=(ROOT/name).read_text()
                guard=source.index('sys.version_info >= (3, 14)')
                self.assertLess(guard,source.index('-m pip'))
                self.assertIn('Existing virtual environment requires Python 3.14',source)
