# 096 - Stage 1 campaign-operation feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 Stage 1 Step 1 - 2026-11-12

Status: 1A/1B/1C.1 implementations published; 1C.2 implementation archive prepared.
Base: bb1581d4bd21608d79bbb0a246776c8246697901. 1C publication/covering validation/bounded
acceptance remain pending, not inferred from preparation or earlier pushes.
[Parent plan](097-feedback-delivery-plan.md) and
[current evidence/limits](../handover/520-campaign-operation-feedback.md).

The complete prior criteria and checkpoint evidence remain in the
[pre-1C.2 task record](https://github.com/dajomas/Scrying-Glass/blob/bb1581d4bd21608d79bbb0a246776c8246697901/docs/todo/096-campaign-operation-feedback.md).
The four campaign operations and their agreed split do not expand scope:
- 1A Create: implementation delivered at 3c144a2279adf9446bf0f0c082df9aa3065961c4;
  covering validation and bounded acceptance remain separate.
- 1B Edit: implementation published at 385ad5690f2783c1bb22767cba80b2bae5dff0db;
  validation/acceptance remain separate. Retain campaign/session/draft safeguards.
- 1C.1 Switch validation/request: published at the base above; preserve selection
  validation, persistent request errors, confirmation, encoded endpoint and payload.
- 1C.2 Switch success/refresh: implemented in this archive; explicit three-second
  success, persistent refresh failure after applied activation, expected transition
  and stale-refresh guards, setup preservation and busy protection. Publication,
  covering validation and bounded acceptance pending.
- 1D Delete: not implemented here. Retain validation/request/success requirements,
  applied deletion versus refresh failure, confirmations, move/delete-setup options
  and existing dialog. This is the next campaign operation, not part of this archive.

Retain explicit operation/target/scope identities, matching resolution and unrelated/
newer feedback. Errors persist until dismissal/matching resolution or replacement.
Guard obsolete outcomes/timers, preserve drafts/files/selections, endpoints,
payloads, authorization and encounter rules. Never replay mutations automatically.
No D2 near-field/connection/polling work or deferred suite audit is included.

Executed scoped checks: 10 request Node, 10 refresh Node, 14 creation Node,
18 font Node, 9 context Node, 4 source/pin/tamper/syntax checks, and 10 distinct
complete-Admin Chromium scenarios (4 refresh, 3 request, 3 creation) pass. Four
negative controls detected; restored source passes. See handover/logs for fixture
changes, preparation corrections and limits. These are not full-suite/hosted CI,
live-server, human visual or accessibility acceptance.

Remaining: publish/review this archive, review covering integrated evidence under
the agreed validation sequence, obtain bounded 1C acceptance, implement 1D and
continue the existing wider Stage 1 plan. No new acceptance gate is added.
Intermediate 1A/1B/1C deliveries/corrections include [skip ci]; final 1D retains
normal push CI unless subsequently directed otherwise. No workflow edit/dispatch.
Prior accepted Stage 2, 4A.1-4A.13 and 009.1-009.6 stay closed. Stage 1, Stages 3-4,
D1 acceptance, D2 and 009.7/009 remain open. Test cleanup stays deferred until 009.
