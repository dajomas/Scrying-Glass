# 185. Monster provider and roster correction plan

[Back to TODO index](../../TODO.md)

- Updated: 2026-11-08. Tracking: SG-TODO-018 follow-up and adjacent lookup/roster corrections.
- Status: A.1 accepted; A.2 backend delivered, first CI failed on two stale locked-page expectations; focused test correction included with covering CI pending. Commit 4, A.3 and stage B remain pending.
- Branch: features/perplexity-018. No merge/write-back or overall close-out authorized.
- Related: [018 initiative/refresh contract](180-monster-initiative-bonus.md), [lookup](010-monster-lookup.md), [source configuration](060-fivetools-source-configuration.md), [rosters](../handover/310-admin-rosters.md), [A.1 history](../handover/335-fivetools-initiative-correction.md), [current A.2 delivery](../handover/340-combined-monster-lookup.md).

## Decision and current state

The rejected step-6 close-out draft must not be pushed. SG-TODO-018 as a whole is
not accepted or completed. A.1 alone has covering successful CI and explicit manual
acceptance. The user chose blocking incomplete lookup and approved four A.2 commits;
that supersedes the initial two-commit proposal. No owner/deadline is assigned.
This section consolidates current requirements/status, not application history.
Earlier detailed records remain in the linked handover and the immutable
[pre-activation snapshot](https://github.com/dajomas/Scrying-Glass/blob/d4757545a857f57b541659e860e52272b5d1fafc/docs/todo/185-monster-correction-plan.md).
No unfinished action is removed by that consolidation.

## Processing order

Process A before B, retaining the six actions below. Every implementation increment
requires its own exact-content approval, appropriate tests and documentation.
Review covering CI and fix failures before calling an increment validated.

### Stage A: provider correctness and candidate selection

1. A.1: fix 5e.tools initiative extraction for creation and Refresh. Accepted.
   - Noble Prodigy XMM +7 is verified from supplied provider JSON/renderer and the
     user's deployed creation, Refresh/apply/reload and raw16+bonus7=total23 checks.
   - Signed values, exact source identity and provenance are retained. Explicit
     zero differs from missing; no absent-field Dexterity guess or source-backed
     default zero. The linked 180 contract remains authoritative.
2. A.2: replace fallback-only lookup with combined-source search. In progress.
   - Search all enabled providers and configured books, not disabled providers or
     unconfigured books. Preserve all available provider/book/edition versions and
     their separate statistics; do not collapse editions or merge fields.
   - Acceptance case: D&D Beyond 2014 and 5e.tools 2024 versions both selectable.
   - Keep selected identity through creation/Refresh. Fail closed on any enabled
     provider failure or incomplete book search: report an explicit error with no
     candidates, rather than offering partial results as exhaustive.
   - Retain the existing configuration keys/defaults, documenting the independent
     candidate-search meaning of fivetools_fallback and the unchanged legacy paths.
   - Commit 3 activates the backend; commit 4 still must update in-UI help/config
     comments and associated browser/application regressions. README describes the
     interim runtime; older ordering help is a disclosed limitation until commit 4.
3. A.3: automatically resolve a sole available Refresh candidate. Pending.
   - Multiple candidates require selection; zero remain unresolved. Do not silently
     substitute another source for retained identity. Auto-resolution must not check
     fields, mutate state or bypass Apply; preserve other rows' choices.

### Stage B: compact and consistent roster presentation

4. Remove Roll heading and (legacy) suffix, retaining accessible raw-input labels,
   separate totals and internal legacy semantics. Presentation only, not migration.
5. Repair status/control wrapping without a blanket nowrap that overflows narrow
   viewports; test long names/statuses. Use fixed AC, HP and Init labels without
   on/off wording, with state styling consistent with Join Battle, Ally and Visible.
   Retain programmatic state (for example aria-pressed), keyboard/focus access and
   non-colour-only indication.
6. Replace displayed standing with alive consistently in Characters and Monsters,
   without unnecessary stored-identifier renames or life-state rule changes.

### Final validation and acceptance

After A/B, review covering CI and desktop/narrow workflows against all six actions.
Keep format/unit/ASGI/browser/live-provider/manual evidence distinct and disclose
unexecuted checks/fixture limits. Obtain workflow/visual acceptance and resolve
remaining agreed checks before step-6 reconciliation. Completion and merge are
separate approvals. A.1 acceptance does not close A.2 or SG-TODO-018.

## Current four-commit plan and fixture readiness - 2026-11-08

1. Preparation: bc28cd96f47c4a86f2e9d7a47eaef8744672ff68; successful CI
   42500152371 attempt 1, publication aa12c783e426ab4e326a023772d2a37bd51996b1.
2. Fixture isolation/expired-offer restoration: 22e0f08f27bf0a340fbfb0f269d330513ca7569a;
   successful CI 42501718072 attempt 1, publication d4757545a857f57b541659e860e52272b5d1fafc.
   Run/job metadata confirms every listed step/cleanup succeeded for that tested SHA.
3. Backend activation: 5414f1359808fdc07c75b94b1ca3ffe15c078d70; first CI failed, targeted fixture correction included, covering CI pending.
4. Help/config wording and browser/application/final validation: pending.

### Initial activation preparation (historical)

Prepared commit-3 source and both migrated test modules parse/compile. Thirty-six
isolated cases passed using the actual combiner and extracted lookup body with
mocked provider/signing boundaries. That is not full application, ASGI, browser or
live-provider proof. Those suites were not run locally because FastAPI was absent;
normal existing CI discovers the migrated tests. No new CI pass is claimed.
Runtime/manual A.2 acceptance remains required after the planned delivery.

## Original planning inspection and validation status (historical)

The pre-activation snapshot above preserves the original planning-only skip rule,
inspection and stage records. The current mixed implementation commit runs normal
CI, without a skip marker, workflow modification or separate dispatch.

## A.1 implementation increment - 2026-11-08

Accepted source extraction history and source-file hashes are preserved in 335.

## A.1 CI fixture correction - 2026-11-08

Run 42496852926 remains failed history; later covering success does not relabel it.

## A.1 acceptance and initial A.2 staged preparation (historical) - 2026-11-08

A.1 covering run 42497904756 attempt 1 passed exact
9417cf7d0c8fc2f4d45606708c5312ef508d96a6; publication
8fdf41731ad42a936721a841e26c82d2aaa9e479. The user confirmed all three manual checks.
The initial two-commit A.2 plan is superseded by the four-commit plan above.

## Commit 3 locked-page CI correction - 2026-11-08

Run 42503436253 attempt 1 failed for exact tested SHA
5414f1359808fdc07c75b94b1ca3ffe15c078d70; publication
a06ac1fad20816ff3403506eca070cc1b101cc83 / ci-results-42503436253-attempt-1.
Main/repeated suites each ran 1,391 tests with the same two assertion failures in
test_dndbeyond_locked_pages.SelectionIntegrationTests, not four distinct defects.
The expectations of one candidate and no secondary call contradict combined lookup.

This correction updates only that fixture and tracking documents. It retains both
provider candidates after an accessible primary result and verifies both providers
are queried on failure while all results/signing remain blocked. A new secondary-
failure case strengthens this contract; the six access-gate methods are unchanged.
Local isolated reconstruction reproduced the original two failures (9 methods),
then passed all 10 corrected methods using unchanged production D&D/pure helpers
and the four production selection nodes already extracted by the fixture. This is
not server/package initialization, real signing, ASGI, browser, live-provider or
full-suite verification. Covering normal CI must pass before commit 4. Production
code, access-gate classification and workflows are unchanged; no A.2 completion.
