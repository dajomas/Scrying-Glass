# 091 - SG-TODO-022 close-out: acceptance and documentation (022.16)

[Back to handover index](../../HANDOVER.md) · [TODO 220](../todo/220-admin-statblock-viewer.md) · [Correction round 1](088-statblock-correction-round-1.md) · [Windows workers](089-windows-worker-limits.md)

Date: 2026-11-21. Branch `features/claude-statblock`, baseline `28ff23c`. SG-TODO-022 (GM-only
statblock viewer and statblock imports) is **completed and closed**.

## Acceptance

- The user accepted the delivered feature in steps on 2026-11-20 (correction-round
  findings 2-4; then finding 1 with the stats-lookup paywall rules, statblock collection
  on Add Monster/Import with its confirmation dialog and the Show statblock button in Add
  Monster), confirmed Windows and Linux/WSL2 operation, and on 2026-11-21 08:21 CET asked
  to "implement 022.16 and close out 022" after the green e2e run.
- 5e.tools `_versions` candidates and generated magic-item variants (04e.2) were moved to
  SG-TODO-033 by the user's decision of 2026-11-20 and do not block closure.
- The engineering safeguards proposed in Stages A and C1 were agreed on 2026-11-20 as fixed
  constants (TODO 220).

## Validation evidence

- CI (Branch tests, published by Publish CI results): green from run 44807877763 onward;
  latest code run 44832146478 for `524412d`: 2286 main-suite tests, pytest and standalone
  checks passed (`ci-results-44832146478-attempt-1`).
- E2E (`tools/run_e2e.sh`, Chromium and Firefox): run 20261121T065222Z against `1180299`:
  137 passed, 0 failed, including the axe scans, the statblock viewer and both statblock
  import flows (`e2e-results/20261121T065222Z/`).
- Windows: `test_worker_windows` 13/13 with the venv interpreter; Find statblock and the Add
  Monster preview with the real server (user, 2026-11-20).

## Documentation reconciled (022.16)

- `README.md`: three applications; statblock capability; statblock viewer interface row
  (no longer "in development"); preparation requirements (prlimit on Linux, Job Object on
  Windows, fail-closed elsewhere); Python 3.14 advice for Windows environments; statblocks
  in database backups and campaign bundles (version 2).
- `docs/User-Guide.md`: new "Statblocks" section (viewer access and layout, sources, Add
  Monster preview and collection with Replace statblocks?, Edit Monster, Load statblocks,
  automatic loading, storage, platform requirement); port note updated.
- `DEPLOYMENT.md`, `docs/Systemd-Deployment.md`: worker requirements, GM-only port; the unit's
  hardening allows prlimit.
- `docs/technical/010-architecture-runtime-security.md`: three applications and a statblock
  architecture summary; `020` already lists the statblock routes.
- `config.example.yaml`: viewer comment and worker memory limit per platform.
- TODO 220, the TODO index and the handover index: SG-TODO-022 closed.

## Not implied

No merge, deployment or release. The user merges `features/claude-statblock` into
`features/claude`, then `features/development`, then `main`.

## Follow-up items

SG-TODO-033 (5e.tools versions and magic-item variants) and the other proposed TODOs
(SG-TODO-023 to SG-TODO-032) remain open in the TODO index.
