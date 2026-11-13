# 333. Read-only monster roster initiative bonus

[Edit dialog](332-monster-initiative-edit-dialog.md) |
[Task SG-TODO-018](../todo/180-monster-initiative-bonus.md)

Updated: 2026-11-07. Incremental delivery; task remains in progress on
features/perplexity-018. No merge/write-back authorized.

## Covering baseline

Run 42356632966 attempt 1 reports success for exact tested commit
70b2b1339dfccff763e516ff789a0442f53acadf. Evidence folder
ci-results-42356632966-attempt-1 was read at publication commit
db2173dd36316dd9589beffeb07911f48e632118. All run.json test/audit/cleanup
steps report success. Individual log assertions/counts were not audited here.
This provides covering evidence after the Edit dialog serialization fix;
earlier failed runs remain failed, not relabelled by later evidence.

## Presentation-only increment

Adds a signed plain-text bonus column between HP and the existing Initiative
column for monsters only. Zero is shown as +0. Known assignment origin is exposed
in the cell title; values are not editable inline and no source evidence is
invented. Missing bonuses default to zero for legacy presentation. Invalid,
null or numerically unsafe values show Unavailable instead of a rounded number.
This is a view limitation, not a change to the server's stored integer range.

The module observes only table replacement at the monster container boundary.
It resolves rows by monster selection ID, stages additions before mutation, skips
unrecognized layouts and marks decorated tables to avoid duplicate columns.
Existing initiative inputs, Edit buttons, selections and character table are
retained. No network requests or application-state mutation are introduced.
The existing HP-change-column layout addon remains compatible in local fixtures.
Split Admin sources, API, storage and workflows are unchanged; normal CI applies.

## Executed checks and limits

Node syntax validation passed. Both real Chromium fixture methods passed locally
in 1.625 seconds, including widths 375 and 1440, positive/negative/explicit/default
zero, unavailable values, preserved input identity/selection/state, redraw,
character isolation and missing/unrecognized containers. The exact existing
combatant-row-layout.js blob was verified before running it with the new module.
An initial Python fixture quoting error was repaired before either browser method
executed; the final test module parses and both methods passed.

These are isolated markup/browser presentation checks, not assembled Admin/CSS
visual acceptance, authenticated HTTP/storage/restart or active-order validation.
No new-stage full-suite/CI result is claimed. Existing Initiative still has its
legacy final-total edit semantics; it is not labelled as a raw roll by this stage.
Next integrate raw-roll transport and separate-total UI together, preserve keyboard
navigation and active-order/turn/round/ties, then finish source-refresh and all
remaining agreed acceptance before SG-TODO-018 completion.
