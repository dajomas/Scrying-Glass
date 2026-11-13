# 480 - Stage 2 character Edit feedback

[Back to handover index](../../HANDOVER.md)

## Implementation preparation - 2026-11-11

Scope: character Edit only, under [SG-TODO-009.7](../todo/097-feedback-delivery-plan.md).
The [bounded task record](../todo/098-character-edit-feedback.md) tracks remaining gates.
This is not completion of Stage 2, Stage 1, either deliverable or phase 009.7.
4A.1-4A.13 retain their accepted closed scopes. No merge or deployment.

The new character-edit-feedback.js asset installs after core Admin and before
monster-initiative-edit.js. The unchanged monster wrapper captures it and delegates
character submissions to it; monster submissions retain their existing owner.
Core fragments, identity/size pins, tracked admin.js marker, accepted Join runtime,
other asset versions and workflows remain unchanged. Reload browsers for the new
asset; deploy the complete static tree with the matching template.

Character saves retain the JSON PATCH endpoint, encoded ID, trimmed name, color,
numberValue HP conversions and blank/null versus explicit zero/negative initiative.
Native validity remains; server validation and combat/authorization rules do not
change. Explicit character.edit and character.edit.refresh identities preserve
unrelated notices. Request errors persist and preserve the draft; matching save
success replaces its error and expires after three seconds. Success precedes
refresh. Refresh failure has separate persistent no-replay guidance, not a failed
save or automatic retry. Controls retain prior disabled states; Cancel stays usable.

Pending guards cover mutation plus refresh per target in the current encounter.
Editing-object identity distinguishes even same-character reopen sessions. Stale
session/scope completions cannot close a newer dialog, publish save results or
start a refresh. A refresh failure after a newer Edit opens is suppressed. Cleanup
restores captured controls only, not replacement DOM controls. Scope invalidation
and closing dialogs do not revoke already-sent server mutations.

## Preparation evidence and limits

Node syntax passed. The exact proposed asset and test file passed 15 focused Node
cases with the production controller, mocked DOM/transport, deterministic timers
and a scoped feedback adapter. Two cases execute the unchanged production monster
wrapper for actual character delegation and retained monster FormData request
ownership; the fake FormData is not native browser serialization. Asset wiring
checks the document-end order and single versioned include.

Three negative controls remove session identity, encounter validity and duplicate
protection separately. Each caused an assertion failure; the restored suite passed
15/15 with zero failures, cancellations or skips. The original scope test also
changed session and missed a removed scope guard; an independent scope-only case
was added before the final passing/negative-control runs. Earlier runs are not
additional unique case counts. Source reconstruction matched production controller
blob c4a82d73b21f4657da651ce45f76003c3348a6ef, unchanged monster wrapper blob
2fffc7beb27053dc348d93c5f28b4c48d8e9b426 and template base blob
6cf25b5dfbd0132a0e5bb9502a1a7fe5742ec242.

These are not complete Admin/bootstrap/view, native browser, authenticated-server,
human visual, screen-reader or exhaustive accessibility acceptance. Full loaded
composition and retained browser suites remain required; they were not executed
in this preparation environment. Existing CI discovers the new .cjs without a
workflow change. Normal push-triggered CI applies; no [skip ci] or separate dispatch.
No new commit identity, CI result or completed acceptance is claimed.

Successful equivalent local tests, hosted CI or both count as automated-validation
evidence for the identified revision and required scope actually covered. Both are
not required; this focused run does not establish full-suite success. The previously
accepted shared-roster local evidence is not validation of this subsequent change.
README and plan 097 were reviewed against verified unchanged identities and retain
accurate wider boundaries. HANDOVER and TODO indexes link this checkpoint.

## Remaining Stage 2 work

Creation/import forms; effective monster initiative/Edit/raw-roll and roll-all;
select-dead; bulk Join pane success without changing accepted global reporting;
complete fixture/asset reconciliation, combined loaded-Admin/browser regression,
covering local-or-hosted validation/corrections and bounded acceptance remain open.
Pane compatibility stays until required migrations finish. Stage 1, Stages 3-4,
Deliverable 2 and wider phase acceptance remain separate. This checkpoint does not
claim live/manual/accessibility checks that have not run.

## Composition fixture correction preparation - 2026-11-11

Character Edit was delivered as fd13991c2c15cb6e15f056f0050431f5bc686ada.
Run 43063381965 attempt 1, job 130671689532, covers Chromium repair
6c97f22ae661156f6f2e5620b7b8d3ba0ff1c136 including that implementation.
Standalone audit completed 172 modules with one failed module:
test_admin_global_feedback_composition.py. Its four scenarios all stopped at
open_page's obsolete 42-script expectation: the loaded page has 43 after the
character-Edit asset addition. That module reported four opened SQLite connections
and zero without explicit close. The standalone real-Chromium smoke completed its
reported checks with no page errors. This is not an overall successful CI run.

The correction preserves an exact count of 43 and additionally requires exactly
one core Admin, character-edit-feedback.js?v=1 and monster-initiative-edit.js?v=1
asset, in that order. It does not derive the expected count from unchecked live
HTML or relax it to a lower bound. All four scenario bodies are AST-identical to
the live base; existing boot-error, missing-asset, no-mutation and cleanup checks
remain. No production asset/template, fragment pin, workflow or audit changes.

Five new inventory unittest methods passed in isolation, extracted from the
complete proposed source via AST to avoid unavailable full-fixture imports.
They reject wrong totals, missing/duplicate required assets at the same total,
wrong owner order and wrong character asset version. Removing count, singleton or
order guards separately made the regression suite fail; the singleton negative
control also exposed missing-index errors. Restored checks passed 5/5. Full-module
AST parsing passed, and the original source reconstruction matched Git blob
c5f141467fa4779c2a789805d9b5e0234a4405d9. This is guard-level validation, not
execution of the four native browser scenarios or the full repository audit.

