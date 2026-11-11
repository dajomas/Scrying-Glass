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
