# Battle setup controls layout

The original inline control sequence is unchanged:

Battle setup name input → New → Save → Battle setup dropdown → Load → Rename → Delete

The **Has lair** checkbox occupies the next row, below the setup-name input
and the rest of this control sequence, and above the Import buttons.
No block-level row is inserted between the name input and New/Save controls.
The existing responsive layout can still wrap controls on narrow screens.

This corrects the layout only. Per-setup checkbox persistence, Lair-pane gating,
existing visibility rules, and the schema v7 migration are unchanged.

Regression check:

```sh
node --test tests/setup-input-layout.test.cjs
```
