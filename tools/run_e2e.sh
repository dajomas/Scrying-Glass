#!/usr/bin/env bash
# SG-TODO-021: run the Playwright end-to-end suite (Chromium and Firefox) against a
# real local server, store the results in e2e-results/<timestamp>/, keep only that
# latest results folder, then commit and push it with [skip ci].
#
# Usage: tools/run_e2e.sh [--no-push] [extra pytest arguments]
# Environment: E2E_BRANCH (default features/perplexity-021), E2E_REMOTE (default origin),
#              E2E_VENV (default .venv-e2e), E2E_HEADED=1 to show the browsers.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BRANCH="${E2E_BRANCH:-features/perplexity-021}"
REMOTE="${E2E_REMOTE:-origin}"
VENV="${E2E_VENV:-.venv-e2e}"
PUSH=1
if [[ "${1:-}" == "--no-push" ]]
then
    PUSH=0
    shift
fi

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

if (( PUSH ))
then
    [[ "$(git rev-parse --abbrev-ref HEAD)" == "$BRANCH" ]] || fail "check out $BRANCH first (or use --no-push)"
    git diff --cached --quiet || fail "the index already has staged changes; commit or unstage them first"
    git fetch --quiet "$REMOTE" "$BRANCH"
    behind="$(git rev-list --count "HEAD..$REMOTE/$BRANCH")"
    [[ "$behind" == "0" ]] || fail "local $BRANCH is $behind commit(s) behind $REMOTE/$BRANCH; pull first"
fi

if [[ ! -x "$VENV/bin/python" ]]
then
    python3 -m venv "$VENV"
fi
PY="$VENV/bin/python"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r e2e/requirements.txt
"$PY" -m playwright install chromium firefox

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="e2e-results/$STAMP"
mkdir -p "$OUT"
SHA="$(git rev-parse HEAD)"

set +e
E2E_ARTIFACTS="$ROOT/$OUT" "$PY" -m pytest -c e2e/pytest.ini e2e -q -rA \
    --junitxml="$OUT/junit.xml" --html="$OUT/report.html" --self-contained-html "$@" \
    2>&1 | tee "$OUT/pytest.log"
STATUS="${PIPESTATUS[0]}"
set -e

"$PY" - "$OUT" "$SHA" "$STATUS" <<'PY'
import sys, xml.etree.ElementTree as ET
from pathlib import Path
out, sha, status = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
per_browser = {}
junit = out / "junit.xml"
if junit.exists():
    for case in ET.parse(junit).iter("testcase"):
        name = case.get("name", "")
        browser = name[name.rfind("[") + 1:-1] if name.endswith("]") else "server-only"
        result = "passed"
        for tag in ("failure", "error", "skipped"):
            if case.find(tag) is not None:
                result = tag
        counts["tests"] += 1
        counts[{"failure": "failures", "error": "errors", "skipped": "skipped"}.get(result, "tests")] += result != "passed"
        per_browser.setdefault(browser, {}).setdefault(result, 0)
        per_browser[browser][result] += 1
passed = counts["tests"] - counts["failures"] - counts["errors"] - counts["skipped"]
lines = [f"# E2E results {out.name}", "", f"- Commit tested: `{sha}`", f"- pytest exit status: {status}",
         f"- Total: {counts['tests']}; passed {passed}, failed {counts['failures']}, errors {counts['errors']}, skipped {counts['skipped']}"]
lines += [f"- {browser}: " + ", ".join(f"{k} {v}" for k, v in sorted(r.items())) for browser, r in sorted(per_browser.items())]
lines += ["", "Files: `junit.xml`, `report.html`, `pytest.log`; screenshots, traces, console and server logs for failed tests under `failures/`."]
(out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
(out / "subject.txt").write_text(f"{passed} passed, {counts['failures'] + counts['errors']} failed", encoding="utf-8")
PY
cat "$OUT/summary.md"
RESULT="$(cat "$OUT/subject.txt")"
rm -f "$OUT/subject.txt"

# Keep only the latest results folder.
for old in e2e-results/*/
do
    [[ "${old%/}" == "$OUT" ]] || rm -rf "$old"
done

if (( ! PUSH ))
then
    echo "Results in $OUT (not committed)."
    exit "$STATUS"
fi

git add -A e2e-results
outside="$(git diff --cached --name-only | grep -v '^e2e-results/' || true)"
[[ -z "$outside" ]] || fail "refusing to commit files outside e2e-results/: $outside"
git diff --cached --quiet && fail "no result changes to commit"
git commit --quiet -F - <<MSG
E2E results $STAMP: $RESULT (chromium, firefox) [skip ci]

Playwright end-to-end suite run against $SHA.

Co-authored-by: Perplexity <noreply@perplexity.ai>
MSG
git push --quiet "$REMOTE" "HEAD:refs/heads/$BRANCH"
echo "Pushed $(git rev-parse HEAD) to $REMOTE/$BRANCH."
exit "$STATUS"
