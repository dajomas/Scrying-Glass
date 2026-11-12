# 096 - Stage 1 campaign-operation feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 Stage 1 Step 1 - 2026-11-12

Status: 1A/1B/1C/1D.1 implementations published; 1D.2a archive prepared.
Base: 478d8dacd1de282ab2ad919af9459345ab507526. No new GitHub write or acceptance is claimed.
[Parent plan](097-feedback-delivery-plan.md) and
[current evidence/limits](../handover/520-campaign-operation-feedback.md).
Full previous criteria/history are preserved in the
[pre-1D.2a task record](https://github.com/dajomas/Scrying-Glass/blob/478d8dacd1de282ab2ad919af9459345ab507526/docs/todo/096-campaign-operation-feedback.md).

The remaining 1D.2 implementation is now two smaller deliveries, not added scope:
- 1D.2a: independent refresh ownership, own-result/modal-close context and obsolete
  success/error publication guards around the shared helper. Implemented here;
  publication/covering validation/acceptance pending. Normal legacy success/error
  wording and helper internals remain for the final part.
- 1D.2b: final remaining implementation. Migrate explicit three-second success and
  persistent applied-deletion/failed-refresh feedback with reload/no-replay guidance;
  propagate refresh failures; guard internal setup/refresh work and expected
  transitions/newer state; preserve matching resolution and busy restoration.
  Finish focused request/success/refresh integration/regressions and documentation.
  Do not describe a completed deletion as failed or advise repeating DELETE.

Preserve 1D.1 validation, campaign/dialog/revision/registry/scope identity,
confirmation, move/delete-setup options, payloads/queries, authorization and dialog.
Preserve drafts/selections/files, unrelated/newer feedback, obsolete-timer guards
and persistent actionable errors until dismissal or matching recovery/replacement.
No automatic mutation replay, new deletion rules, dialog redesign, D2 near-field/
connection/polling work or deferred test-suite cleanup.

Executed here: eight new Node component cases, four detected negative controls,
restored suite, 050 syntax and pin Python parse. Base bundle plus exact byte delta
sets the size pin. Existing request/browser, full assembly/pin/tamper and full-suite/
hosted CI checks are not rerun or claimed. Review final covering evidence under the
existing sequence; prior historical results do not cover this prepared revision.

Remaining: publish/review 1D.2a, implement final 1D.2b, review covering integrated
validation and obtain bounded acceptance, then continue the existing wider plan.
Every intermediate part includes [skip ci]; only the last 1D.2b omits it for normal
push CI. No workflow edit/dispatch or new acceptance gate. Prior accepted Stage 2,
4A.1-4A.13 and 009.1-009.6 stay closed. Stage 1, Stages 3-4, Deliverable 1 acceptance,
Deliverable 2 and 009.7/009 remain open; cleanup remains deferred until after 009.
