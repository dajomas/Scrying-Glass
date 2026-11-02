# 190 - Restore statistics readability and affected-only display

[Back to handover index](../../HANDOVER.md)

Recorded: 2026-11-02. Related task: [SG-TODO-002](../todo/020-monster-damage-effects.md).

## Correction

The supplied screenshot showed inline labels/inputs wrapping into one unreadable
stream. Restore statistics now displays a semantic table with Statistic,
Original/base, Reduction and Effective columns. Only supported version-1 manual
reductions with a positive accumulated amount produce restore rows/options.
Effective zero is not treated as absence of a reduction. The original values in
this view are read-only; unaffected/unknown abilities are hidden. After restoration,
rows/options refresh, and no remaining reductions disables the restore controls
and shows an explicit empty message.

Original-score setup remains usable in a separate Edit original/base statistics
view. It deliberately shows all seven bases only when the GM requests that editor;
Back returns to affected-only restoration and discards unsaved base drafts. API,
tokens, health rules, persistence, schema version and attack controls are unchanged.
Restore still never heals or resurrects. Scoped CSS prevents the new layout from
changing other modals, supports narrow screens and explicitly honors hidden views.
The replacement template preserves Add statistics reduction in the attack toolbar.

## Validation actually executed for this correction

- `node --test tests/statistics-restoration.test.cjs`: exit 0, mocked DOM/fetch
  checks for filtering, one/multiple stats, selected/all restoration, zero Max HP,
  empty-state disabling, separate base editing, cancellation, stale errors,
  scope changes and focus return.
- `python -m unittest discover -s tests -p test_statistics_layout.py -v`: one
  Chromium test passed, with actual DOM/layout at widths 1000, 697 and 375 pixels.
  It verifies the screenshot example (only Max HP: 1 / 9 / 0), headings, no table
  overflow, cancellation, restoration/empty state, seven-input separate editor,
  drafts and campaign isolation. HTTP responses are intercepted fixture data;
  this is not an authenticated running application.

The browser harness initially used an unavailable remove_all_listeners API; it was
corrected to remove_listener and the complete test rerun successfully. No backend
suite, full application server, live authentication or CI was run for this UI-only
correction. Prior backend/attack counts remain historical evidence in section 180.

## Delivery

A small corrective overlay for the installed Attack-Statistics archive, not the
original baseline or the earlier Encounter tools archive. Complete replacement
JS/template and new scoped CSS are included, along with revised/new tests,
README/User Guide and complete indexed handover/TODO context. Apply project files
preserving paths, restart for the imported HTML fragment, and reload the browser.
No migration, file deletion or rename is required. Patch/ is supporting material,
not repository content to stage. No GitHub write or workflow status is claimed.

Remaining: verify appearance in the user's full running theme/deployment and
validate authenticated restoration end to end. The broader task remains open.
