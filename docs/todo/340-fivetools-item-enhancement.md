# 340 - 5e.tools item type and property text

[Back to TODO index](../../TODO.md) · [SG-TODO-033](330-fivetools-variants.md) · [04e resolution](224-fivetools-statblock-resolution.md)

## Task and status

SG-TODO-034 - proposed 2026-11-22, split off from SG-TODO-033 part 2 by the user's decision
(scope "generate variants now"). No owner, priority or deadline has been agreed.

## Scope

The pinned runtime runs every item through `Renderer.item.enhanceItem` (js/render.js,
`_enhanceItems`), which builds `_fullEntries` with the item's type and property entries
(for example the text of the Versatile or Finesse property, or a weapon type's additional
entries) and adjusts rarity values. Scrying Glass shows item definitions from the item's own
`entries` (and, for generated variants, the runtime's pre-enhancement `_fullEntries`), so
this text is missing for every item definition, not only for generated ones.

## Open decisions

- Whether item definitions should show the runtime's enhanced text at all (all item tooltips
  change).
- Which of `enhanceItem`'s parts are wanted (type entries, property entries, mastery,
  rarity value).

## Acceptance criteria (proposed)

- Enhanced items match the pinned runtime's `enhanceItem` output for every item a real
  monster references (oracle comparison, as for SG-TODO-033).
- Existing limits apply.
