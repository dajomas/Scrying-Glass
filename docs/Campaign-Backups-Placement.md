# Move Campaign backups into Campaign Setup

Requires the previously supplied Encounter features, tidied Encounter tools layout and logging
patches. This is a presentation-only overlay, not a standalone feature installation.

The existing Campaign backups detail panel is moved into #campaignInputPane on page load,
before features.js attaches its handlers. The DOM nodes are moved, not copied, so control IDs,
file input state and event listeners remain intact. Export/import still use the existing API.
Campaign backups now inherits the campaign pane's hide/show behaviour. The section remains
collapsed initially, as in the earlier tidy layout. A scoped stylesheet uses the campaign pane's
teal palette and lays export/import out side by side, stacking below 700px.

There is no Python, database, endpoint, permission, or port configuration change.
Existing templates/admin/020_battle_controls.html and static/features.js are not replaced.
The initial source markup remains in the earlier template; the new script relocates that exact
panel into Campaign Setup when the admin page loads. This avoids replacing the entire Encounter
tools fragment and accidentally overwriting prior layout work.

## Apply

1. Extract at the application root, retaining paths and overwriting the two included HTML fragments.
2. Restart Scrying Glass, since HTML fragments load at server startup.
3. Hard-refresh the admin browser. New script/stylesheet URLs are versioned.
4. Expand Campaign Setup > Campaign backups, and verify export/import.
5. Hide Campaign Setup and confirm its backups section is hidden too.

Keep the previously supplied static/encounter-tools.css, static/features.js, logging files and
all original campaign template files. The new head fragment retains the encounter-tools stylesheet
link; the ending fragment retains admin.js and features.js and adds the relocation script.
If you have customized those two fragments yourself, merge the new asset links instead of
blindly overwriting local edits.

## Validation

Node syntax check passed. Six DOM-contract tests passed: relocation of the same nodes,
idempotency, delayed DOM readiness, missing pane, missing panel and missing-control protection.
CSS block delimiters and archive integrity were checked. These use DOM substitutes, not a live
browser: rendering and live export/import have not been retested in this environment.

Run the focused test from the application root:

    node tests/test_campaign_backups_layout.js

Rollback: restore the prior two HTML fragments and remove the new script/style files. The
original backup markup is untouched, so it returns to Encounter tools on reload.
