# 150. Battle Actions combatant statistics

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-015
- Status: proposed
- Recorded: 2026-11-06
- Priority: not assigned; no change to the [agreed Admin delivery sequence](115-admin-delivery-sequence.md).
- Dependencies: none established.

## Requested change

In the Battle Actions modal, when a target is selected, show its AC, current HP and HP MAX below the target dropdown, where those values are available. Show the same information below the Reaction source dropdown for the selected Reaction source.

## Acceptance criteria

- The selected target's available AC, HP and HP MAX appear immediately below its dropdown.
- The selected Reaction source's available AC, HP and HP MAX appear immediately below its dropdown.
- Each summary updates when its selection changes and clears when no combatant is selected, without retaining another combatant's values.
- Missing values are not invented or displayed as zero; valid zero values remain visible.
- Summaries are read-only and do not change action/reaction resolution or combatant statistics.

## Validation required

Add or update relevant UI regression coverage for both selectors, selection changes, clearing selections, partially missing statistics and zero HP. Manually verify placement and readability in the Battle Actions modal for character and monster selections.

## Delivery status

Backlog entry only. Implementation and validation have not been performed for this task.
