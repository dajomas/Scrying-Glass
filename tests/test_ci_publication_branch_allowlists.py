"""Focused publisher configuration/gate checks; no GitHub API or pushes."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"features/perplexity", "features/perplexity-018", "features/perplexity-009.7"}


class PublicationBranchAllowlistsTests(unittest.TestCase):
    def test_workflow_allowlist(self):
        source = (ROOT / ".github/workflows/publish-ci-results.yml").read_text()
        match = re.search(r"^    branches: \[(.*?)\]$", source, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual({value.strip() for value in match[1].split(",")}, EXPECTED)

    @unittest.skipUnless(shutil.which("bash"), "Bash is required")
    def test_collector_gate(self):
        source = (ROOT / "tools/publish_ci_results.sh").read_text()
        gate = next(line for line in source.splitlines() if line.startswith('case "$BRANCH" in '))
        for branch in sorted(EXPECTED) + ["main", "features/perplexity-009.70", "features/perplexity-009.7/other", "untrusted"]:
            with self.subTest(branch=branch):
                result = subprocess.run(["bash", "-c", gate], env={**os.environ, "BRANCH": branch}, capture_output=True)
                self.assertEqual(result.returncode, 0 if branch in EXPECTED else 1)

    @unittest.skipUnless(shutil.which("bash"), "Bash is required")
    def test_collector_syntax(self):
        result = subprocess.run(["bash", "-n", str(ROOT / "tools/publish_ci_results.sh")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
