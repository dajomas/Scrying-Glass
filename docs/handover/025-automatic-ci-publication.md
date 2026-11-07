# 025 - Automatic CI evidence publication

[Back to handover index](../../HANDOVER.md)

## Branch delivery correction - 2026-11-07

Publisher source is delivered to features/perplexity-018 as requested, without
merging other main changes or replacing this branch's newer handover entries.
The initial default-branch deployment remains at main commit
6f68a646b7314201b8a629f1707719529e1b507e; this correction does not revert it.
The completion trigger requires the workflow on the default branch. The running
publisher deliberately checks out trusted collector code from main, so future
collector edits on this working branch require separate approved deployment to
main before taking operational effect.

## Operation

.github/workflows/publish-ci-results.yml listens for completed Branch tests push
runs on features/perplexity and features/perplexity-018, including failed and
cancelled runs. tools/publish_ci_results.sh collects exact-attempt metadata,
jobs and logs, plus run-scoped artifacts, and builds/verifies lossless reading
copies with tools/chunk_ci_evidence.py. Artifacts are not guaranteed to belong
to the selected attempt; inspect provenance and collection warnings.

Evidence is committed to the tested branch in ci-results-RUN_ID-attempt-ATTEMPT.
Older tracked root evidence directories are replaced, remaining in Git history.
Newer published runs/later attempts are preserved. Publication is serialized per
branch and retries non-force pushes against the latest remote contents.
Only selected evidence paths are staged. Downloaded evidence is never executed.
The runtime-provided GITHUB_TOKEN has actions: read and contents: write; no token
value is committed. Evidence commits contain [skip ci]. The workflow summary
records tested and publication SHAs. Failed publication uploads collected
evidence as a fallback artifact; branch protections may prevent publication.

Automatic publication has no manual sensitive-data review. Keep secrets and
sensitive data out of test output and artifacts. getworkflow.sh remains unchanged
as a manual fallback. Application code and tests.yml are unchanged.

## Validation pending

No local or live publisher execution has been verified. This non-documentation
commit omits [skip ci], allowing normal configured branch tests. No separate
workflow is dispatched. Verify a completed run publishes evidence to this branch,
check the tested SHA/attempt and reading copies, and exercise failed-test, rerun
and concurrent-publication behavior before marking the publisher validated.
README and TODO index were reviewed; application descriptions and task statuses
are unaffected and are left unchanged. SG-TODO-018 remains in progress.
