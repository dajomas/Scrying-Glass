# 185. Monster provider and roster correction plan

[Back to TODO index](../../TODO.md)

- Updated: 2026-11-08. Tracking: SG-TODO-018 follow-up and adjacent lookup/roster corrections.
- Status: in progress. A.1 accepted; all four A.2 increments and commit 5 delivered, commit-5 covering CI verified, A.2 manual acceptance pending. A.3 implementation included in this increment; covering CI/manual acceptance pending. Stage B remains pending.
- Branch: features/perplexity-018. No overall close-out, merge or write-back authorized.
- Related: [018 contract](180-monster-initiative-bonus.md), [lookup](010-monster-lookup.md), [configuration](060-fivetools-source-configuration.md), [rosters](../handover/310-admin-rosters.md), [A.1 history](../handover/335-fivetools-initiative-correction.md), [current A.2/A.3 delivery](../handover/340-combined-monster-lookup.md).

## Decision and current state

Do not push the rejected step-6 close-out draft. SG-TODO-018 is not accepted overall.
A.1 alone has covering CI and explicit manual acceptance. The user chose blocking
incomplete lookup and approved four A.2 increments, superseding the initial two.
No owner/deadline is assigned. This is the current task scope; historical delivery
records and failed/passing evidence remain in the linked handovers and immutable
[pre-finalization snapshot](https://github.com/dajomas/Scrying-Glass/blob/ce44afba0e12cd4b46125e735e935753ccb41be0/docs/todo/185-monster-correction-plan.md).
No pending action is removed by this consolidation.

## Processing order

Process A before B. Each implementation/corrective write requires exact-content
approval, appropriate tests/docs and review of covering CI before validation claims.

### Stage A: provider correctness and candidate selection

1. A.1 initiative extraction: accepted. Noble Prodigy XMM +7, creation, Refresh/
   apply/reload and raw16+bonus7=23 were confirmed by the user. Signed values, exact
   identity/provenance and explicit-zero versus missing remain required; no absent-
   field Dexterity guess/source-backed zero. The linked 180 contract is authoritative.
2. A.2 combined search: implementation included; acceptance pending.
   - Search enabled providers and configured books only. Keep provider/book/edition
     versions and their statistics separate; do not collapse editions or mix fields.
     Acceptance example: D&D Beyond 2014 and 5e.tools 2024 both selectable.
   - Retain exact selected identity through creation/Refresh. Any enabled-provider
     failure/incomplete book search must return an explicit error with no candidates,
     not selectable partial results presented as exhaustive.
   - Keep keys/defaults and document fivetools_fallback as independent enablement
     for candidate search; legacy image/stats fallback behavior stays unchanged.
   - Commit 4 aligns in-UI help/config comments and adds browser/application checks.
     Later covering commit-5 CI is verified; deployed workflow acceptance is still
     required before A.2 closure.
3. A.3 sole-candidate Refresh auto-resolution: implementation included in this
   increment; validation/acceptance pending. Multiple candidates still require
   selection; zero stay unresolved. Never substitute another retained identity.
   Auto-resolution must not select fields, mutate state or bypass Apply; retain
   other rows' choices. See the separate gate below.

### Stage B: compact and consistent roster presentation

4. Remove Roll heading and (legacy) suffix; retain accessible raw-input labels,
   separate totals and internal legacy semantics. No data migration.
5. Fix status/control wrapping without blanket nowrap/viewport overflow; test long
   names/statuses and narrow UI. Fixed AC/HP/Init labels omit on/off wording; style
   state consistently with Join Battle/Ally/Visible. Retain programmatic state
   (such as aria-pressed), keyboard/focus access and non-colour-only indication.
6. Replace displayed standing with alive in Characters/Monsters, without needless
   stored-identifier renames or life-state rule changes.

### Final validation and acceptance

After A/B, review CI and desktop/narrow workflows against all six actions. Keep
format/unit/ASGI/browser/live-provider/manual evidence distinct; disclose skipped,
unexecuted and fixture limits. Obtain workflow/visual acceptance and resolve agreed
checks before step-6 reconciliation. Completion and merge are separate approvals.
A.1 acceptance and code delivery do not close A.2 or SG-TODO-018.

## Current four-commit plan and validation - 2026-11-08

1. Preparation: bc28cd96f47c4a86f2e9d7a47eaef8744672ff68; CI 42500152371 attempt 1 succeeded.
2. Fixtures/expiry coverage: 22e0f08f27bf0a340fbfb0f269d330513ca7569a; CI 42501718072 attempt 1 succeeded.
3. Backend: 5414f1359808fdc07c75b94b1ca3ffe15c078d70; CI 42503436253 failed on two stale
   locked-page assertions. Correction e2d06aac12dabbdc7d4febe7be1efc3b3a2b2b29 has verified
   successful CI 42504619218 attempt 1, publication ce44afba0e12cd4b46125e735e935753ccb41be0.
   Run/job metadata confirms every listed step/cleanup succeeded for that exact SHA.
   Earlier failed runs remain failed historical evidence.
4. Help/config wording and added browser/application regressions: delivered; later
   commit-5 CI covers these files, while manual acceptance remains pending.

Commit-4 preparation: two static tests passed. Creation/import form blocks remain
byte-identical; every non-comment YAML line is identical. Updated/new Python tests
parse/compile. The retained browser fixture checks 1440/375 widths and no mutations.
Four new secured ASGI/SQLite methods cover source choice/signing/persistence, either-
provider failure, Refresh choice/apply/raw totals/unchecked state, and disabled
providers/empty sources. Synthetic data/provider transport and HP generation are
mocked; sessions pre-seeded. Neither browser nor ASGI suites ran locally (FastAPI
unavailable); no framework substitute, full-suite or live-provider pass is claimed
for that preparation. Later covering CI is recorded below. Existing normal CI
discovers both modules; no workflow change, skip or dispatch.

## Historical references

A.1's source hashes, failed CI, covering run 42497904756 and manual acceptance are
preserved in 335. The immutable snapshot above retains the earlier per-stage task
records/anchors; 340 records current delivery and limits. Root TODO remains
in progress with unchanged stable task links. Stage B and merge are not started.

## Commit 5 initiative overwrite follow-up - 2026-11-08

- Tracking: SG-TODO-018 follow-up before A.3.
- Status: implementation delivered as 7c760064aaa3484974362fb423f89245e4eb55fa; covering
  CI verified, deployed workflow acceptance pending.
- Agreed scope: remove the separate Add Monster bonus confirmation, not candidate
  choice or Refresh Apply. Available bonuses follow the existing AC/HP overwrite
  option; preserve intervening edits, missing/invalid values and exact signed offers.
- Preparation evidence: 21 local Chromium fixture methods and Node syntax passed;
  see [handover limits](../handover/340-combined-monster-lookup.md#commit-5-initiative-overwrite-follow-up---2026-11-08).
- Covering evidence: Branch tests 42514703672 attempt 1 succeeded for the exact
  implementation SHA above on features/perplexity-018. Publication
  8c7ce113ee00548ac3126744dd98a6c25d2a3579 / ci-results-42514703672-attempt-1.
  Main/repeated suites each report 1,398 tests OK; connection audit 752 opened/0
  without explicit close. All listed job steps succeeded; no skipped job steps or
  reported setup/collection failure. Individual test skips were not independently
  enumerated. Historical failed runs are not relabelled.
- Remaining acceptance gate: verify deployed desktop/narrow blank fills, checked/
  unchecked replacement, explicit zero/negative bonuses, edits during request/choice
  (including revert), missing/invalid source values, exact selected-provider
  attribution, cancellation/reset and no repeat popup/lookup. Verify source creation/
  Refresh persistence with server validation intact.
- Existing AC/HP assignments, Refresh review/Apply, A.3 and stage B stay separate.
  No task close-out, overall acceptance, merge or write-back is inferred.

## A.3 implementation and validation - 2026-11-08

- Status: implementation and regressions included in this increment; covering CI
  and deployed acceptance pending. Delivery SHA must be recorded after push.
- Behavior: identity-less sole signed candidate resolves automatically; multiple
  require choice, zero remain unavailable. Invalid retained identity/conflicting
  signed choice cannot substitute source. Exact-source fetch/token failure stays
  unresolved. No automatic field selection, live-stat/image mutation or HP roll.
- Continuation preserves unaffected server-held automatic/explicit rows and their
  proposals; unchanged UI preserves individual choices. Reload starts fresh.
  Explicit Apply and existing authentication/stale/expiry/transaction guards remain.
- Preparation: four Python code/test files compiled and parsed. Application/browser
  tests did not run locally: FastAPI and HTTPX2 are absent. Existing normal CI
  discovers the updated source tests and new ASGI/SQLite/Chromium regressions; no
  skip marker, workflow modification or separate dispatch. Fixture limits and
  coverage are recorded in [handover](../handover/340-combined-monster-lookup.md#a3-sole-candidate-refresh---2026-11-08).
- Required follow-up: inspect covering CI by exact SHA/run/attempt, diagnose failures
  without relabelling history, then deployed desktop/narrow acceptance for sole/
  multiple/zero, retained-source failure, other-row choices, unchecked defaults,
  explicit Apply/HP generation/persistence, stale rejection and cancellation.
  Recheck commit-5 Add Monster behavior unchanged.
- Stage B, overall SG-TODO-018 close-out, manual acceptance and merging remain
  outside this delivery.
