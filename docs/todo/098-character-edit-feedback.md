# 098 - Stage 2 character Edit feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 character Edit checkpoint - 2026-11-11

Status: in progress; implementation delivered as
fd13991c2c15cb6e15f056f0050431f5bc686ada. Composition-fixture correction prepared;
covering integrated validation and bounded acceptance remain pending. This is a
bounded part of the [approved feedback plan](097-feedback-delivery-plan.md), not
a new priority, owner, deadline or whole-stage acceptance.

Required behavior: preserve character JSON PATCH values and server gates; retain
drafts on failure; persistent matching save errors and three-second pane successes;
separate no-replay refresh errors; duplicate protection through refresh; stale
encounter/session isolation including same-character reopen; prior disabled-state
restoration and unchanged monster-Edit delegation. No automatic mutation replay.

Preparation passed 15 focused Node cases; three guard-removal negative controls
failed assertions, and the restored run passed. This uses production controller
and monster wrapper with mocked DOM/transport and a scoped adapter, not full Admin
or native browser acceptance. [Implementation/evidence/limits](../handover/480-character-edit-feedback.md).

Run 43063381965 attempt 1 covering 6c97f22, including this implementation, failed.
Its standalone audit completed 172 modules with one failed composition module;
all four scenarios stopped at the stale 42-versus-43 script assertion, with zero
unclosed connections reported for that module. Prepared correction retains an
exact 43-script guard and checks unique core/character/monster owner order.
Five extracted inventory methods passed; the four native browser scenarios and
full audit have not been rerun in preparation. [Correction evidence and limits](../handover/480-character-edit-feedback.md#composition-fixture-correction-preparation---2026-11-11).

Remaining acceptance: exact-content approval/delivery of the fixture correction;
retained full-page and browser composition regression; review equivalent covering
local or hosted results and correct failures; bounded acceptance with unperformed
live/manual/accessibility checks stated rather than invented. Either successful
equivalent local validation or hosted CI can satisfy automated validation for its
tested revision/scope; both are not required. Existing CI discovers the added .cjs
and revised Python fixture without workflow changes.

Creation/import and all other unfinished Stage 2 producers, Stage 1, both feedback
deliverables and 009.7 remain open. Accepted 4A.1-4A.13 scopes remain closed;
pane compatibility and accepted Join reporting/server behavior remain unchanged.

## Entry forms checkpoint - 2026-11-11

Status: in progress; complete-fragment integration for character creation, monster
creation and .monster import is prepared with twelve passing focused production-
controller tests. Exact approval/delivery, covering repository validation and
bounded acceptance remain pending. This is the next Stage 2 checkpoint, not a
reimplementation or acceptance of character Edit. Composition correction 7e49938
has verified successful run 43067755682 attempt 1; historical pending wording above
is superseded for that earlier covering run, not for this later core change.

Preserve JSON/FormData/dice/bonus/token and file/draft behavior, explicit independent
validation/request/update feedback, matching recovery, three-second pane success,
no replay and duplicate/stale guards. Complete-source integration updates only
060's digest and bundle length; all other pins/guards remain. [Preparation and
limits](../handover/480-character-edit-feedback.md#entry-forms-checkpoint-preparation---2026-11-11).

Remaining: CSV/setup-import migration; real native FormData/candidate/loaded-Admin
regression for the new paths; retained full-suite/reader/runner/tamper validation;
review equivalent covering local or hosted results and corrections; bounded
acceptance without invented manual/live/accessibility results. Existing CI
executes the added Node cases and retained browser suites; the new focused harness
is not native-browser acceptance. Remaining Stage 2 producers, Stage 1, both
deliverables and 009.7 stay open; pane compatibility and accepted Join stay intact.

## Lookup-focus fixture correction - 2026-11-11

Status: in progress; entry forms delivered as 37137b6367172549ffc7028b44af64e0e6534d75,
but covering run 43076164519 attempt 1 failed on the lookup-focus fixture's obsolete
source-order boundary. Its three setup errors recur inside the connection audit;
the audit completed with one failed module, not a demonstrated connection leak.
This supersedes earlier prepared/unpushed entry-form status, not pending acceptance.

Prepared correction uses the following bulk-action section boundary, retains blur
wiring and rejects accidental inclusion of form handlers. Five extracted synthetic
boundary tests passed and the three existing browser scenario bodies remain
AST-identical. [Evidence and limits](../handover/480-character-edit-feedback.md#lookup-focus-source-slicing-correction---2026-11-11).

Remaining gates: exact-content approval/delivery; all three native Chromium cases,
full unittest and standalone audit covering the revised revision; correction review
and bounded acceptance. No production/pin/workflow/audit changes are included.
CSV/setup import and other unfinished Stage 2 work remain open. Successful equivalent
local or hosted evidence may satisfy automated validation for its actual scope;
synthetic extraction checks alone do not establish native browser success.
