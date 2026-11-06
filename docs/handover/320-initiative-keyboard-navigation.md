# 320 - Initiative keyboard navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-013](../todo/130-initiative-keyboard-navigation.md).
Status: feature scope closed at the user's explicit direction; separate test-only
correction included, but covering green local/CI rerun remains outstanding.
Do not represent this as successful full-suite validation.
Initial delivery: d23ee70d6beea3f6c5031f0102c27e5f537edbc8. Wrapping/Escape delivery:
8a5fa937cecd8563d5fe79a28a32a73fcd0babd1, based on
5992362c478c7763432268b8fd0b33d72140ddab.

## Current decision and implementation

The user initially approved native first/last exit, then reported it unintuitive
and requested first/last wrapping. They approved Escape as the loop exit. The
current rule is within-roster, displayed-row-order cyclic Tab/Shift+Tab, never a
forced jump between Characters and Monsters. Single-editor Tab stays on that field.
Hidden/disabled/readonly/inert/negative-tabindex fields are skipped; modified keys
and composition remain native. Empty rosters do not intercept navigation.

Escape from an initiative editor focuses the roster scroll region, clears the
refresh anchor and enables normal Tab/Shift+Tab within that roster. This pass-
through survives table replacement, so Tab through the first editor can reach Edit
and other controls instead of re-entering the loop immediately. Leaving/re-entering
the roster or pointer interaction re-enables looping. The enhancement supplies a
tabindex only if the region lacks one; existing roster labels/focus remain.

The enhancement still loads after character-hp-display.js and observes only direct
table replacement. Its navigation anchor identifies destination combatant and
campaign/setup, restoring focus after reorder only if the old node disconnected
and focus fell to body/region. Pointer/external focus, window blur, changed scope
or missing destination cancel restoration; Escape explicitly cancels it as well.
Existing local focus exposure is retained, and installation is idempotent.

WeakMaps retain destination drafts and track emitted/attempted values. A restored
draft missing native change emits one bubbling change in a blur microtask through
the original delegated handler; native change clears the fallback, and attempt
tracking propagates across replacements to avoid replay/automatic rejected-value
retry. No network code, replacement save API, validation or combat-order rule is
added. Admin core fragments, marker/assembly identities, backend rules, permissions,
HP workflow and Turn removal remain unchanged. This is not 009.5 navigation.

## Preparation history

Initial preparation passed syntax/AST and five isolated Chromium methods. An
intermediate duplicate-change assertion exposed a defect, corrected by propagating
attempt tracking before all five methods passed. Those original checks and the
initially prepared seven-method suite did not validate the later wrapping change.

Wrapping correction preparation passed node --check, regression AST parsing and
all five updated isolated Chromium methods. They cover 1440/375 navigation in both
rosters, both wrap directions, Escape, normal forward/reverse navigation afterwards,
pass-through across rerender, re-entry/pointer reactivation, single/empty/unavailable
fields, modifier noninterception, refresh identity/drafts, exact change counts,
missing-change fallback and pointer/scope/deletion cancellation. These are isolated
DOM fixtures, not a complete application or authenticated server. Three full-Admin
methods were also prepared under existing test discovery without workflow changes.
Their subsequent observed CI results are recorded below.

## Reviewed local and CI evidence - 2026-11-06

CI: Branch tests run 42285125000 attempt 1 tested exact
8a5fa937cecd8563d5fe79a28a32a73fcd0babd1 on features/perplexity. Evidence at
69d028b4c62e697e11165e1b72425e5b4b145fde under ci-results-42285125000-attempt-1.
run.json reports completed/failure for workflow and tests job. Python/browser and
standalone audit steps failed; syntax/import, pytest, JavaScript and artifact upload
succeeded. Post setup-node/setup-python cleanup steps were skipped, not passed.

workflow.log reader-chunks/file-000025 parts 000065-000066 explicitly report all
eight initiative-navigation methods OK: three full-Admin asset/native save-refresh-
rejection/wrapping-Escape methods and five isolated fixture methods. Part 000080
shows the older test_keyboard_reaches_every_button_and_scrolls_locally failing
at tests/test_monster_button_layout.py line 145 for the viewport subtests; parts
000109-000110 show the repeated audit failing at 1440/768/375, 1,074 tests with
three failures and 682 connections/zero without explicit close. These are the same
fixture failures repeated, not separate application defects or a connection leak.

Local: suite=all tested the same 8a5fa937 revision; publication
58b6f0f2c6fefa90681ab680baf248aee73186fd, folder
local-tests-8a5fa93/run-20261106T200427Z-FEmi6R. environment.txt reports completed=1,
20:04:27Z to 20:10:31Z. Overall exit-code.txt is 1. summary.tsv reports unittest
and standalone script-2 exit 1, all other command entries zero. The complete
suites/standalone/script-2.log reports 1,074 tests, the same three viewport failures
and 682/0 connections. Main unittest output retrieved for review was truncated;
its failure status is verified by its command exit, with the complete repeated
audit supplying counts and failure details. Published/completed is not passed.

## User-directed feature close-out

After these findings were explained, the user explicitly requested finishing and
closing 013, updating/pushing documentation with [skip ci], then making the test
correction. Documentation-only close-out eb936e2421712e6e8c871b923d08a44bc3caa900
was published first, changing only the index and these task/handover documents.
It ran no tests and changed no application/tests/workflows, with [skip ci] and no
separate dispatch. This records user-directed feature acceptance and closure with
a disclosed validation exception, not green full-suite validation or a waiver of
the requested test repair. Dedicated browser HTTP state/saves remain intercepted.

## Subsequent test-maintenance correction - 2026-11-06

The old fixture entered initiative and immediately expected Tab to reach Edit.
With the approved single-editor wrap that precondition was stale. The separate
corrective delivery adds seven lines before button traversal: Escape, assert
roster-region focus, Tab/assert checkbox, Tab/assert initiative. It uses normal
keyboard events, does not force button focus, and leaves application code untouched.
All existing 10-forward/9-reverse visits, strict local-focus visibility and scroll
checks at 1440/768/375, error/no-mutation assertions and other layout methods remain.

Executed preparation: corrected-method AST parsing and assertion-preservation
comparison passed. The method retains all eight original assertion calls and adds
three, with its remainder identical when the insertion is removed. The assembled-
Admin browser method and full application suite were not executed in preparation;
static checks are not substitute pass evidence. The existing CI discovery covers
the changed method. No workflow changes, skips or weakened checks are introduced.

This mixed commit changes tests/test_monster_button_layout.py and proportionate
TODO/task/handover status notes only. It omits [skip ci] for normal push-triggered
CI, with no separate dispatch or inferred triggered/pass state. A covering green
local/CI rerun and audit review are still required to resolve the validation
exception; old failed evidence remains historical and does not validate the fix.
Feature scope stays closed at user direction while that follow-up stays open.

README, User Guide and HANDOVER index were reviewed/reused and remain accurate
without edits. The 018 backlog addition and other task statuses are preserved.
009.4/012 stay closed, overall 009 remains in progress, and later tasks are unchanged.
