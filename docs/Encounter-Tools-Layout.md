# Encounter tools layout update

Presentation-only overlay for the six-feature encounter patch supplied earlier.
Apply AFTER that feature patch. Keep its existing static/features.js and backend files.

## Contents

- templates/admin/020_battle_controls.html: replacement battle/encounter fragment.
  The original Battle controls are preserved. Encounter tools is reorganized below them.
- templates/admin/000_document_start.html: replacement head fragment, adding the scoped stylesheet.
- static/encounter-tools.css: new stylesheet. Existing static/admin.css is not replaced.

## Layout

The first view now shows connection status, Undo and the selected combatant overview.
Four clearly labelled expandable panels organize less-frequent operations:

1. Health & survival: temporary HP, damage/healing, life state, death saves.
2. Conditions & concentration: source concentration, current effects, effect creation/duration.
3. Encounter checkpoints: save and restore/delete, in separate groups.
4. Campaign backups: export and import, in separate groups.

All four panels are collapsed initially. Open only the tools you need. This uses native details/
summary elements, not a new JavaScript tab framework. Form labels sit above their fields,
associated buttons align beside them, and help text explains sign conventions and consequences.
On wider screens the panels use two columns; at 850px or below they use a single column.
At 480px or below compact input/action rows also stack. Keyboard focus indicators and explicit
labels are included. Potentially destructive actions use distinct outline styling.

## Apply

1. Stop/restart the service around installation because HTML fragments load at server import.
2. Extract the ZIP at the application root, retaining the folder paths and overwriting the two
   HTML fragments. The new stylesheet goes in static/.
3. Restart Scrying Glass.
4. Hard-refresh the administration page. The new CSS link also has a versioned query string.

No Python, JavaScript, API, database schema, authentication or network changes are included.
The two-port setup remains unchanged. Existing control IDs and form field types are retained,
so the previously supplied features.js continues binding to the same controls.
Existing static/admin.css and templates/admin/190_document_end.html must remain as installed
by the earlier feature patch (including the features.js script tag).

## Validation

Checked that every expected encounter control ID exists once; select/form/list element types
are preserved; explicit labels reference existing controls; no nested forms are present; all
four detail panels start collapsed; the original Battle fragment is retained unchanged; the
new stylesheet link is present; and CSS block delimiters are balanced.
ZIP contents and integrity are verified. This is structural validation, NOT screenshot or
browser-rendering validation: no live browser visual test was run in this environment.

## Rollback

Restore the two previous HTML fragments, remove the new stylesheet, restart, and refresh.
No database rollback is needed for this layout-only update.
