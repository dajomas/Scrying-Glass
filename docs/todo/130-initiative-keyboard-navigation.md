# 130. Initiative keyboard navigation

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-013
- Status: completed for feature scope at the user's explicit direction, 2026-11-06; test-only correction included, covering green local/CI rerun still pending. This is not a green full-suite sign-off.
- Recorded: 2026-11-06. Wrapping/Escape revision approved: 2026-11-06.
- Priority, owner and deadline: not assigned.
- Coordination: follows completed 009.4/012 and precedes 009.5.
- Delivered wrapping/Escape implementation: 8a5fa937cecd8563d5fe79a28a32a73fcd0babd1.
- User-directed documentation close-out: eb936e2421712e6e8c871b923d08a44bc3caa900, with [skip ci].

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
It records user-directed acceptance/closure with a known validation exception,
not a fully passing suite or assistant-executed authenticated/live persistence audit.

## Test-maintenance correction - included; rerun pending

The subsequent test-changing delivery updates only the precondition in
test_keyboard_reaches_every_button_and_scrolls_locally, tests/test_monster_button_layout.py.
From initiative it presses Escape, asserts roster-region focus, then Tabs through
checkbox and initiative before the original button traversal. This uses the
approved exit instead of expecting Tab to leave a single-editor wrap.

Seven precondition lines are added, including three assertions. Static parsing of
the corrected method and AST comparison passed: all eight original assertion calls
remain and the corrected method has eleven. The remaining method body is unchanged
when the insertion is removed. Ten forward/nine reverse button visits, strict
focus/local visibility, scroll checks, viewport coverage, errors and mutations
assertions are retained. Wrapping is not disabled and button focus is not forced.

The assembled-Admin method and full suite were not executed during this preparation;
these static checks are not a test pass. Existing CI discovers the corrected test.
This mixed test/documentation commit omits [skip ci] for normal push-triggered CI;
no separate dispatch or unobserved run status/result is claimed. Application code,
user behaviour and workflows remain unchanged.

Open action: run/review covering local and CI evidence for the corrective commit,
verify the three viewport subtests and full suite/audit pass, then resolve the
validation exception. The known failed results remain historical failure evidence,
not validation of this unverified correction. Earlier 009.4/012 results are not 013
evidence. See [implementation, reviewed evidence and limits](../handover/320-initiative-keyboard-navigation.md).
