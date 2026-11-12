# 520 - Stage 1 campaign-operation feedback

[Back to handover index](../../HANDOVER.md)

## 1A foundation checkpoint - 2026-11-12

First of the user's approved two commits within 1A: encounterContext() returns a
fresh frozen {scope, epoch} snapshot without changing scope, tickets, feedback or
requests. Its epoch detects leaving and returning to the same scope identity.
Only this accessor and bootstrap asset v=2 are added. Existing campaign handlers,
all eight fragments, assembly, marker, pins and workflows are unchanged.
This is not creation migration or completed 1A; checkpoint 2 implements creation.
[Task/split/criteria](../todo/096-campaign-operation-feedback.md).

## Preparation evidence and limits

Base: 80cbdd8a82119f13c529a645e53bb393756aed21. Reconstructed originals matched live
bootstrap/header blobs 16c62c99d50455a3bc19265ae27f639fc8d051df and
fcf90a2afa8b682913b08130c198a4e8c725cc11. Proposed bootstrap: 6,920 UTF-8 bytes,
Git blob 747d352ca23d6935778fe6f8421c2a8f1b4902c7. Node syntax passed.
Nine focused Node tests passed, zero failures/cancellations/skips, using the
complete proposed bootstrap, unchanged production controller and mocked absent-view
DOM. Coverage: immutable snapshots, same/changed/returned scopes, obsolete/invalid
state, ticket/error preservation, lookup isolation, idempotency and asset wiring.
Removing immutability or losing the epoch caused expected failures; restored run
passed 9/9. Controller reconstruction matched blob
c4a82d73b21f4657da651ce45f76003c3348a6ef; controller is not changed.

These are preparation checks, not full repository/browser/live-server, human
visual, screen-reader or exhaustive accessibility evidence. Earlier 24-test
creation-draft evidence is separate. Covering validation and 1A acceptance remain
pending. No commit/run identity is invented. README and parent 090/097/380 records
were reviewed and retained; indexes link these dedicated records.

This mixed checkpoint uses user-directed [skip ci]; no workflow edit, separate
dispatch or inferred workflow outcome. Prior accepted scopes, including Stage 2,
stay closed. 1B-1D, wider Stage 1, Stages 3-4, both whole deliverables and 009.7/009
remain open. No merge, deployment or deferred test-suite cleanup.
