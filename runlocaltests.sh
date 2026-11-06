#!/usr/bin/env bash
# Test committed Scrying Glass sources in a disposable checkout.
set -Eeuo pipefail
usage() {
cat <<'HELP'
Usage: bash runlocaltests.sh [--suite all|syntax|python|pytest|javascript|standalone|browser]
                            [--python PATH] [--no-publish]
Default: all five CI groups, then publish completed evidence to features/perplexity.
browser is an alias for standalone; unittest also includes browser fixtures.
--no-publish never stages, commits or pushes results.
Tests committed HEAD, not uncommitted files. Does not install dependencies.
Needs Git, Bash, Python dependencies, pytest, Node and Playwright Chromium.
SG_LOCAL_TEST_TMPDIR overrides the scratch parent (default /tmp).
Evidence: local-tests-<short-hash>/run-<UTC>-<unique>/
The suite status records command exits, not a guarantee of zero skipped tests.
No Looking Glass live/recovery suite or workspace helper is used.
HELP
}
suite=all
python_arg=''
publish=1
completed=0
WORK=''
while (($#)); do
    case "$1" in
        --help|-h) usage; exit 0 ;;
        --no-publish) publish=0; shift ;;
        --suite|--python)
            (($# >= 2)) || { usage >&2; exit 2; }
            if [[ "$1" == --suite ]]; then suite=$2; else python_arg=$2; fi
            shift 2 ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done
case "$suite" in
    all|syntax|python|pytest|javascript|standalone) ;;
    browser) suite=standalone ;;
    *) usage >&2; exit 2 ;;
esac
ROOT=$(git -C "$(dirname -- "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)
HASH=$(git -C "$ROOT" rev-parse --verify 'HEAD^{commit}')
SHORT_HASH=$(git -C "$ROOT" rev-parse --short=7 "$HASH")
if [[ -n "$python_arg" ]]; then
    PY=$(command -v -- "$python_arg")
elif [[ -n "${VIRTUAL_ENV:-}" && -x "$VIRTUAL_ENV/bin/python" ]]; then
    PY=$VIRTUAL_ENV/bin/python
elif [[ -x "$ROOT/.venv-test/bin/python" ]]; then
    PY=$ROOT/.venv-test/bin/python
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
    PY=$ROOT/.venv/bin/python
else
    PY=$(command -v python3.14 || command -v python3)
