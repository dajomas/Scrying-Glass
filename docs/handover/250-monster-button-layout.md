# 250 - Single-line monster row controls

[Back to handover index](../../HANDOVER.md)

Date: 2026-11-03. Task: [SG-TODO-007](../todo/070-monster-button-layout.md).
Initial preparation base: `5bcc1cc99fd49615d38c9853951b8ec6424efd82`.
Initial delivery: `da8e7352fee0b504628aeed94aae6687341e2c35`.

## Decision and implementation

The user approved keeping all 13 monster-row buttons on one line and using
horizontal scrolling confined to the Monsters table when they do not fit.
The Display/status and HP change columns remain separate. Labels, state classes,
data attributes, handlers and DOM button order are unchanged. Creation forms,
bulk controls and character rows are unchanged. No operations are hidden.

`static/monster-button-layout.css` limits the table container to its available
width and prevents wrapping in its two action cells and button labels. The Admin
head loads that stylesheet. The existing `#monsters` container is a named region
with `tabindex=0`, a focus outline and an accessible scrolling hint. Tab continues
through selection, initiative and the 13 existing buttons; browser focus scrolling
can expose off-screen operations. This behavior still requires full-page evidence.

The user subsequently reported word-by-word wrapping of the name and species.
The initial change protected action cells but not the name column. The correction
adds `min-width: 16ch` and `white-space: nowrap` to column 2, preserving the explicit
break between name and species and leaving additional width in the local scroller.
The original button-only geometry tests missed this readability regression.

Selectors target name column 2 and action columns 6 and 7 of the existing monster
table only. If that structure changes, update the selectors and tests together.

## Source architecture and size policy

No Admin JavaScript source, tracked failure marker, assembly reader, adapter or
source identity assertion is changed. Live `020-source.js` was inspected at blob
`350f9b2b998a035ec17a5ab2f7840ae622430bba`. Existing live identity assertions
retain the 114,814-byte bundle and SHA-256
`40fca092f989bcd85eaf7f06dc02b962b662a28827864df68c998919cdf87b46`;
these assertions were read, not executed during this preparation.

New code files remain below 20,000 bytes. The agreed 25,000-byte tolerance for
existing code does not relax the native Admin reader's 20,000-byte fragment cap.
This change does not reconcile SG-TODO-008 records or alter SG-TODO-004's hold.

## Validation and remaining work

Initial preparation executed Python AST parsing and byte counts: 476-byte initial
CSS and 9,201-byte original browser module. Its three methods cover six geometry/
state cases (1440, 768, 375 pixels; active/inactive), Tab traversal at all three
widths, local scroll geometry and keyboard opening/closing of Edit and Restore
statistics. These methods were prepared, not executed here.

Corrective preparation executed AST parsing of a new 2,941-byte regression module.
It reuses the assembled-page intercepted-HTTP harness for six name/species cases,
including Crawling Claw and a longer name with the Ally suffix. The original
three methods remain intact. A separate simplified Chromium reproducer at 768
pixels observed species wrapping change from two lines to one, cell width from
97.375 to 174.375 pixels and table width from 1370.09375 to 1447.09375 pixels;
document width remained 768 pixels. This isolates the CSS issue but is not an
assembled-page, authenticated-server or deployed-interface test.

No full-page browser method, existing interaction regression, authenticated
server check or live-provider check was executed during these preparations.
No CI result is claimed. The normal workflow installs Chromium and discovers
both test modules through `tools/run_split_tests.py`; no workflow edit or skip
is requested. Review user-collected evidence against its exact SHA and attempt,
separately from deployed-interface acceptance. Task status remains in progress.

Deploy matching templates and the complete static tree, restart and reload the
browser. README and root indexes were reviewed and remain accurate for this
correction; the existing task and handover sections carry the regression details.
No unrelated backlog cleanup is included.
