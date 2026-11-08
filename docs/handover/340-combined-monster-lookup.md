# 340 - Combined monster lookup activation

[Back to handover index](../../HANDOVER.md)

2026-11-08. [SG-TODO-018 correction A.2](../todo/185-monster-correction-plan.md).
Branch features/perplexity-018. Backend delivered; first commit-3 CI failed.
Locked-page fixture correction included with covering CI, commit 4 and A.2 acceptance pending. A.1 remains accepted; no overall close-out/merge.

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

## Failed activation CI and locked-page correction - 2026-11-08

Verified run 42503436253 attempt 1 tested exact
5414f1359808fdc07c75b94b1ca3ffe15c078d70. Publication:
a06ac1fad20816ff3403506eca070cc1b101cc83 / ci-results-42503436253-attempt-1.
Both main and repeated runs report 1,391 tests with two failures, not four defects.
The stale locked-page fixture expected one candidate (actual two) and no 5e.tools
calls (actual two across the two failure cases). Syntax/server import, pytest,
JavaScript and artifact upload succeeded. Standalone step failed; connection
tracking 742 opened/0 without explicit close does not make it pass. Python/Node
post-setup cleanup was skipped. The original failed run remains failed history.
Log file-000026 parts 109 and 148 contain main/repeated failure summaries.

The correction migrates the remaining fallback-only assertions, retains exact
provider order/stat checks and adds observable no-signing guards plus a secondary-
failure regression. LockedPageTests (all six access-gate methods) is AST-identical;
no production/security classifier is modified. The original test blob was verified.

An isolated reconstructed package reproduced 9 original methods with two failures,
then passed all 10 corrected methods. Six unchanged pure dependency blobs were
verified; the local selection source contains the same four production AST nodes
that this fixture extracts, not the full FastAPI module. HTTP is mocked and signing
is a fixture Mock; no server/package initialization, actual signing/ASGI/browser/
live-provider or full-suite proof is claimed. Corrected syntax checks passed.
Covering CI and A.2 acceptance are pending. README/root indexes/workflows remain
unchanged: runtime behavior, overall status and links are unaffected. This is a
commit-3 corrective increment, not commit 4 or an authorization to merge/close.
