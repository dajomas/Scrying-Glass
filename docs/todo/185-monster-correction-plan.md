# 185. Monster provider and roster correction plan

[Back to TODO index](../../TODO.md)

- Updated: 2026-11-08. Tracking: SG-TODO-018 follow-up and adjacent lookup/roster corrections.
- Status: A.1 accepted; all four A.2 implementation increments included, commit-4 CI and A.2 manual acceptance pending. A.3 and stage B remain pending.
- Branch: features/perplexity-018. No overall close-out, merge or write-back authorized.
- Related: [018 contract](180-monster-initiative-bonus.md), [lookup](010-monster-lookup.md), [configuration](060-fivetools-source-configuration.md), [rosters](../handover/310-admin-rosters.md), [A.1 history](../handover/335-fivetools-initiative-correction.md), [current A.2 delivery](../handover/340-combined-monster-lookup.md).

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
     Covering CI and deployed workflow acceptance remain required before A.2 closure.
3. A.3 sole-candidate Refresh auto-resolution: pending. Multiple candidates still
   require selection; zero stay unresolved. Never substitute another retained
   identity. Auto-resolution must not select fields, mutate state or bypass Apply;
   retain other rows' choices. Not implemented by A.2.

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
4. Help/config wording and added browser/application regressions: included here,
   new covering CI and manual acceptance pending.

Commit-4 preparation: two static tests passed. Creation/import form blocks remain
byte-identical; every non-comment YAML line is identical. Updated/new Python tests
parse/compile. The retained browser fixture checks 1440/375 widths and no mutations.
Four new secured ASGI/SQLite methods cover source choice/signing/persistence, either-
provider failure, Refresh choice/apply/raw totals/unchecked state, and disabled
providers/empty sources. Synthetic data/provider transport and HP generation are
mocked; sessions pre-seeded. Neither browser nor ASGI suites ran locally (FastAPI
unavailable); no framework substitute, full-suite or live-provider pass is claimed.
Existing normal CI discovers both modules; no workflow change, skip or dispatch.

## Historical references

A.1's source hashes, failed CI, covering run 42497904756 and manual acceptance are
preserved in 335. The immutable snapshot above retains the earlier per-stage task
records/anchors; 340 records current A.2 delivery and limits. Root TODO remains
in progress with unchanged stable task links. A.3, stage B and merge are not started.
