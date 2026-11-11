# 098 - Stage 2 character Edit feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 character Edit checkpoint - 2026-11-11

Status: in progress; implementation/test preparation complete, GitHub delivery,
covering integrated validation and bounded acceptance pending. This is a bounded
part of the [approved feedback plan](097-feedback-delivery-plan.md), not a new
priority, owner, deadline or whole-stage acceptance.

Required behavior: preserve character JSON PATCH values and server gates; retain
drafts on failure; persistent matching save errors and three-second pane successes;
separate no-replay refresh errors; duplicate protection through refresh; stale
encounter/session isolation including same-character reopen; prior disabled-state
restoration and unchanged monster-Edit delegation. No automatic mutation replay.

Preparation passed 15 focused Node cases; three guard-removal negative controls
failed assertions, and the restored run passed. This uses production controller
and monster wrapper with mocked DOM/transport and a scoped adapter, not full Admin
or native browser acceptance. [Implementation/evidence/limits](../handover/480-character-edit-feedback.md).

Remaining acceptance: exact-content GitHub approval/delivery; retained full-page
and browser composition regression; review equivalent covering local or hosted
results and correct failures; bounded acceptance with unperformed live/manual/
accessibility checks stated rather than invented. Either successful equivalent
local validation or hosted CI can satisfy automated validation for its tested
revision/scope; both are not required. Existing CI discovers the added .cjs.

Creation/import and all other unfinished Stage 2 producers, Stage 1, both feedback
deliverables and 009.7 remain open. Accepted 4A.1-4A.13 scopes remain closed;
pane compatibility and accepted Join reporting/server behavior remain unchanged.
