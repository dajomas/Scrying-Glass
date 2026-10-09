# Select all shortcuts

Adds a Select all button immediately left of the Bulk control in both Characters and Monsters.
Both existing dropdowns, including Select all and Unselect all, remain unchanged.
The buttons call the existing setAllSelected(kind,true) helper, updating selection sets AND
checkboxes so subsequent bulk operations see the correct IDs. They do not toggle/unselect,
change HP, or perform API writes. Selection is scoped to the appropriate current list.

This overlay targets the prior supplied patches. Existing admin.js, damage/logging logic,
Encounter tools controls and client page are not replaced. The new standalone script reuses
existing functions. Prior scoped CSS/script links are retained in the two header/footer
replacements. Merge those links if you have other local template customizations.

Install: extract at the application root, retaining paths; restart Scrying Glass because templates
load at startup; hard-refresh the admin page. No database or backend change.

On wider screens the button and dropdown remain grouped at the right of the heading, with the
button immediately before Bulk. On small screens the group wraps below the heading.

Validation: both dropdown option lists match the baseline exactly; each new ID is unique;
buttons precede their respective bulk controls. Node syntax check and seven focused tests passed
using the actual existing setAllSelected helper with DOM substitutes: character/monster scoping,
repeated clicks, stale ID cleanup, empty list, invalid kind and early click before data loads.
Archive integrity is verified. No live browser visual test was performed.

    node tests/test_bulk_select_all.js

Rollback: restore the prior four template fragments and remove the new script/style files.
