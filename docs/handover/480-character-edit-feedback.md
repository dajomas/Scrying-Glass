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
