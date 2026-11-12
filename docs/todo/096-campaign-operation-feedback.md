# 096 - Stage 1 campaign-operation feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 Stage 1 Step 1 - 2026-11-12

Status: 1A/1B/1C implementations published; 1D.1 implementation archive prepared.
Base: 3f3621ab3fae5b82bfcfe5be5545ca0a46352f32. Publication, covering integrated validation and
bounded acceptance remain separate/pending; no new commit/push is claimed.
[Parent plan](097-feedback-delivery-plan.md) and
[current evidence/limits](../handover/520-campaign-operation-feedback.md).
Complete earlier criteria/history remain in the
[pre-1D.1 task record](https://github.com/dajomas/Scrying-Glass/blob/3f3621ab3fae5b82bfcfe5be5545ca0a46352f32/docs/todo/096-campaign-operation-feedback.md).

Agreed campaign operations and splits, without expanding scope:
- 1A Create: implementation delivered at 3c144a2279adf9446bf0f0c082df9aa3065961c4.
- 1B Edit: implementation published at 385ad5690f2783c1bb22767cba80b2bae5dff0db.
- 1C.1 Switch request: published at bb1581d4bd21608d79bbb0a246776c8246697901.
- 1C.2 Switch success/refresh: published at the base above. Preserve explicit
  three-second success, persistent refresh errors and transition/late-result guards.
- 1D.1 Delete validation/request: this archive. Migrate existing validation and
  request errors; preserve dialog/options/confirmations, encoded DELETE/query,
  authorization and successful follow-up. Guard sessions, newer options/revert,
  registry/scope/feedback identity and duplicates. No automatic replay.
- 1D.2 Delete success/refresh: remains unimplemented. Add explicit three-second
  success, completed deletion versus failed refresh, resulting transition and late-
  follow-up guards, matching recovery and busy/disabled-state restoration. Retain
  move/delete-setup options, dialog and existing server validation. Complete focused
  integration/regressions and relevant documentation; do not reinterpret refresh
  failure as a failed deletion or advise repeating DELETE.

Retain operation/target/scope identity, persistent actionable errors until dismissal
or matching resolution/replacement, unrelated/newer feedback and timer guards.
Preserve drafts/files/selections, endpoints, payloads, authorization and encounter
rules. No D2 near-field/connection/polling work or deferred test-suite audit.

Executed scoped checks: 12 delete Node, 14 creation Node, 18 font Node, 9 context
Node, 4 source/pin/assembly/tamper/syntax checks, 7 full-Admin Chromium cases
(4 delete, 3 creation), whole-bundle syntax and four detected negative controls.
All restored checks pass. Fixtures/intercepted HTTP are not full-suite/hosted CI,
live-server, human visual or exhaustive accessibility acceptance. See 520/logs.

Remaining: publish/review 1D.1, implement 1D.2, review covering integrated evidence
under the agreed sequence and obtain bounded acceptance; then continue the existing
wider Stage 1 plan. Intermediate 1D.1 message includes [skip ci]; final 1D.2 omits
it for normal push CI. No workflow edit/dispatch or new acceptance gate. Prior
accepted Stage 2, 4A.1-4A.13 and 009.1-009.6 stay closed. Stage 1, Stages 3-4,
D1 acceptance, D2 and 009.7/009 remain open. Cleanup remains deferred until 009.
