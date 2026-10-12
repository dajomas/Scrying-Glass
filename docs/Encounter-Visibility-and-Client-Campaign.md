# Encounter tools visibility and client campaign label

Documented baseline: `features/development` at `4f401b4adfca92e9c9599aea8924c14efb49aea4`.

## Encounter tools

A Show/Hide encounter tools button is available to the existing admin pane-control bar, outside
Encounter tools so it remains available when the tools are hidden.

- Hidden by default on a new page load; CSS suppresses the initial content flash.
- On a server-confirmed battle start (battle_round > 0), save the current visibility and show it.
- The user can show/hide it during the battle. Next/HP edits do not repeatedly force it open.
- On server-confirmed End battle or Reset All (battle_round becomes 0), restore the saved value.
- Starting again snapshots the current pre-battle visibility, not an older battle's value.
- An empty initiative order alone is not treated as End battle: the tools remain in battle mode
  until round state ends, preserving controls if all combatants die.

The controller is per page/tab and updates through the existing admin load() state-refresh path.
It does not persist preferences across reloads. Opening/reloading during an ongoing battle shows
the tools; absent a pre-battle snapshot in that new page, the default restored value is hidden.
Only successful state responses cause transitions. This does not introduce a new cross-admin
real-time polling loop; other admins' changes are reflected when this page next reloads state.

This control is independent of the older automatic hiding of campaign/monster input panes.
The moved Campaign backups section remains in Campaign Setup and is unaffected by hiding tools.

## Client status bar

The leftmost element shows Campaign: <current name>. Connection/synchronization status and
logout remain to the right. Long names wrap on narrower screens without covering the encounter.

Only campaign ID and name are added to the existing player-safe display_state payload. Campaign
descriptions, account data and GM notes are not exposed. The label is set via textContent, not
HTML, including for names containing special characters. Missing active campaign displays
No active campaign. Switching campaigns updates via existing snapshots; renaming the active
campaign broadcasts an updated snapshot too.

The client replacement preserves existing effects/down-state rendering and revision/ping/ack
handling. The admin replacement preserves Details-column logging, critical-hit controls and
corrected downed-character turn selection from prior patches.

