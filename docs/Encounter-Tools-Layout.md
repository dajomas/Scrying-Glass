# Encounter tools layout

Documented baseline: `features/development` at `4f401b4adfca92e9c9599aea8924c14efb49aea4`.

Encounter tools shows viewer synchronization, Undo and a selected combatant overview, followed by expandable panels:

1. Health & survival: temporary HP, damage/healing, life state and death saves.
2. Conditions & concentration: source concentration, current effects and effect creation/duration.
3. Encounter checkpoints: save, preview/restore and delete.

Campaign backups is relocated to Campaign Setup on page load; it is not part of the visible Encounter tools panel. The top pane-control bar toggles tools; battle start/end temporarily changes visibility as described in [Encounter visibility](Encounter-Visibility-and-Client-Campaign.md).

The layout uses native details/summary elements, explicit labels and scoped `static/encounter-tools.css`. Panels use two columns on wider screens and one at 850px or below; compact rows stack at 480px or below. Lair tools are a separate pane assembled from `185_lair_tools.html` in the loader’s explicit order, not filename sort order.

Restart after fragment edits and reload the admin page after asset edits. Keep element IDs, script order and styles synchronized. See [User Guide](User-Guide.md) for functional workflows.
