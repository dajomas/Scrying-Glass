# 340 - Combined monster lookup activation

[Back to handover index](../../HANDOVER.md)

2026-11-08. [SG-TODO-018 correction A.2](../todo/185-monster-correction-plan.md).
Branch features/perplexity-018. Commit 3 backend included; covering CI, commit 4
and A.2 workflow acceptance pending. A.1 remains accepted; no overall close-out/merge.

## Runtime and compatibility

lookup_candidates now calls the prepared combiner with both provider enable flags.
D&D Beyond success no longer suppresses 5e.tools. Configured books are enumerated;
missing index mappings, malformed datasets/entries, fetch failures and limits block
the combined result. Unconfigured entry sources are not offered. Both enabled
callbacks are attempted, but failed/incomplete lookup returns no candidates and
never reaches token/bonus signing. Successful candidates retain separate statistics
and source-bound selection/bonus offers. No account access or entitlement changes.

Configuration names/defaults remain. fivetools_fallback independently enables
5e.tools for candidate searches; legacy stats/image fallback paths are unchanged.
Existing creation/Refresh callers consume the same ok/error contract. Retained
Refresh identities still resolve exactly; no automatic sole-candidate Refresh
selection, checkbox changes, Apply bypass, schema or permissions change is included.

README documents runtime behavior. Old in-UI source help/config-example comments
remain a disclosed interim limitation for commit 4, together with associated
browser/application checks. No frontend source or workflow changes in this commit.

## Validation and history

Commit 2 run 42501718072 attempt 1 succeeded for exact
22e0f08f27bf0a340fbfb0f269d330513ca7569a; publication
d4757545a857f57b541659e860e52272b5d1fafc / ci-results-42501718072-attempt-1.
All listed job and cleanup steps succeeded. It does not test this activation.

Original selection/candidate/marketplace blobs were verified before preparation.
Changed modules parse/compile. Thirty-six extracted-lookup cases passed with the
actual combiner but mocked providers/signers. Migrated CI regressions cover both
providers/counts, exact signed identities, no signing on incomplete search, missing
configured books, unconfigured entries and marketplace redirects. The constructor,
manual selection and signed-image tests are retained. These real-module regressions
were prepared, not executed locally: FastAPI was absent. Existing normal CI runs
them; new covering results and live/manual acceptance remain pending.

The 185 task section is consolidated to current requirements/status with all six
unfinished/accepted actions retained. Closed delivery detail remains in 335 and
its linked immutable pre-activation snapshot. Root TODO's overall SG-TODO-018
in-progress status and stable links are unchanged. No task completion is inferred
from code preparation or push. Commit 4, A.3, stage B and merge remain pending.
