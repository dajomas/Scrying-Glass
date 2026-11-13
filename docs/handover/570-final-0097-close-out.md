# 570 - Final Deliverable 1, 009.7 and overall 009 close-out

[Back to handover index](../../HANDOVER.md)

[009.7 task/contract](../todo/097-feedback-delivery-plan.md) ·
[Parent 009 checklist](../todo/090-admin-usability-redesign.md) ·
[Deliverable 2 close-out](560-connection-field-feedback.md)

## Acceptance and outcome - 2026-11-12

Following the final-review explanation, the user requested "Proceed with final
acceptance and close out" at 22:58 CET on 2026-11-12. This records acceptance and
closure of whole Deliverable 1, SG-TODO-009.7 and parent SG-TODO-009 on the agreed
scope and stated evidence limits. Deliverable 2 and all previously accepted units/
stages remain closed. No agreed implementation, validation or acceptance action
remains inside 009.7/009; no further acceptance request is required for those scopes.
This record supersedes earlier whole-D1/final-pending notes in dated handovers,
without changing their original evidence, failed/cancelled-run history or limits.

## Final integrated baseline and identity

Tested application: 8da0657325818c69fc82dc1234995a5146e88ebc on
features/perplexity-009.7. Successful Branch tests 43310602854 attempt 1,
job 131505374358; publication dbb78d3057a2d38527bd612b948a6566a1a741e3,
directory ci-results-43310602854-attempt-1. Previously reviewed run.json/jobs.json
agree on tested SHA, branch, attempt and completed/success; all configured stages
succeeded. No new test run is claimed by this final reconciliation.

Git root comparisons between the tested SHA and current documentation base
2eb3b4d8a35b8a97761c1479f1ef68275652a01d show identical source/test/tool/workflow
identities, including:

| Tree | Matching Git identity |
|---|---|
| static | 86453d573bcf1bf0923606e02dbd64f2b953aea2 |
| templates | e73dad96b0af9cb941de38676d1c82986732eff6 |
| tests | 5b6531839da1966d53401182a0afed718ecadc8e |
| tools | 880158b42fb2b8e691137f16a3633846323d2b30 |
| python | b2b5c5279690798ae7ce58aa283ecf95f64bb31f |
| web_html | 377ba05f1c45bb5504f2b821ef5db5e4167914cf |
| .github | 8710dbedbf5d3e707ed4bd051dcd5f70f290d24b |
| deployment | a2e246dc56132fcb4278184e808e5c55075f8dc8 |

Root server, requirements, launchers and other non-documentation files also match.
Differences are documentation and CI evidence directories, not a new untested
application revision. Reusing the integrated run is justified; doc-only close-out
does not require an invented new run or separate workflow dispatch.

## Criterion-to-evidence reconciliation

The accepted numbered stage records retain detailed producer/operation/guard and
source identities. This final pass maps the agreed areas to the integrated run,
not to a new scope or a supposed exhaustive proof of all event combinations.

| Agreed area | Reconciled evidence |
|---|---|
| D1 persistent errors, 5s/3s successes, matching resolution and stale/timer isolation | Logged passes in test_admin_feedback_loading and test_admin_feedback_rendering include persistent lookup/Join errors, success deadlines, unrelated-error preservation, stale scope/timer suppression, keyboard dismissal and focus recovery. |
| Actual loaded owners, asset order, compatibility retirement and composition | Logged passes in test_admin_global_feedback_composition and test_admin_global_feedback_inventory cover late Join/bulk/Next wrappers, End/Reset/statistics/import coexistence, Stage 2 coexistence, exact inventory/order/version checks and no untyped core calls. Nine accessibility-composition cases pass, including rejection of untyped delivery in every region. Earlier accepted 440/450/470/530/540/550 records supply detailed migration history. |
| Responsive/keyboard/dialog/destructive-confirmation behavior | Logged accessibility-composition passes cover document language/main landmark, named dialogs, focus containment/return, nested Escape and named silent cancellations. Logged rendering/header/foundations cases cover narrow local overflow, keyboard controls, stable focus and draft preservation. Stage 4's local audit limits remain explicit, not hosted exhaustive accessibility certification. |
| 009.6 safeguards and original context | Logged independent-control cases preserve one-time collapse/manual reopening, independent panels and lair gating; loading/rendering cases preserve drafts; selected Battle Actions/Next cases preserve busy, stale-scope and no-replay behavior. Previously accepted 370 scope is not reopened. |
| D2 warning/recovery/deduplication and field/combatant association | All four test_admin_deliverable2_composition cases are logged ok: blocked Join association/dismissal, persistent deduplicated connection warning with unrelated-error-preserving recovery, raw-roll association and setup-name attributes. 560 retains the separate nine-case Node connection suite and field-contract design; configured JS stage succeeds. |
| Assembly, tests and delivery integrity | Existing runner workflow uses tools/run_split_tests.py for unittest/pytest/JS/standalone checks, preserving the tracked failure marker. Final source identity, eight-fragment limits, 44 scripts and 131,939-byte bundle are retained in 550/560. Runtime/test/workflow identities match the tested revision. |

## Direct log review and limits

Workflow configuration at the tested SHA was read. JavaScript and standalone loops
aggregate failures into their exit status; their successful stage outcomes are not
merely successful artifact uploads. Chromium launch/render preflight passed.
Main unittest summary is "Ran 1583 tests" / "OK"; pytest reports "43 passed".
These are suite counts, not independent requirement counts or a claim of unique
nonoverlapping tests. No aggregate Node count is invented.

Selected source-log chunks under reader-chunks/file-000038 were directly reviewed:
parts 000012, 000014-000018, 000025, 000030, 000100, 000110, 000119-000121,
000180 and 000277. Parts 000014/000015 contain all nine accessibility-composition
and all four D2 composition passes; 000016-000018 contain feedback/inventory/header
passes; 000119/000121 contain the Python/pytest summaries. Other sampled parts
retain combat/permission/state regression context. This was not a full review of
all 277 chunks, every test or screenshots. CI action-runtime deprecation warnings
in the tail are tooling warnings, not failed test conclusions; no workflow repair
was added to the finish line.

No new authenticated live-server/provider, human visual/manual, screen-reader or
exhaustive accessibility execution is claimed. Browser fixtures intercept HTTP;
local ad hoc axe evidence is not a new final CI audit. D2 remains Admin-only;
Client Display reconnect, guessed general HTTP-detail field association and single-
field bulk mapping remain outside its accepted scope. Bounded final user acceptance
resolves the agreed scope on these explicit limits, not falsely executed checks.
No blocker against the agreed scope was identified in this bounded reconciliation.

## Documentation, history and independent work

README, TODO/HANDOVER indexes, 090 and 097 are reconciled with this final record.
Earlier detailed scope/evidence remains in numbered handovers and the
[pre-final task record](https://github.com/dajomas/Scrying-Glass/blob/2eb3b4d8a35b8a97761c1479f1ef68275652a01d/docs/todo/097-feedback-delivery-plan.md).
Existing task headings/anchors remain addressable. The dated sequence/rationale
115 was reviewed and left unchanged; current indexes record its completed steps.

Deferred test-suite cleanup, proposed 016/017 and SG-TODO-019 stay separate, not
prerequisites or automatically started work. No owner/deadline/order change,
merge, deployment, release operation or blanket future external-write approval.

This close-out is documentation only and uses [skip ci]. No application/tests/
assets/templates/pins/dependencies/workflows change; no fresh tests or separate
dispatch. No final close-out commit SHA is invented before the approved write.
