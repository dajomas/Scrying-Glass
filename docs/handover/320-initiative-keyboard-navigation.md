# 320 - Initiative keyboard navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-013](../todo/130-initiative-keyboard-navigation.md).
Status: feature scope closed at the user's explicit direction with a known overall-
suite validation exception; the separate test correction and green rerun remain
outstanding. Do not represent this close-out as successful full-suite validation.
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

## User-directed feature close-out and outstanding correction

After these findings were explained, the user explicitly requested finishing and
closing 013, updating/pushing documentation with [skip ci], then making the test
correction. This records user-directed feature acceptance and scope closure with
a disclosed validation exception. It does not waive or complete the requested
test repair, claim green full-suite results, or establish an assistant-executed
authenticated-server, live persistence or exhaustive accessibility/combat audit.
HTTP state/saves in the dedicated browser methods are intercepted.

Open follow-up: the old monster-button fixture focuses initiative and immediately
expects Tab to reach Edit. With the approved single-editor wrap this expectation
is stale. In a separate next commit, press Escape, verify region focus, navigate
natively through checkbox and initiative, then retain the full existing 10-button
forward/9-button reverse traversal, strict local-focus visibility, overflow and
no-mutation assertions. Do not bypass the enhancement or force focus onto buttons.
Run normal CI for the test-changing commit and review a covering rerun; no result
for an unmade correction is claimed. Track resolution in the 013 task and here.

This first close-out changes only TODO.md and these existing task/handover sections;
it runs no new tests and leaves application, tests, dependencies and workflows
unchanged. Commit message includes [skip ci], with no separate workflow dispatch.
README, User Guide and HANDOVER index were reviewed/reused and remain accurate
without edits. Preserve the newly added 018 backlog entry and other tasks.
009.4/012 stay closed, overall 009 remains in progress, and later tasks are unchanged.
