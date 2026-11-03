# 250 - Single-line monster row controls

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-03. Task: [SG-TODO-007](../todo/070-monster-button-layout.md).
Initial delivery: da8e7352fee0b504628aeed94aae6687341e2c35.
Name correction: 49aed0cbf074d63930ce29a8d64ef2d9cc970226.
Current corrective preparation base: aff0ff459a2aae1e8f4301c40d162097068a711d.

## Decisions and delivered history

The user agreed one-line monster controls and table-local horizontal scrolling.
The initial 13-button implementation left name/species wrapping word by word;
the name correction protected column 2 with min-width:16ch and nowrap while
retaining their explicit line break. The user subsequently requested removal of
Damage and Heal from both combatant rows. The current scope is 11 monster-row
buttons and removal of both HP change columns, preserving alternate workflows.

## Corrective implementation

`static/combatant-row-layout.js` loads deferred after the other Admin modules.
Following the separate Admin enhancement pattern, it normalizes both rendered
tables: find the HP change header, verify each body cell contains only the two
known per-row HP buttons, then remove the header and matching cells from the DOM.
A childList observer watches each container's direct table replacement by load().
It does not watch its own nested cell removals, avoiding an observer loop. Initial
normalization also handles a load that completed before the module executed.
Installation is guarded against duplication. No encounter/API mutation occurs.

This deliberately leaves the legacy core renderer templates and HP handlers
unchanged; the loaded enhancement removes their obsolete rendered columns rather
than deleting core source or hiding controls with CSS. Missing the new script
would restore the legacy controls, so deploy matching templates and the complete
static tree, restart and reload browsers. The module fails closed if a future HP
column gains another button; revisit its validation and tests if that layout changes.

On Monsters focusin, the module adjusts only that container's scrollLeft when a
focused control crosses the visible client area, with a small focus-ring margin.
This handles partially visible controls that native keyboard scrolling left
clipped. It does not move focus or alter handlers/order. Character layout beyond
HP-column removal, forms, bulk toolbars and other HP workflows are unchanged.

The scoped CSS protects name column 2 and remaining action column 6. The original
region name, keyboard access, hint and focus outline remain.

## Source architecture and size

The eight Admin source fragments, tracked failure marker, assembly reader and
static adapter are unchanged. The assembled core remains 114,814 bytes, expected
SHA-256 40fca092f989bcd85eaf7f06dc02b962b662a28827864df68c998919cdf87b46.
Existing identity, UTF-8, ordered assembly, syntax and runner-isolation tests are
retained unchanged; no claim that they were rerun locally. No source fragment is
loaded independently. The new standalone module is 2,125 bytes; the updated
browser module is 10,940 bytes, below the agreed code limits. The native reader's
20,000-byte fragment cap is not relaxed. SG-TODO-008 cleanup and SG-TODO-004's hold
remain untouched. README and root indexes were reviewed and remain accurate;
these existing task/handover sections carry the corrective scope and evidence.

## CI diagnosis

Run 41641117462 attempt 1 tested 49aed0cbf074d63930ce29a8d64ef2d9cc970226.
Evidence commit aff0ff459a2aae1e8f4301c40d162097068a711d, folder
ci-results-41641117462-attempt-1. Reader index maps workflow.log to file-000007.
Parts 76-78 show three viewport failures at the keyboard test's line 143; the
1,015-test suite failed. Parts 104-105 show the connection audit repeating the
same suite/failures, not a separate connection leak: 673 opened, zero without
explicit close. Part 78 reports 43 pytest passes. Run metadata reports successful
syntax/import and JavaScript steps. Parts 106-107 show later audit/smoke completion.
The failed run is not acceptance and does not validate the new correction.

## Preparation checks and remaining validation

Node --check passed for the exact new module; Python AST parsing passed for the
updated four-method browser module. A simplified real-Chromium fixture exercised
the exact module at 1440, 768 and 375 pixels: both HP columns removed across three
refresh cycles per width, 11 forward and 10 reverse focus checks per width passed.
Document width did not increase (1440->1440, 768->768, 540->430). The simplified
narrow fixture's preexisting Character-table overflow is outside the monster
scroll assertion. An initial whole-document-equals-viewport assertion failed on
that fixture; the revised check measures newly introduced overflow instead.

The full-page intercepted-HTTP browser tests retain name readability, state
labels, geometry, ancestor-overflow and Edit/Restore keyboard regressions, and
add refreshed-table removal, idempotence and Battle Actions damage/heal choices.
The strict focused-button visibility assertion remains and covers both traversal
directions. Desktop need not overflow if all remaining controls fit; narrower
widths must use the local scroller. Full assembled-page tests were not executed
here. New CI, individual assertion results and authenticated/deployed validation
remain pending. Normal push-triggered CI is requested, with no skip or workflow
configuration change. User-collected evidence must identify tested SHA and attempt
before task completion is considered.
