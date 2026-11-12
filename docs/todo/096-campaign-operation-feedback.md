# 096 - Stage 1 campaign-operation feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 Stage 1 Step 1 - 2026-11-12

Status: in progress. The agreed split replaces combined Step 1 without expanding
scope: 1A Create, 1B Edit, 1C Switch, 1D Delete. Only 1A is being implemented.
[Parent plan](097-feedback-delivery-plan.md) and
[evidence/limits](../handover/520-campaign-operation-feedback.md).

The user approved two commits within 1A:
1. Read-only encounter context, bootstrap version, focused tests and records.
   This foundation checkpoint does not migrate creation.
2. Creation handler, minimal shared-form plumbing, applicable pins, focused
   creation/loaded-Admin tests and updated records.
Each requires exact-content approval. 1A remains incomplete pending checkpoint 2,
covering validation and bounded acceptance; this adds no new acceptance gate.

Retain three-second pane successes; persistent actionable errors; explicit
operation/target/scope identities; matching resolution, unrelated/newer feedback
and stale-result/timer protection. Separate mutation failure from completed
mutation plus refresh failure. Preserve endpoints, payloads, authorization,
confirmations, drafts, selections and behavior; busy protection spans refresh.
Never replay mutations automatically. No D2 near-field/connection/polling work.
1B retains accepted creation; 1C retains setup-opening rules and intentional
transitions; 1D retains move/delete-setup options and the existing dialog.

Nine foundation preparation tests pass; covering execution and creation
integration remain pending. User-directed intermediate 1A/1B/1C pushes and
corrections include [skip ci]; final 1D uses normal push-triggered CI unless
subsequently directed otherwise. No workflow edit or separate dispatch.

009.1-009.6, 4A.1-4A.13 and accepted Stage 2 stay closed. Stage 1, Stages 3-4,
Deliverable 1 acceptance, D2 and 009.7/009 stay open. Historical pending notes do
not reopen Stage 2. Test-suite cleanup remains deferred until after 009.
