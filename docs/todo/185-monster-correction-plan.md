# 185. Monster provider and roster correction plan

[Back to TODO index](../../TODO.md)

- Updated: 2026-11-08.
- Tracking: SG-TODO-018 follow-up and adjacent roster/lookup corrections; not a new completed task.
- Status: planned corrections; implementation and validation pending.
- Branch: features/perplexity-018. No merge or write-back authorized.
- Related: [018 initiative/refresh contract](180-monster-initiative-bonus.md), [lookup](010-monster-lookup.md), [5e.tools configuration](060-fivetools-source-configuration.md), [roster presentation](../handover/310-admin-rosters.md), [initiative handover](../handover/330-monster-initiative-foundations.md).

## Decision and current state

The user declined the proposed step-6 close-out reconciliation after reporting
implementation defects and adjacent usability issues. SG-TODO-018 is not accepted
or completed. The rejected reconciliation must not be pushed. Earlier passing CI
is scoped evidence, not proof that these reported behaviors work.

This document records the requested actions and processing order for later work;
it does not implement them. The single-candidate rule below supersedes the earlier
requirement to ask for candidate selection even when only one is available. The
combined-source requirement supersedes fallback-only search. Earlier delivery and
foundation notes remain history, not the current corrective work queue.

## Processing order

Process stage A before stage B, in the numbered order below. Each implementation
stage needs appropriate regression tests, documentation and its own exact-content
write approval. Review covering CI and fix failures before treating a stage as
validated. This documentation-only skip request does not apply to later code pushes.

### Stage A: provider correctness and candidate selection

1. Fix 5e.tools initiative extraction for creation and refresh.
   - Verify the actual provider data/rendering format before implementation.
   - User-reported acceptance example: Noble Prodigy, XMM, initiative +7. This
     value has not yet been independently verified against retrieved source data.
   - Handle validated provider representations rather than guessing from Dexterity
     or silently defaulting unsupported source data to a source-backed zero.
   - Preserve signed value, source identity and provenance through lookup, creation,
     review/apply and persistence. Explicit zero remains distinct from unavailable.
2. Replace fallback-only lookup with combined-source search.
   - Search all enabled providers and all configured source books, not disabled or
     unconfigured sources. Include every found version with clear provider/book/
     edition labels; do not collapse distinct versions or mix their statistics.
   - Acceptance case: D&D Beyond returns a 2014 version and 5e.tools returns a
     2024 version; both remain available for selection.
   - Retain exact selected identity for creation and refresh. Surface provider
     failures explicitly; do not silently present partial results as exhaustive.
   - Update fallback terminology/help and consider compatibility of the existing
     fivetools_fallback setting when preparing the implementation.
3. Automatically resolve one available candidate in Refresh.
   - Do not ask the user to select a sole candidate. Multiple candidates still
     require selection; zero candidates remain unresolved.
   - Automatic candidate resolution must not check fields, mutate live state or
     bypass explicit Apply. Preserve retained-identity constraints and other rows'
     selections; do not silently replace an exact retained source with another.

### Stage B: compact and consistent roster presentation

4. Remove excessive visible initiative row text.
   - Remove the Roll heading and (legacy) suffix.
   - Retain accessible raw-input labeling, separate calculated totals and internal
     legacy-total semantics; this is presentation cleanup, not a data migration.
5. Repair status/control layout and display-toggle presentation.
   - Avoid the reported status-line wrapping without a blanket nowrap rule that
     pushes controls outside the viewport. Test long names/statuses and narrow UI.
   - Use fixed AC, HP and Init labels without on/off wording. Show active/inactive
     state using color/styling consistent with Join Battle, Ally and Visible.
   - Retain programmatically exposed toggle state, such as aria-pressed, and
     keyboard/focus access; color must not be the sole accessible indication.
6. Replace displayed standing with alive in Characters and Monsters panels.
   - Change user-facing wording consistently without unnecessarily renaming stored
     life-state identifiers or changing life-state rules.

### Final validation and acceptance

After both stages, review covering CI and desktop/narrow workflow checks against
all six actions. Keep provider-format, unit, ASGI, browser, live-provider and manual
checks distinct; report unexecuted checks and fixture limits honestly. Obtain user
workflow/visual acceptance, resolve remaining agreed checks, then revisit step 6
tracking reconciliation. Completion and merge remain separate approvals.

## Inspection basis and validation status

The inspected python/scrying_glass_monster_selection.py has no 5e.tools initiative
field in candidate construction and calls 5e.tools only when D&D Beyond returns
no candidates. static/monster-initiative-roll.js inserts Roll and (legacy). These
observations support investigation; they do not establish that a fix is delivered.
The other UI defects are recorded user findings, not independently reproduced here.

This planning commit changes human-readable documentation only. No application
code, tests, configuration or workflows change; no tests were run for it. Use
[skip ci]; do not modify workflows or separately dispatch CI. README continues to
describe existing fallback behavior until that implementation changes.
