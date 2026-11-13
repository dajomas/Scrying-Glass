# 320 - Initiative keyboard navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-013](../todo/130-initiative-keyboard-navigation.md).
Status: completed; user-directed feature acceptance retained and corrective test
revision 3709341013dcef483a11975b5c6a5dd3f1c2603c has covering successful local/CI
suite and audit evidence. The former validation exception is resolved. This does
not establish authenticated live-server verification.
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
separate dispatch. This recorded user-directed feature acceptance and closure with
a disclosed validation exception, not green full-suite validation or a waiver of
the requested test repair. Dedicated browser HTTP state/saves remain intercepted.
The later covering results below resolve that exception; historical failures remain
failure evidence for their original tested revision.

## Subsequent test-maintenance correction - 2026-11-06

Corrective commit 3709341013dcef483a11975b5c6a5dd3f1c2603c retained the existing
Escape precondition. Relative to b510d4269d9d41ae71cf913d117214796199bea0, it added
four lines: Tab/assert Edit, then Shift+Tab/assert initiative. The original button
loop starts from initiative so its first Tab can reach Edit. The discarded draft
that continued backward to checkbox was not delivered. Application code and
workflows were unchanged and focus was not forced.

All existing 10-forward/9-reverse visits, strict local-focus visibility and scroll
checks at 1440/768/375, error/no-mutation assertions and other layout methods remain.
Two assertions were added to the existing eleven, yielding thirteen. The original
eight checks and three Escape-precondition checks remain intact.

Preparation AST parsing of a representative Python precondition/loop fragment and
removal-of-insertion comparison passed. Those static fragment checks and the earlier
minimal native-order browser fixture were not assembled-Admin/full-suite evidence.
The test-containing commit omitted [skip ci] for normal push-triggered CI without
workflow changes or separate dispatch. Subsequent execution results follow.

## Covering validation close-out - 2026-11-06

Tested revision for both runs: 3709341013dcef483a11975b5c6a5dd3f1c2603c.
Evidence publication commits identify stored results, not additional tested code.

### Local execution

Publication: c44a0c43d53f0a32f7c96fa2417955388252008a.
Folder: local-tests-3709341/run-20261106T205300Z-tsCSj8.

- environment.txt identifies exact commit, suite=all, a detached local clone,
  Python 3.14.7/Node 22.23.2 and completed=1, 20:53:00Z to 20:59:12Z.
- exit-code.txt is 0. Every summary.tsv command exits zero: syntax/import,
  unittest, pytest, 38 JavaScript entries and six standalone entries.
- suites/standalone/script-2.log reports 1,074 tests in 157.369s, OK;
  682 connections opened, zero without explicit close, and connection-audit PASS.
- The main unittest log returned during review was truncated. Its command success
  is supported by summary.tsv; counts and audit details come from the complete
  repeated-suite log, not from an invented reading of the truncated portion.

### GitHub Actions execution

Workflow: Branch tests, run 42292006888 attempt 1, push on features/perplexity.
Publication: 8723a4c9451cfd334287a00fd5023e8c44b8e236.
Folder: ci-results-42292006888-attempt-1.
Run: https://github.com/dajomas/Scrying-Glass/actions/runs/42292006888.

- run.json identifies exact headSha, completed/success for workflow and tests job
  128147529059. Syntax/import, Python/browser suite, pytest, JavaScript, standalone
  checks, visual-artifact upload and cleanup steps all succeed.
- workflow.log, reader-chunks/file-000025/part-000065.txt and part-000066.txt,
  explicitly reports all eight dedicated initiative-navigation methods OK,
  including full-Admin wrapping/Escape and native save/refresh/rejection.
- part-000070.txt explicitly reports the corrected
  test_keyboard_reaches_every_button_and_scrolls_locally OK. Its retained test
  covers 1440/768/375; the other roster-layout methods also pass in parts 70-71.
- part-000080.txt reports the main suite: 1,074 tests in 108.092s, OK.
- part-000107.txt reports the repeated suite: 1,074 tests in 105.817s, OK;
  682 opened connections, zero without explicit close, and connection-audit PASS.

The covering local/CI suite-and-audit validation exception is resolved. No further
corrective code is indicated by these results. Prior failed runs are retained as
historical evidence, not relabelled as passes. These fixtures, including mocked
HTTP/WS with real Chromium rendering, do not establish authenticated live-server
or complete end-to-end validation.

### Documentation-only recording

This update changes TODO.md and the existing task/handover sections only. The
commit message includes [skip ci]; no workflow is modified or separately dispatched.
No new tests were executed for this documentation update and no new workflow state
is inferred from the skip marker. README and HANDOVER index were reviewed/reused
and remain accurate without edits. The 018 backlog addition, closed 009.4/012,
overall in-progress 009 and other task statuses are preserved.
