# 250 - Single-line monster row controls

[Back to handover index](../../HANDOVER.md)

Date: 2026-11-03. Task: [SG-TODO-007](../todo/070-monster-button-layout.md).
Preparation base: `5bcc1cc99fd49615d38c9853951b8ec6424efd82`.

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
can expose off-screen operations. This behavior still requires browser evidence.

The selectors target columns 6 and 7 of the existing monster table only. If that
column structure changes, update the scoped selectors and layout tests together.

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

Preparation executed Python AST parsing of the new browser module and byte counts:
476-byte CSS and 9,201-byte test module. Three browser methods are prepared for
normal unittest CI discovery, using Playwright Chromium and intercepted HTTP
with the assembled Admin page. They cover six geometry/state cases (1440, 768,
375 pixels; active/inactive), Tab traversal at all three widths, local scroll
geometry and keyboard opening/closing of Edit and Restore statistics.

No browser test, existing interaction regression, authenticated server check or
live-provider check was executed here. No CI run or successful assertion result
is claimed. The normal workflow already installs Chromium and discovers the new
test filename through `tools/run_split_tests.py`; no workflow edit is needed.
Retain validation-pending task status until evidence is reviewed and acceptance
criteria are satisfied. User-collected CI evidence will be reviewed against its
exact tested SHA and attempt, separately from deployed-interface acceptance.

Deploy the matching templates and complete static tree, restart and reload the
browser. README was reviewed and left unchanged because its existing source and
deployment descriptions remain accurate; this section and the linked task carry
the new layout details. The root handover index gains this section; the TODO index
reflects work in progress. No unrelated backlog cleanup is included.
