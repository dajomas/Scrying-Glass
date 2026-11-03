# 070 - Single-line monster buttons

[Back to TODO index](../../TODO.md)

## SG-TODO-007 - Restructure monster buttons into one line

- Status: in progress; implementation prepared for delivery, CI and user validation pending.
- Requested: 2026-11-02. Scope approved: 2026-11-03.
- Priority, owner and deadline: not assigned.

### Agreed behavior and implementation

Keep all 13 per-monster row buttons on one horizontal line across the existing
Display/status and HP change cells. Preserve labels, state indicators, handlers,
accessible names and keyboard access. Monster-creation forms, the bulk toolbar
and character rows are outside this change.

The user explicitly approved horizontal scrolling confined to the Monsters table
when needed. Do not shrink controls excessively, hide actions in overflow menus
or allow the table to widen the whole page. The scoped stylesheet prevents
wrapping in the two action cells; the existing table container becomes a named,
keyboard-focusable scroll region with an accessible scrolling hint. No Admin
JavaScript fragment or event handler is modified.

### Acceptance and validation

- [ ] Browser evidence verifies all 13 buttons on one line at 1440, 768 and 375 pixels.
- [ ] All existing operations, state indicators, event bindings and statistics-restoration access remain available.
- [ ] Keyboard focus, accessible names and click targets remain usable.
- [x] Narrow-screen strategy explicitly agreed: table-local horizontal scrolling.
- [ ] Browser evidence verifies the table does not widen its ancestors.
- [ ] Existing monster/battle/statistics interaction regressions remain green.
- [ ] User acceptance on the deployed interface.

Prepared tests: `tests/test_monster_button_layout.py` contains three browser
methods covering active/inactive labels and indicators, single-line geometry,
table-local overflow, sequential Tab/Shift+Tab access and keyboard activation of
Edit and Restore statistics. These use the assembled Admin page with intercepted
HTTP, not an authenticated deployed server. Existing interaction regressions
remain configured in normal CI; no CI workflow changes or skip are requested.

Preparation checks executed: Python AST parsing of the new test module and byte
counts of the new code files (476-byte CSS; 9,201-byte test module). No browser
method or existing regression was executed during this preparation. CI execution,
individual assertion results and authenticated/live-server validation remain
separate and pending. Do not mark this task completed solely after a push.

Run with the disposable assembled-source runner:

```bash
python tools/run_split_tests.py -- python -m unittest discover -s tests -p 'test_monster_button_layout.py' -v
python tools/run_split_tests.py -- python -m unittest discover -s tests -p 'test_*.py' -v
python tools/run_split_tests.py -- node --test tests/statistics-restoration.test.cjs
python tools/run_split_tests.py -- node --test tests/battle-action-apply.test.cjs
```

After normal CI, the user collects and commits evidence with `getworkflow.sh`
and supplies the run ID, tested SHA, evidence commit and folder for review.
See [implementation handover](../handover/250-monster-button-layout.md).
