# 465 - Statistics-open feedback

[Back to handover index](../../HANDOVER.md)

## 4A.13 statistics-open migration - 2026-11-11

This change set supplies the statistics-open migration only on
features/perplexity-009.7, baseline 13528784d0eadcc9fe00d77cdc21364676c76ed0.
Delivery identity, covering CI and acceptance are not invented. 4A.13 remains open.
[Inventory snapshot and remaining scope](460-global-feedback-reconciliation.md#checkpoint-ci-and-template-loaded-source-inventory---2026-11-11)
records the pre-migration source, including the then-existing alert candidate.

Only open() in static/statistics.js changes. Begin encounter-scoped statistics.open
with combatant-ID target before GET /api/state. Publish explicit persistent errors
instead of alert(); retain existing message wording. Successful draw/focus silently
resolves only that target's matching error. Module generation plus feedback scope/
attempt checks suppress superseded, closed and old-scope results and protect modal
opening. Successful open creates no success toast or mutation. Restore/base editor,
POST/token/confirmation, modal-local validation/request/refresh notices, controls,
state renderer, selection and focus-return logic outside open remain unchanged.
No automatic retry, server, shared fixture, core fragment, pin, marker or markup edit.

## Executed preparation and fixture integration

Original runtime blob 82cdc4337290953742820197091d002fbc8029c0 and restoration
test blob 136bbbbbf47392795efd238483853992d15c50f4 were verified. Complete runtime
outside open() compared byte-for-byte unchanged. Runtime draft is 8,891 UTF-8 bytes,
Git blob 99c5f57fe3aa0e5991a44c66c719860ce6cbc6a3, SHA-256
97280141b132e9bc21456e4f2a5ae4bcebf76ff1b2a578dde36b01979b445b0e.

Runtime/new-test syntax passed. New suite: 18 passed, zero failures/skips. Retained
restoration file passed with its original assertion body byte-for-byte unchanged.
Restored combined run: 19 TAP results, meaning 18 new cases plus the existing file,
not 19 unique requirements. Five negative controls detected wrong error severity,
omitted matching resolution, omitted generation guard, omitted scope guards and
restored alert; runtime was restored before the combined pass.

The legacy harness installs the existing real controller/Admin-bootstrap fixture,
validates campaign/setup scope, restores its DOM getter and adds a controllable
clock/realistic initially hidden modal. New tests reuse that harness prefix without
running its async original assertion body twice. Network and DOM remain mocked;
production controller/bootstrap/shared fixture input blobs were verified. No mounted
feedback view, full Admin/browser, authenticated live-server or human accessibility
acceptance is inferred. Preparation results are reused, not claimed as fresh tests
while assembling this write payload.

The isolated Chromium statistics-layout fixture also needs real feedback before
its first open. It now uses feedback_browser_fixture.install_feedback and valid
initial/same-scope campaign references. AST comparison preserved all 18 original
browser assertions, including responsive geometry, restore/cancel/no-heal, base
drafts and scope closure. Python AST/compilation passed; that browser fixture was
not executed locally. Do not treat compilation as its behavioral pass.

## Delivery and remaining gates

Normal configured CI already discovers both CJS files and the Python fixture;
no workflow change or dispatch. This mixed runtime/test/docs commit omits the
skip marker. Review covering results tied to the actual delivered SHA, including
new/legacy statistics, browser layout and full-source/loading regressions; obtain
fresh approval for corrections and explicit acceptance when supported. Earlier
checkpoint CI does not cover this runtime change.

Bundle-import success feedback remains unmigrated. Full-page/late-wrapper
composition, unintended legacy.global traffic and eventual global retirement are
still pending. Global and pane compatibility remain intact; later pane/Deliverable 2
work, both deliverables and 009.7 stay open. 4A.1-4A.12 remain closed. Root README/
TODO links and source/CI conventions were reviewed/reused and remain accurate;
HANDOVER index and task detail now link this bounded implementation. No archive/
Patch/, merge or deployment. [Task](../todo/097-feedback-delivery-plan.md#4a13-global-reconciliation---2026-11-11).
