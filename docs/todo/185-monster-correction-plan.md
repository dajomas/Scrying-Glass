# 185. Monster provider and roster correction plan

[Back to TODO index](../../TODO.md)

- Updated: 2026-11-08. Tracking: SG-TODO-018 follow-up and adjacent lookup/roster corrections.
- Status: in progress. A.1 remains accepted; A.2 and A.3 accepted after covering corrective CI and user manual sign-off on 2026-11-08. Initial stage B delivered as 11f104058efb2a56365b0309ce8c6ee829d84c18; first CI failed and visual corrections requested. Colour-only/single-line follow-up included here; corrective CI/manual acceptance pending. SG-TODO-018 is not closed.
- Branch: features/perplexity-018. No overall close-out, merge or write-back authorized.
- Related: [018 contract](180-monster-initiative-bonus.md), [lookup](010-monster-lookup.md), [configuration](060-fivetools-source-configuration.md), [rosters](../handover/310-admin-rosters.md), [A.1 history](../handover/335-fivetools-initiative-correction.md), [current A.2/A.3/B delivery](../handover/340-combined-monster-lookup.md).

## Decision and current state

Do not push the rejected step-6 close-out draft. SG-TODO-018 is not accepted overall.
A.1 remains accepted. The user manually tested and signed off A.2 and A.3 on
2026-11-08, after successful covering corrective CI recorded below. The user chose
blocking incomplete lookup and approved four A.2 increments, superseding the
initial two. Stage B delivery and its visual/fixture correction are separate from
acceptance. No owner/deadline is assigned. Historical records and failed/passing
evidence remain in linked handovers and the immutable
[pre-finalization snapshot](https://github.com/dajomas/Scrying-Glass/blob/ce44afba0e12cd4b46125e735e935753ccb41be0/docs/todo/185-monster-correction-plan.md).
No pending action is removed by this consolidation. Earlier dated pending gates
below describe those deliveries, not a reversal of the later explicit sign-off.

## Processing order

Process A before B. Each implementation/corrective write requires exact-content
approval, appropriate tests/docs and review of covering CI before validation claims.

### Stage A: provider correctness and candidate selection

1. A.1 initiative extraction: accepted. Noble Prodigy XMM +7, creation, Refresh/
   apply/reload and raw16+bonus7=23 were confirmed by the user. Signed values, exact
   identity/provenance and explicit-zero versus missing remain required; no absent-
   field Dexterity guess/source-backed zero. The linked 180 contract is authoritative.
2. A.2 combined search: accepted after covering CI and user manual sign-off.
   - Search enabled providers and configured books only. Keep provider/book/edition
     versions and their statistics separate; do not collapse editions or mix fields.
     Acceptance example: D&D Beyond 2014 and 5e.tools 2024 both selectable.
   - Retain exact selected identity through creation/Refresh. Any enabled-provider
     failure/incomplete book search must return an explicit error with no candidates,
     not selectable partial results presented as exhaustive.
   - Keep keys/defaults and document fivetools_fallback as independent enablement
     for candidate search; legacy image/stats fallback behavior stays unchanged.
   - Commit 4 aligns in-UI help/config comments and adds browser/application checks.
     Commit-5 and later corrective CI are verified; the A.2 manual gate is satisfied
     by the user's explicit sign-off below.
3. A.3 sole-candidate Refresh auto-resolution: accepted. Multiple candidates still
   require selection; zero stay unresolved. Never substitute another retained
   identity. Auto-resolution must not select fields, mutate state or bypass Apply;
   retain other rows' choices. The first failed run remains failed; corrective
   delivery/CI and manual acceptance are recorded separately below.

### Stage B: compact and consistent roster presentation

Status: initial implementation delivered; first covering CI failed. Colour-only
controls/single-line status and fixture correction included here, with corrective
CI/manual acceptance pending. No corrective delivery SHA invented before push.

4. Remove Roll heading and (legacy) suffix; retain accessible raw-input labels,
   separate totals and internal legacy semantics. No data migration.
5. Status is one line, allowed to continue beneath AC/HP without covering values
   or controls or creating page-level overflow. Test short and long names/narrow UI.
   Fixed AC/HP/Init captions omit on/off wording, consistent with Join Battle/Ally/
   Visible colours. By the user's follow-up, remove dashes/checkmarks and use
   colour-only visual state, superseding the earlier non-colour visual-marker
   requirement. Retain aria-pressed, fixed accessible names and keyboard/focus.
6. Replace displayed standing with alive in Characters/Monsters, without needless
   stored-identifier renames or life-state rule changes.

### Final validation and acceptance

Review corrective stage-B CI and desktop/narrow workflows against all three roster
actions. Keep format/unit/ASGI/browser/live-provider/manual evidence distinct;
disclose skipped, unexecuted and fixture limits. A.2/A.3 are accepted, but stage B
needs its own workflow/visual acceptance before step-6 reconciliation. Overall
completion and merging remain separate approvals.

## Current four-commit plan and validation - 2026-11-08

1. Preparation: bc28cd96f47c4a86f2e9d7a47eaef8744672ff68; CI 42500152371 attempt 1 succeeded.
2. Fixtures/expiry coverage: 22e0f08f27bf0a340fbfb0f269d330513ca7569a; CI 42501718072 attempt 1 succeeded.
3. Backend: 5414f1359808fdc07c75b94b1ca3ffe15c078d70; CI 42503436253 failed on two stale
   locked-page assertions. Correction e2d06aac12dabbdc7d4febe7be1efc3b3a2b2b29 has verified
   successful CI 42504619218 attempt 1, publication ce44afba0e12cd4b46125e735e935753ccb41be0.
   Run/job metadata confirms every listed step/cleanup succeeded for that exact SHA.
   Earlier failed runs remain failed historical evidence.
4. Help/config wording and added browser/application regressions: delivered; later
   commit-5 CI covers these files. Manual acceptance was pending at that delivery
   and is now satisfied by the later A.2 sign-off.

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
preserved in 335. The immutable snapshot above retains earlier per-stage records/
anchors; 340 records current delivery and limits. Root TODO remains in progress
with stable task links. Overall close-out and merge are not authorized.

## Commit 5 initiative overwrite follow-up - 2026-11-08

- Tracking: SG-TODO-018 follow-up before A.3.
- Status: implementation delivered as 7c760064aaa3484974362fb423f89245e4eb55fa; covering
  CI verified. The deployed workflow gate listed here was pending at that delivery;
  the later explicit user sign-off is A.2/A.3, not invented broader acceptance.
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
- Acceptance checklist retained: deployed desktop/narrow blank fills, checked/
  unchecked replacement, explicit zero/negative bonuses, edits during request/choice
  (including revert), missing/invalid source values, exact selected-provider
  attribution, cancellation/reset and no repeat popup/lookup; source creation/
  Refresh persistence with server validation intact. Stage B does not change it.
- Existing AC/HP assignments, Refresh review/Apply, A.3 and stage B stay separate.
  No task close-out, overall acceptance, merge or write-back is inferred.

## A.3 implementation and validation - 2026-11-08

- Status: accepted. Implementation c62d203d3b92aa277eb7e34f4c90da789ab0e58b; fixture
  correction 1c289d485bffcf8197fb32238349729e52b822ed has verified successful covering
  CI and the user's manual sign-off below. The first covering run stays failed.
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
- The corrective CI/manual gates below are now satisfied for A.2/A.3 only. Stage B,
  overall SG-TODO-018 close-out and merging remain separate.

### First A.3 CI failure and fixture correction

Run 42516636403 attempt 1 failed for the exact A.3 implementation SHA above, on
features/perplexity-018. Publication 5c8cd561b46a8694fe3da267771927f31ff7b45c /
ci-results-42516636403-attempt-1 was inspected. Each main/repeated 1,406-test run
has one browser timeout in the same existing explicit-choice test, which offered
one candidate and expected the chooser A.3 now correctly omits. This is not a
collection/setup error or two distinct defects. New A.3 ASGI/isolated-browser
methods explicitly passed, but the overall run remains failed. Syntax/import,
pytest, JavaScript/upload succeeded; Node/Python post-setup cleanup skipped.
Connection tracking: 759 opened/0 without explicit close; the audit step still
failed with its repeated suite. Detailed paths and limits are in the
[handover correction record](../handover/340-combined-monster-lookup.md#a3-first-covering-ci-and-fixture-correction---2026-11-08).

The correction supplies two distinct candidates in the explicit-choice fixture
and preserves other-row/unchecked-HP/no-mutation assertions. A new assembled-
browser/secured-ASGI/SQLite method covers sole-candidate review and explicit Apply
at desktop/narrow widths. Production behavior is unchanged. Its preparation
compiled/parsed under 20,000 bytes; methods were not run locally because FastAPI/
HTTPX2 were absent. Delivery and successful covering CI are recorded below; the
old failure is not relabelled. No skip/workflow change/dispatch, close-out or merge.

### Corrective CI and user acceptance - 2026-11-08

Run 42517614512 attempt 1 succeeded for exact
1c289d485bffcf8197fb32238349729e52b822ed on features/perplexity-018. Evidence
publication 73183fd70d6111083b2ca0048c6a029c0c04fed8 /
ci-results-42517614512-attempt-1 was inspected. All listed steps and cleanup
succeeded, none skipped; no reported setup/collection failure. Main and repeated
suites each report 1,407 tests OK; connections 761 opened/0 without explicit close.
Repaired multiple-candidate and new assembled sole-candidate methods explicitly
passed. Detailed evidence/fixture limits are in the [handover acceptance record](../handover/340-combined-monster-lookup.md#corrective-ci-and-a2a3-acceptance---2026-11-08).

The user manually tested A2 and A3 and signed off on both on 2026-11-08. Record
A.2/A.3 accepted, not overall SG-TODO-018 completion or an assistant-run live audit.

## Stage B delivery and validation gate - 2026-11-08

- Initial implementation delivered as 11f104058efb2a56365b0309ce8c6ee829d84c18.
  Its first CI failed and visual follow-up was requested. The colour-only controls,
  single-line status lane and fixture correction are included here; corrective
  delivery SHA only after push. Corrective CI/manual acceptance pending.
- Fixed captions/pressed states, scoped actions, alive wording and removal of
  visible Roll/legacy text preserve underlying values/semantics. The fixed-stat
  handler uses boolean state, not label suffixes, and one existing PATCH. No
  optimistic mutation. User follow-up removes the initial minus/check decorations
  in both rosters while retaining pressed semantics and colours.
- Initial preparation: Node syntax and isolated Chromium passed 375/768/1440 with
  three replacements each, 18 keyboard activations, one helper call each, zero old
  delegate calls and no page errors. Layout/new full-Admin modules compiled/parsed;
  original layout blob verified. Full-Admin/application tests were not run locally.
- First covering evidence: run 42520146312 attempt 1 failed for exact initial
  implementation SHA above on features/perplexity-018; publication
  cdccf96fb0e0abd23d82783c0d38c43c3e0ff921 / ci-results-42520146312-attempt-1.
  Each main/repeated suite ran 1,409 tests with one runtime timeout waiting for
  a visible rejection message emitted in a collapsed input pane. No setup/collection
  error. Post-wait state assertions were unexecuted. Syntax/import, pytest,
  JavaScript/upload/checkout cleanup succeeded; Node/Python post-setup cleanup
  skipped. Connection tracking 762 opened/0 without explicit close does not turn
  the failed audit repeat into a pass. Keep this run failed historically.
- Follow-up preparation: CSS-only production change reserves a lower strip in
  every main roster data cell and positions a nonwrapping status line there,
  allowed past the name cell beneath adjacent columns without covering values.
  Revised three-method test compiles/parses; all 15 embedded JS expressions pass
  Node syntax. Isolated Chromium geometry at 375/768/1440, both rosters and three
  replacements passed one-line/spill/non-overlap/no-glyph/no-viewport-widening/no-
  page-error checks. This is synthetic markup/component CSS, not full Admin or
  live-server validation. Full-Admin tests not run locally (FastAPI absent).
- The rejection fixture opens the existing input pane through normal UI toggles
  before asserting visible feedback and unchanged state. Production notification
  placement is unchanged; it can remain hidden if that input pane is closed.
  Updated regressions measure the whole line for short/long names and check colour
  difference, glyph absence and retained exact PATCH count/payload/pressed state.
  See [follow-up evidence and limits](../handover/340-combined-monster-lookup.md#stage-b-ci-failure-and-colour-onlysingle-line-follow-up---2026-11-08).
- Required acceptance: desktop/narrow/short and long names, status one line under
  AC/HP with no value/control/next-row overlap, local scrolling/focus, no dash/check
  decorations, fixed controls distinguished by colour, mouse/Enter/Space toggling,
  rejected saves and persistence, preserved selection/bulk/Edit/statistics, raw
  labels/totals and legacy semantics, alive display with unchanged stored states
  and down/stable/dead behavior. Add Monster/Refresh remain unchanged.
- Normal CI, no skip/workflow edit/dispatch. Review exact corrective SHA/run/attempt,
  correct failures with fresh approval, then obtain user stage-B acceptance before
  overall close-out reconciliation. Merging/other-branch writes not authorized.
