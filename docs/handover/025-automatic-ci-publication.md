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
runs on features/perplexity, features/perplexity-018 and features/perplexity-009.7,
including failed and cancelled runs. tools/publish_ci_results.sh collects exact-attempt metadata,
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

## Allowlist synchronization - 2026-11-10

The user requested the main fix from d3b34f4aa00bb25c1c551321e88bb45947c2aeee
be applied to features/perplexity-009.7 to keep the publisher sources aligned.
The workflow, collector and new tests/test_ci_publication_branch_allowlists.py
match that commit's contents. Both exact branch allowlists now include
features/perplexity-009.7 while preserving the two existing branches and all
other collector/workflow behavior. This is a targeted file synchronization,
not a merge of main or a Git cherry-pick; application changes, newer handover
records and the existing Branch tests configuration are preserved.

The source fix's three local tests passed during its earlier preparation,
covering the workflow branch set, three allowed/four rejected Bash gate values
and full collector Bash syntax. They were not rerun for this synchronization.
Normal push-triggered CI is intended for this mixed commit, with no skip marker.
The new regression test is included by existing unittest discovery. No workflow
is separately dispatched, and no CI or live publication result is claimed.
The default-branch workflow and trusted collector were already corrected by
the referenced main commit; verify publication after a subsequent eligible
Branch tests completion. This update does not republish older evidence.

The historical SG-TODO-018 status above belongs to its original delivery; this
synchronization does not reopen or close any task. README, TODO and HANDOVER
indexes were reviewed/reused against verified live identities and need no edits.
The existing 020 CI history is retained rather than overwritten with main's
older version; this section carries the branch-specific publication update.