fi
[[ "$PY" == /* ]] || PY="$(cd -- "$(dirname -- "$PY")" && pwd)/$(basename -- "$PY")"
[[ -x "$PY" ]] || { echo 'Python executable not found' >&2; exit 2; }
OUT=$ROOT/local-tests-$SHORT_HASH
mkdir -p -- "$OUT"
RUN=$(mktemp -d "$OUT/run-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf 'Evidence directory: %s\n' "$RUN"
mkdir -p -- "$RUN/suites"
printf 'suite\tcommand\texit_code\tlog\n' > "$RUN/summary.tsv"
publish_results() {
    local relative=${RUN#"$ROOT/"} branch head
    branch=$(git -C "$ROOT" symbolic-ref --quiet --short HEAD) || return 1
    [[ "$branch" == features/perplexity ]] || {
        echo 'Refusing publication outside features/perplexity'; return 1;
    }
    head=$(git -C "$ROOT" rev-parse --verify HEAD) || return 1
    [[ "$head" == "$HASH" ]] || { echo 'HEAD changed; refusing publication'; return 1; }
    git -C "$ROOT" diff --cached --quiet || {
        echo 'Index has staged changes; refusing publication'; return 1;
    }
    git -C "$ROOT" add -f -- "$relative" || return 1
    git -C "$ROOT" commit --only \
        -m "Local test results for commit hash $HASH [skip ci]" -- "$relative" || return 1
    git -C "$ROOT" push origin HEAD:refs/heads/features/perplexity || return 1
}
finish() {
    local rc=$? publication_log
    trap - EXIT INT TERM
    cd -- "$ROOT" || exit 1
    printf 'finished_utc=%s\ncompleted=%s\n' "$(date -u +%FT%TZ)" "$completed" >> "$RUN/environment.txt"
    printf '%s\n' "$rc" > "$RUN/exit-code.txt"
    if [[ -n "$WORK" && -d "$WORK" ]]; then
        if ((completed)); then
            if ! rm -rf -- "$WORK"; then
                printf 'Scratch cleanup failed: %s\n' "$WORK" >> "$RUN/cleanup.log"
                rc=1
                printf '%s\n' "$rc" > "$RUN/exit-code.txt"
            fi
        else
            printf 'Interrupted/incomplete scratch retained: %s\n' "$WORK" >&2
        fi
    fi
    if ((publish && completed)); then
        publication_log=$OUT/publication-$(basename -- "$RUN").log
        if publish_results > "$publication_log" 2>&1; then
            printf 'publication_exit=0\n' >> "$publication_log"
            # printf 'Published results at commit %s\n' "$(git -C "$ROOT" rev-parse HEAD)"
            printf 'Published completed local evidence for %s in %s at commit %s\n' \
              "$HASH" "${RUN#"$ROOT/"}" "$(git -C "$ROOT" rev-parse HEAD)"
            if ! rm -f -- "$publication_log"; then
                printf 'Results pushed, but publication-log cleanup failed: %s\n' "$publication_log" >&2
                rc=1
            fi
        else
            rc=1
            printf 'publication_exit=1\n' >> "$publication_log"
            printf 'Publication failed; inspect %s. Evidence retained.\n' "$publication_log" >&2
        fi
    elif ((publish)); then
        echo 'Setup/interruption prevented completion; evidence was not published.' >&2
    fi
    exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
{
    printf 'commit=%s\nshort_commit=%s\nsuite=%s\npython=%s\nstarted_utc=%s\n' \
        "$HASH" "$SHORT_HASH" "$suite" "$PY" "$(date -u +%FT%TZ)"
    printf 'source=detached local clone; uncommitted changes are not tested\n'
    printf 'coverage=CI commands; browser fixtures are not live-server validation\n'
    git -C "$ROOT" status --short
    uname -a
    "$PY" --version
    if command -v node >/dev/null; then node --version; fi
} > "$RUN/environment.txt" 2>&1
WORK=$(mktemp -d "${SG_LOCAL_TEST_TMPDIR:-/tmp}/scrying-local-tests-XXXXXX")
{
    git clone --quiet --no-hardlinks --no-checkout -- "$ROOT" "$WORK/repo"
    # Exclude accumulated evidence, not application or test sources.
    git -C "$WORK/repo" sparse-checkout set --no-cone -- '/*' '!/local-tests-*/' '!/ci-results-*/'
    git -C "$WORK/repo" checkout --quiet --detach "$HASH"
    [[ "$(git -C "$WORK/repo" rev-parse HEAD)" == "$HASH" ]]
} > "$RUN/workspace-prepare.log" 2>&1
cd -- "$WORK/repo"
[[ -f tools/run_split_tests.py && -d tests ]] || {
    echo 'Committed HEAD lacks Scrying Glass test sources' >&2; exit 2;
}
mkdir -p -- "$WORK/tmp"
export TMPDIR="$WORK/tmp"
export PYTHONPATH="$WORK/repo:$WORK/repo/tests"
export PYTHONUNBUFFERED=1
unset PYTHONHOME
run_command() {
    local group=$1 label=$2 logfile rc
    shift 2
    logfile=$RUN/suites/$group/$label.log
    mkdir -p -- "$(dirname -- "$logfile")"
    local -a codes
    printf '\n=== %s / %s ===\n' "$group" "$label"
    printf '%q ' "$@" > "$logfile.command"
    printf '\n' >> "$logfile.command"
    set +e
    "$@" 2>&1 | tee "$logfile"
    codes=("${PIPESTATUS[@]}")
    set -e
    rc=${codes[0]}
    if ((codes[1] != 0)); then rc=${codes[1]}; fi
    printf '%s\t%s\t%s\t%s\n' "$group" "$label" "$rc" "${logfile#"$RUN/"}" >> "$RUN/summary.tsv"
    printf '%s\n' "$rc" > "$logfile.exit-code"
    return "$rc"
}
run_group() {
    local group=$1 failed=0 test n=0
    local -a args=() files=()
    case "$group" in
        syntax)
            run_command syntax compileall "$PY" -m compileall -q \
                scrying_glass_server.py python web_html tests tools || failed=1
            run_command syntax server-import "$PY" -c 'import scrying_glass_server' || failed=1 ;;
        python)
            run_command python unittest "$PY" tools/run_split_tests.py -- "$PY" \
                -m unittest discover -s tests -p 'test_*.py' -v || failed=1 ;;
        pytest)
            mkdir -p -- "$RUN/suites/pytest"
            run_command pytest regressions "$PY" tools/run_split_tests.py -- "$PY" -m pytest -q \
                tests/test_death_save_validation_2ba6607.py \
                tests/test_slug_truncation_82860c4.py \
                --junitxml="$RUN/suites/pytest/results.xml" || failed=1 ;;
        javascript|standalone)
            # Python emits a sorted NUL-delimited inventory, avoiding filename splitting.
            "$PY" - "$group" > "$RUN/$group-inventory.nul" <<'PY'
from pathlib import Path
import sys
paths = sorted(p for p in Path('tests').rglob('*') if p.is_file() and (
    p.suffix in ('.js', '.cjs') if sys.argv[1] == 'javascript'
    else p.suffix == '.py' and not p.name.startswith('test_') and p.name != '__init__.py'))
for path in paths:
    sys.stdout.buffer.write(str(path).encode() + b'\0')
PY
            while IFS= read -r -d '' test; do files+=("$test"); done < "$RUN/$group-inventory.nul"
            if ((${#files[@]} == 0)); then
                run_command "$group" discovery "$PY" -c 'raise SystemExit("No test scripts discovered")' || failed=1
            fi
            for test in "${files[@]}"; do
                n=$((n + 1))
                printf '%s\t%s\n' "$n" "$test" >> "$RUN/$group-inventory.tsv"
                if [[ "$group" == javascript ]]; then
                    run_command "$group" "script-$n" "$PY" tools/run_split_tests.py -- node --test "$test" || failed=1
                else
                    args=()
                    [[ "$test" != tests/audit_log_clear.py ]] || args=(patched)
                    run_command "$group" "script-$n" "$PY" tools/run_split_tests.py -- "$PY" "$test" "${args[@]}" || failed=1
                fi
            done ;;
    esac
    return "$failed"
}
status=0
if [[ "$suite" == all ]]; then
    suites=(syntax python pytest javascript standalone)
else
    suites=("$suite")
fi
for group in "${suites[@]}"; do
    run_group "$group" || status=1
done
completed=1
printf '\nResults: %s\n' "$RUN"
cat "$RUN/summary.tsv"
exit "$status"
