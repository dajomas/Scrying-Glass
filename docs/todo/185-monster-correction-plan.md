# 185. Monster provider and roster correction plan

[Back to TODO index](../../TODO.md)

- Updated: 2026-11-08.
- Tracking: SG-TODO-018 follow-up and adjacent roster/lookup corrections; not a new completed task.
- Status: A.1 accepted; A.2 commit 1 has successful CI; commit 2 fixture readiness included with new CI pending. Active lookup is unchanged; activation, A.3 and stage B remain pending.
- Branch: features/perplexity-018. No merge or write-back authorized.
- Related: [018 initiative/refresh contract](180-monster-initiative-bonus.md), [lookup](010-monster-lookup.md), [5e.tools configuration](060-fivetools-source-configuration.md), [roster presentation](../handover/310-admin-rosters.md), [initiative handover](../handover/330-monster-initiative-foundations.md).

## Decision and current state

The user declined the proposed step-6 close-out reconciliation after reporting
implementation defects and adjacent usability issues. SG-TODO-018 is not accepted
or completed. The rejected reconciliation must not be pushed. Earlier passing CI
is scoped evidence, not proof that these reported behaviors work.

The original plan records the requested actions and processing order. The A.1
implementation update below records the first corrective increment. The single-candidate rule below supersedes the earlier
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
   - Noble Prodigy, XMM, initiative +7 is now verified from the supplied JSON
     and renderer: explicit proficiency multiplier 1, Dexterity 16 and CR 10.
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

## Original planning inspection and validation status (historical)

The inspected python/scrying_glass_monster_selection.py has no 5e.tools initiative
field in candidate construction and calls 5e.tools only when D&D Beyond returns
no candidates. static/monster-initiative-roll.js inserts Roll and (legacy). These
observations support investigation; they do not establish that a fix is delivered.
The other UI defects are recorded user findings, not independently reproduced here.

This planning commit changes human-readable documentation only. No application
code, tests, configuration or workflows change; no tests were run for it. Use
[skip ci]; do not modify workflows or separately dispatch CI. README continues to
describe existing fallback behavior until that implementation changes.

## A.1 implementation increment - 2026-11-08

Explicit signed totals, object totals and proficiency multipliers 0/1/2 now feed
creation offers and exact-source Refresh. Missing initiative has no Dexterity-only
fallback; explicit zero remains available. Unknown/malformed/out-of-range/copy
values cannot overwrite assigned bonuses. Existing source binding, explicit Apply
and persistence remain unchanged. A.2/A.3 and stage B are still pending.

Ten pure unit methods passed; all 503 supplied XMM entries were scanned offline:
187 available, 316 missing; Noble Prodigy +7. Python AST parsing passed. Two secured
ASGI/SQLite regression methods are prepared but unexecuted locally (FastAPI absent).
Normal CI discovers them; covering CI, live-provider and desktop/narrow acceptance
remain pending. See [A.1 handover](../handover/335-fivetools-initiative-correction.md).
The historical documentation-only skip rule above does not apply to this mixed
commit. Do not close SG-TODO-018 or merge/write back.

## A.1 CI fixture correction - 2026-11-08

Run 42496852926 attempt 1 failed for tested commit
7fb5c1ce9c2cddd2275dac4520b6b3b10ad2fcfd; publication
6d4b882e0c9591c8d7172a57a9322605dbcb881d,
ci-results-42496852926-attempt-1. Ten pure initiative tests passed, but two new
flow methods errored because fixture data shadowed candidate(), and four existing
source-configuration methods errored because extracted functions lacked package
metadata. Main and repeated suites each ran 1,375 tests with the same six errors.
These are not twelve distinct defects or completed end-to-end checks.

