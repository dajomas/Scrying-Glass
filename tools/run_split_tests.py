"""Run legacy source-reading fixtures against an assembled temporary checkout.

Usage: python tools/run_split_tests.py -- python -m unittest discover -s tests
The real checkout and its tracked admin.js marker are never overwritten.
"""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from python.scrying_glass_admin_source import read_admin_script


def main():
    command = sys.argv[1:]
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        raise SystemExit("Supply a test command after --")
    bundle = read_admin_script(ROOT / "static")
    with tempfile.TemporaryDirectory(prefix="scrying-tests-") as temporary:
        target = Path(temporary) / "repo"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(
            ".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache",
            "scrying-glass-data", "monster-display-data", "output", "config.yaml", ".env"))
        (target / "static/admin.js").write_bytes(bundle)
        env = os.environ.copy()
        old_paths = env.get("PYTHONPATH", "").split(os.pathsep)
        excluded = {ROOT, ROOT / "tests"}
        paths = [str(target), str(target / "tests")]
        paths.extend(p for p in old_paths if p and Path(p).resolve() not in excluded)
        env["PYTHONPATH"] = os.pathsep.join(paths)
        return subprocess.run(command, cwd=target, env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
