# Encounter tools visibility and client campaign label

Overlay for the prior Encounter features, logging, layout, backup-placement and corrected-damage
patches. Those patches must already be installed. No database schema or two-port change.

## Encounter tools

A Show/Hide encounter tools button is added to the existing admin pane-control bar, outside
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

This new control is independent of the older automatic hiding of campaign/monster input panes.
The moved Campaign backups section remains in Campaign Setup and is unaffected by hiding tools.

## Client status bar

The leftmost element now shows Campaign: <current name>. Connection/synchronization status and
logout remain to the right. Long names wrap on narrower screens without covering the encounter.

Only campaign ID and name are added to the existing player-safe display_state payload. Campaign
descriptions, account data and GM notes are not exposed. The label is set via textContent, not
HTML, including for names containing special characters. Missing active campaign displays
No active campaign. Switching campaigns updates via existing snapshots; renaming the active
campaign now broadcasts an updated snapshot too.

The client replacement preserves existing effects/down-state rendering and revision/ping/ack
handling. The admin replacement preserves Details-column logging, critical-hit controls and
corrected downed-character turn selection from prior patches.

## Apply

1. Stop the service and back up the affected files/storage.
2. Extract at the application root, preserving paths.
3. Restart the service because templates and Python changes load at startup.
4. Hard-refresh both admin and client pages.

The head/footer replacements retain the prior encounter-tools CSS, campaign backup CSS/script,
damage-preview helper and features.js. If these templates have other local changes, merge the
new links/control instead of blindly overwriting those local edits.

## Manual smoke checks

- On idle page load, tools hidden and Show button available.
- Start with tools hidden: show during battle, restore hidden after End and after Reset All.
- Start with tools visible: hide during battle, restore visible after End/Reset All.
- Toggle during battle and press Next: preserve that temporary choice until battle ends.
- Test successive battles and page reload during a battle.
- Check client label before battle, after campaign switch, and after active campaign rename.
- Try a long campaign name and a name with angle brackets; confirm readable text, not markup.

## Validation

10 Node visibility state-machine tests passed (defaults, manual toggle, transitions, restoration,
repeated updates, empty order, successive battles and reset behaviour). Six Python tests passed
for display payload ID/name, privacy, missing campaign, error propagation and rename notification.
Node VM checks passed for label changes, literal-text handling and empty campaign.
Changed Python files compile; changed/new JS passed node --check. ZIP integrity is verified.
These are targeted logic tests, not a live browser visual or HTTP/WebSocket integration run.
The entire feature regression suite has not been rerun for this UI/payload overlay.

    node tests/test_encounter_visibility.js
    python -m unittest discover -s tests -p 'test_client_campaign.py'

Rollback: restore prior replacement files and remove new controller assets/test files. No
database rollback is required.