Rename the flow lookup helper and provide __name__/__package__ in the existing
source-configuration fixture; all 54 assertion calls are preserved. Production
code, initiative arithmetic and workflows are unchanged. Both corrected files
passed AST parsing and assertion-preservation checks; runtime/full-suite checks
remain pending because FastAPI is unavailable locally. Normal CI must cover the
correction, and failed run 42496852926 remains failed historical evidence.
See the linked 335 handover for log locations. No acceptance, close-out or merge.

## A.1 acceptance and initial A.2 staged preparation (historical) - 2026-11-08

A.1 is accepted: run 42497904756 attempt 1 passed tested commit
9417cf7d0c8fc2f4d45606708c5312ef508d96a6, publication
8fdf41731ad42a936721a841e26c82d2aaa9e479 / ci-results-42497904756-attempt-1.
All 1,375 main/repeated tests passed; ten initiative unit and both flow methods
passed, all workflow/cleanup steps succeeded, and connection audit was 742/0 PASS.
On 2026-11-08 the user confirmed creation +7, Refresh/apply/persistence and retained
raw 16 + bonus 7 = total 23. The earlier failed run remains failed history.
This accepts A.1 only; SG-TODO-018 and merge remain open.

The user chose blocking incomplete lookup and agreed two A.2 commits. This first
commit adds an unused pure combiner and twelve offline tests, and isolates the
shared secured creation/Refresh fixture by copying its configuration and explicitly
selecting D&D-only lookup. Existing 5e.tools flow fixtures explicitly re-enable it.
Active lookup still uses fallback-only behavior. README, help, config semantics,
source adapters, signing and Refresh resolution are not changed in this stage.

The combiner queries both enabled callbacks, preserves provider/book versions and
separate statistics, deep-copies results and reports fixed provider statuses.
Any exception, malformed provider list or per-provider limit breach returns an
explicit incomplete error and no candidates. Disabled callbacks are not invoked.
Public errors do not include exception details. Callbacks must raise for incomplete
source-book searches; the pure combiner itself does not fetch books or sign tokens.

Executed: twelve pure unit tests passed locally. The new module/tests passed local
import/execution. Shared ASGI fixture changes were reviewed, not runtime-tested:
FastAPI is unavailable. Existing CI discovers the new test module normally; covering
CI and application acceptance for A.2 are pending. Commit 2 must activate the engine,
migrate remaining direct HTTP/adapter fixtures and fallback-only expectations,
update help/README and fivetools_fallback compatibility wording, and verify signing,
identity retention, configured-book enumeration and blocked incomplete lookup across
creation/Refresh. A.3 and stage B are excluded. No workflow changes or skip marker.

## Current four-commit plan and fixture readiness - 2026-11-08

The user approved four A.2 commits, superseding the historical two-commit plan:
1. Combiner preparation (bc28cd96f47c4a86f2e9d7a47eaef8744672ff68).
2. Provider-specific fixture isolation and restored expired-offer coverage (this increment).
3. Active combined lookup, fallback-expectation migration and runtime documentation.
4. Help/config wording, associated browser/application checks and final validation.

Commit 1 has verified successful run 42500152371 attempt 1 for exact tested SHA
bc28cd96f47c4a86f2e9d7a47eaef8744672ff68; publication
aa12c783e426ab4e326a023772d2a37bd51996b1 / ci-results-42500152371-attempt-1.
All listed workflow and cleanup steps succeeded. That result does not cover this increment.

Commit 2 explicitly disables 5e.tools in D&D-only HTTP/signing fixtures and enables
it in their dedicated 5e.tools cases. It restores the expired-token rejection input
in the shared secured acceptance test, inadvertently omitted from commit 1.
The three provider-specific modules compiled locally with all 60 assertion calls
unchanged; two isolated fixture setup checks passed. The restored rejection method
parses and has three inputs. Actual suites/full ASGI validation remain unexecuted
locally (FastAPI absent) and require covering normal CI. Active lookup, signing,
UI, runtime configuration, production code and workflows are unchanged. A.1 remains
accepted; A.2, A.3, stage B, overall close-out and merge remain pending.
