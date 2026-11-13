# 130. Initiative keyboard navigation

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-013
- Status: completed, 2026-11-06. User-directed feature acceptance retained; the test-maintenance follow-up has covering successful local/CI suite and audit evidence, resolving the former validation exception. Fixture results are not authenticated live-server validation.
- Recorded: 2026-11-06. Wrapping/Escape revision approved: 2026-11-06.
- Priority, owner and deadline: not assigned.
- Coordination: follows completed 009.4/012 and precedes 009.5.
- Delivered wrapping/Escape implementation: 8a5fa937cecd8563d5fe79a28a32a73fcd0babd1.
- User-directed documentation close-out: eb936e2421712e6e8c871b923d08a44bc3caa900, with [skip ci].
- Verified corrective test revision: 3709341013dcef483a11975b5c6a5dd3f1c2603c.

## Current approved behaviour

Within Characters or Monsters, Tab moves to the next available initiative editor
and Shift+Tab to the previous in displayed row order. Last and first wrap to each
other in both directions. Navigation stays within the current roster and skips
unrelated controls and hidden/disabled/readonly/inert/negative-tabindex editors.
A single editor keeps focus on itself; empty rosters introduce no interception.
Modified shortcuts and composition are not intercepted.

Escape from an initiative editor focuses the roster's scroll region and clears
refresh restoration. Normal Tab/Shift+Tab navigation remains active within that
roster, allowing access to other row controls instead of immediately looping again.
Leaving the roster and re-entering, or pointer interaction, re-enables wrapping.
The user explicitly approved wrapping and Escape exit after finding the initial
native-boundary exit unintuitive. This supersedes the original non-wrapping rule
in initial implementation d23ee70d6beea3f6c5031f0102c27e5f537edbc8.

Existing change/save validation, permissions, API payloads and combat ordering
remain authoritative. Same-scope refresh follows destination combatant identity,
retains destination drafts and avoids replaying emitted changes. A restored draft
missing native change emits one change on later blur through the original handler.
Pointer/external focus, window blur, changed scope or a missing target cancel
restoration. No new network/save implementation is introduced.

## Validation evidence and user-directed close-out

Correction preparation passed node --check, regression AST parsing and all five
isolated Chromium methods. Later CI run 42285125000 attempt 1 covered exact
8a5fa937cecd8563d5fe79a28a32a73fcd0babd1. Evidence publication:
69d028b4c62e697e11165e1b72425e5b4b145fde, folder ci-results-42285125000-attempt-1.
All eight dedicated initiative-navigation methods explicitly passed, including
full-Admin wrapping/Escape exit and native save/refresh/rejection. Workflow/job
conclusion was failure: the older button-traversal test failed at 1440/768/375,
and the connection audit repeated those same three failures. Its repeated suite
ran 1,074 tests with three failures and 682 connections/zero without explicit close.
Syntax/import, pytest, JavaScript and visual-upload steps succeeded.

Completed local suite=all tested the same 8a5fa937 revision. Evidence publication:
58b6f0f2c6fefa90681ab680baf248aee73186fd under
local-tests-8a5fa93/run-20261106T200427Z-FEmi6R. completed=1 but overall exit=1;
unittest and standalone script-2 exited 1, all other command entries exited zero.
The repeated suite reports 1,074 tests, three failures at the same keyboard-test
widths, and 682/0 connections. Completion/publication does not mean test success.

After reviewing these results, the user explicitly requested finishing/closing 013
and pushing a documentation-only close-out with [skip ci], then making the test
correction. That feature close-out was delivered at eb936e2421712e6e8c871b923d08a44bc3caa900.
It recorded user-directed acceptance/closure with a known validation exception,
not a fully passing suite or assistant-executed authenticated/live persistence audit.
The later covering results below resolve that exception, without rewriting these
historical failures as successes.

## Test-maintenance correction - delivered and verified

The test exits initiative wrapping with Escape, asserts roster-region focus, and
Tabs through checkbox and initiative. Corrective commit
3709341013dcef483a11975b5c6a5dd3f1c2603c adds Tab/assert Edit, then Shift+Tab/assert
initiative before the original button loop. The loop starts from initiative, not
checkbox; the discarded draft that moved backward again to checkbox was not used.

Relative to b510d4269d9d41ae71cf913d117214796199bea0, four lines and two assertions
were added without removing existing checks. The method has thirteen assertion
calls: the original eight, three Escape-precondition assertions and two native-order
assertions. Ten forward/nine reverse button visits, local visibility, scroll,
viewport, errors and mutations checks remain. Wrapping and application behaviour
were not changed; focus was not forced. Preparation fragment AST/comparison checks
were static checks, not the subsequent full-suite execution evidence.

## Covering validation close-out - 2026-11-06

Both reviewed runs cover exact 3709341013dcef483a11975b5c6a5dd3f1c2603c:

- Local suite=all: publication c44a0c43d53f0a32f7c96fa2417955388252008a,
  folder local-tests-3709341/run-20261106T205300Z-tsCSj8. completed=1 and overall
  exit=0; every summary.tsv command exits zero, including syntax/import, unittest,
  pytest, 38 JavaScript entries and six standalone entries. The repeated audit
  reports 1,074 tests OK and 682 connections/zero without explicit close.
- CI: Branch tests run 42292006888 attempt 1, published at
  8723a4c9451cfd334287a00fd5023e8c44b8e236 under ci-results-42292006888-attempt-1.
  Workflow and tests job are completed/success. The corrected roster keyboard test
  and all eight dedicated initiative-navigation methods explicitly pass. The main
  suite and repeated audit each report 1,074 tests OK; audit reports 682/0
  connections and PASS. Syntax/import, pytest, JavaScript, standalone checks and
  visual-artifact upload succeed.

The outstanding local/CI suite-and-audit validation action is resolved. Detailed
log locations and review limitations are recorded in the
[handover close-out](../handover/320-initiative-keyboard-navigation.md#covering-validation-close-out---2026-11-06).
Earlier 009.4/012 evidence is not substituted for these covering results. Browser
fixtures remain distinct from authenticated live-server verification.

This close-out changes documentation only, with [skip ci] in the commit message.
No new tests were executed for the documentation update, no workflow is modified
or separately dispatched, and no new workflow state is inferred from the marker.
README and HANDOVER index remain accurate without edits; unrelated tasks and
prior acceptance decisions are unchanged.
