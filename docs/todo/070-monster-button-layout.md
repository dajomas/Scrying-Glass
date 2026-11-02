# 070 - Single-line monster buttons

[Back to TODO index](../../TODO.md)

## SG-TODO-007 - Restructure monster buttons into one line

- Status: proposed/requested; implementation and validation not started.
- Requested: 2026-11-02.
- Priority, owner and deadline: not assigned.

### Requested behavior

Restructure the monster buttons so they appear on a single line rather than
wrapping across multiple lines. This is a layout request, not removal or change
of any existing monster operation.

### Scope and design considerations

Inspect the current monster controls to identify the intended button group(s) and
representative viewport widths before implementation. The request does not define
whether this applies only to table-row controls or also other monster toolbars.
Choose and document a narrow-screen strategy without silently hiding, deleting,
disabling or changing labels/actions to force a single line. Any use of scrolling,
compact controls or overflow menus is a design choice still to be agreed.

### Acceptance and validation

- [ ] The agreed monster button group is displayed in one line at the agreed supported widths.
- [ ] All existing operations, state indicators, event bindings and statistics-restoration access remain available.
- [ ] Keyboard focus, accessible names and click targets remain usable.
- [ ] Narrow-screen behavior is deliberate and documented rather than accidental page overflow.
- [ ] Browser layout tests verify single-line geometry and representative narrow/wide viewports.
- [ ] Existing monster/battle/statistics interaction regressions remain green.

No runtime markup, styles or button behavior is changed by adding this task.