Normal push-triggered CI applies without a skip marker. The existing workflow
runs this module through unittest and the connection audit; the revised module
contains four retained browser scenarios plus five inventory unit methods.
Covering results and any further corrections remain pending, as does bounded
acceptance. README, HANDOVER and TODO indexes were reviewed/reused against live
identities and remain unchanged; their links and open scopes remain accurate.
Both deliverables, Stage 2 and 009.7 stay open. No new passing CI or commit identity
is invented before delivery/verification. No merge or deployment.

## Entry forms checkpoint preparation - 2026-11-11

This next bounded Stage 2 checkpoint migrates character creation, monster creation
and .monster import, not CSV/setup import or the whole stage. Prior composition
correction 7e49938c8064b7c70526583a2d4bfac358150cce has verified successful covering
run 43067755682 attempt 1; that evidence does not validate this later core change.

The complete 060 fragment replaces the three existing handlers, without an extra
asset or script-count change. Explicit per-form validation, request and refresh
identities retain independent errors. Payload capture precedes disabled controls;
character JSON values, monster FormData/dice strings/bonus fields and the native
formdata token hook remain. Drafts/files survive request failures. Success precedes
reset/refresh and expires after three seconds; update failure has a separate
persistent no-replay error. Per-form busy guards last through refresh, and obsolete
encounter completions cannot reset the form or initiate refresh. Already-sent
mutations are not cancelled or replayed. The species listener, applyBackground and
bulk/battle-action source outside the replaced handler blocks remain unchanged.

060 is 13,674 UTF-8 bytes, SHA-256
fc9fb3d3cc8dbf1e3524848cea75924bf1e3c2e532e622cb6bc82ba74388ec2b.
Only its digest and the calculated bundle size, 119,233 bytes, change in the pin
fixture. Other fragment identities/order, UTF-8/20,000-byte/tamper guards and the
tracked admin.js failure marker are retained. No workflow/template/cache-version,
candidate asset, accepted Join owner or server-rule changes.

Twelve focused cases passed executing complete 060 with the exact production
controller (blob c4a82d73b21f4657da651ce45f76003c3348a6ef), deterministic timers,
mock DOM/transport/FormData and a scoped adapter. Three removed-guard controls
(duplicate, stale and matching validation) caused assertion failures; restored
suite passed 12/12. Complete-fragment Node syntax and pin-file compilation passed.
Original 060 reconstruction matched blob 5ce48f8d0e82a0ce3eaa35b06037ea0c1a03c029.
The earlier ten-case draft/mock-controller run is superseded for this payload,
not an additional current case count. Native HP parsing is stubbed in these tests;
real FormData events, candidate capture blocking, bootstrap/view and full Admin,
reader/runner/tamper/browser/server/manual/accessibility checks were not executed.
Existing CI discovers the new .cjs and retains the existing browser regressions;
new-path native-browser acceptance and any fixture reconciliation remain open.

Normal CI applies without a skip marker. Covering validation/corrections and
bounded acceptance remain pending; equivalent successful local or hosted results
count for their tested revision/scope, not future changes. README, root indexes
and plan 097 were reviewed against known live identities and need no unrelated
edits. CSV/setup import, remaining monster initiative/Edit/roll-all, select-dead,
bulk Join pane success, final Stage 2 reconciliation and wider deliverables remain
open. No merge/deployment or new CI/commit identity is invented.

## Lookup-focus source slicing correction - 2026-11-11

Entry forms were delivered as 37137b6367172549ffc7028b44af64e0e6534d75.
Covering run 43076164519 attempt 1, job 130716410552, failed: the main suite ran
1,525 tests with three errors, all in LookupFocusRegressionTests.setUp. The audit
completed 172 modules with one failed module, test_monster_lookup_focus_browser.py,
reporting zero connections opened and zero unclosed for that module. Each error
was ValueError at the old upload-handler boundary searched after the species
listener. The upload handler now precedes that listener. No lookup/focus assertion
was reached; this is not a demonstrated connection leak or Chromium launch failure.

The fixture now slices from the existing species-listener registration to the
following character bulk-action registration, not to another form's submit handler.
This retains any additional blur wiring within that listener section. Unexpected
form-submit code inside the slice fails explicitly instead of executing an
unrelated handler in the minimal fixture. Missing/reversed boundaries still fail.
The three browser test bodies are AST-identical, retaining all focus, request-count,
popup, source-token and value checks; cleanup and timeouts remain unchanged.

Five added synthetic source-boundary methods passed via AST extraction from the
complete proposed test source. They reproduce the old boundary failure with upload
before species, retain blur wiring, exclude following bulk/other handlers and
reject missing boundaries or an unrelated submit handler inside the slice. A
copied current 593-byte production listener section extracts unchanged and passes
Node syntax checking. Original test reconstruction matched Git blob
cc801748e0d6ecc000025b863e67f9beea680843; complete Python AST parsing passed.
These are extraction/syntax checks, not native execution of the three Chromium
cases, actual full-bundle assembly or full repository/audit validation.

Production sources, candidate asset, fragment identities, templates, workflow and
audit remain unchanged. Existing unittest discovery and the standalone audit will
execute the revised module (three browser cases plus five boundary methods).
Normal CI applies without a skip marker or separate dispatch. Covering results,
any further corrections and bounded acceptance remain pending. README and indexes
were reviewed/reused against live identities and left unchanged. Stage 2, both
deliverables and 009.7 remain open. No merge/deployment or invented passing result.
