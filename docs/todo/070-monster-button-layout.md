# 070 - Single-line monster buttons

[Back to TODO index](../../TODO.md)

## SG-TODO-007 - Restructure monster buttons into one line

- Status: in progress; initial implementation delivered, name-column correction prepared; CI and user validation pending.
- Requested: 2026-11-02. Scope approved: 2026-11-03.
- Priority, owner and deadline: not assigned.
- Initial implementation: `da8e7352fee0b504628aeed94aae6687341e2c35`.

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

The user reported word-by-word monster-name/species wrapping after the initial
implementation on 2026-11-03. The corrective stylesheet protects column 2 with
`white-space: nowrap` and `min-width: 16ch`; the existing explicit break between
name and species remains. Extra width belongs inside the table-local scrollbar.

### Acceptance and validation

- [ ] Browser evidence verifies all 13 buttons on one line at 1440, 768 and 375 pixels.
- [ ] Monster name and species each occupy their own unwrapped line, including long names and the Ally suffix.
- [ ] All existing operations, state indicators, event bindings and statistics-restoration access remain available.
- [ ] Keyboard focus, accessible names and click targets remain usable.
- [x] Narrow-screen strategy explicitly agreed: table-local horizontal scrolling.
- [ ] Browser evidence verifies the table does not widen its ancestors.
- [ ] Existing monster/battle/statistics interaction regressions remain green.
- [ ] User acceptance on the deployed interface.

`tests/test_monster_button_layout.py` contains three browser methods covering
active/inactive labels and indicators, single-line geometry, table-local overflow,
sequential Tab/Shift+Tab access and keyboard activation of Edit and Restore
statistics. `tests/test_monster_name_layout.py` adds six name/species cases using
the same assembled-page intercepted-HTTP harness, without duplicating inherited
test methods. Neither fixture is authenticated deployed-server validation.

Initial preparation executed AST parsing and byte counts (476-byte initial CSS;
9,201-byte original test module), not the browser methods or interaction suite.
Corrective preparation executed AST parsing of the new 2,941-byte test module and
a simplified Chromium layout reproducer at 768 pixels: species changed from two
lines to one, with document width remaining 768 pixels. This reproducer is not
the assembled application and does not establish full-page regression success.
No full-page browser test, existing interaction regression or CI evidence has
been reviewed for this task. Normal CI remains enabled; no skip is requested.

Run with the disposable assembled-source runner:

```bash
python tools/run_split_tests.py -- python -m unittest discover -s tests -p 'test_monster*layout.py' -v
python tools/run_split_tests.py -- python -m unittest discover -s tests -p 'test_*.py' -v
python tools/run_split_tests.py -- node --test tests/statistics-restoration.test.cjs
python tools/run_split_tests.py -- node --test tests/battle-action-apply.test.cjs
```

After normal CI, the user collects and commits evidence with `getworkflow.sh`
and supplies the run ID, tested SHA, evidence commit and folder for review.
Do not mark this task completed solely after a push. See
[implementation handover](../handover/250-monster-button-layout.md).
