# 180. Monster initiative bonus

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-018
- Status: proposed
- Recorded: 2026-11-06
- Priority: not assigned; existing delivery sequencing is unchanged.
- Dependencies: inspect current provider mappings, persistence and initiative assignment paths during implementation planning.
- Related tasks: [initiative keyboard navigation](130-initiative-keyboard-navigation.md), [source-based monster selection](160-source-based-monster-selection.md), [Open5e integration](170-open5e-monster-source.md).

## Requested change

Support a monster initiative bonus when adding a monster: pull it from the selected monster source where available or allow manual entry. Take the bonus into account when assigning initiative. Display the bonus in the Monsters roster between HP/Max HP and the Initiative edit box.

## Acceptance criteria

- Monster creation supports a separately stored initiative bonus, populated from source data where available and enterable manually.
- Source-derived values can be corrected manually; missing source data is not silently treated as a verified bonus.
- Initiative assignment accounts for the bonus exactly once, with clear distinction between a raw roll and a final initiative total.
- The roster displays the bonus between HP/Max HP and the Initiative edit box, with unambiguous signed formatting including zero and negative modifiers.
- The bonus persists across saving, reloading and supported encounter/setup reuse.
- Existing monsters remain usable after any required migration; existing initiative totals are not silently reinterpreted or modified.
- Shared/group initiative, tie handling and initiative keyboard navigation remain consistent with the agreed assignment semantics.

## Implementation decisions to resolve

Inspect how each provider represents initiative modifiers. Define behavior when an explicit initiative bonus is absent, including whether any derivation is allowed; do not assume the bonus always equals a Dexterity modifier.

Agree whether the Initiative edit box accepts a raw roll or a final total, how any existing automatic assignment uses the bonus, and how manual total overrides work. Specify defaults for legacy monsters and missing values before implementation. Coordinate provider mapping with SG-TODO-016/017 without making their delivery an assumed prerequisite.

## Validation required

Add provider, persistence and initiative regression coverage for explicit source bonuses, absent values, manual entry/override, positive/zero/negative modifiers, exactly-once application, legacy records and shared initiative. Manually verify creation, save/reload, assignment and roster placement, including Tab/Shift+Tab behavior.

## Delivery status

Backlog entry only. Implementation and validation remain outstanding.
