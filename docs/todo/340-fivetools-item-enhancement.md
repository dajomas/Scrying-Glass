# 340 - 5e.tools item type and property text

[Back to TODO index](../../TODO.md) · [SG-TODO-033](330-fivetools-variants.md) · [04e resolution](224-fivetools-statblock-resolution.md) · [Handover 750](../handover/750-fivetools-item-enhancement.md)

## Task and status

SG-TODO-034 - proposed 2026-11-22, split off from SG-TODO-033 part 2 by the user's decision
(scope "generate variants now"). Started 2026-11-22 on `features/claude` at the user's
request ("continue with the final two items"). Delivered 2026-11-22 (12fa87e). Completed and
closed 2026-11-22 at the user's request: CI 45018908380 green; e2e 20261122T160750Z: 136 passed, 0 failed, 1 not run (`test_global_success_clears_after_five_seconds[firefox]`: its server did not start because the e2e setup gave two listeners the same port, fixed in f5dc0d6).

## Scope

The pinned runtime runs every item through `Renderer.item.enhanceItem` (js/render.js,
`_enhanceItems`), which builds `_fullEntries` with the item's type and property entries
(for example the text of the Versatile or Finesse property, or a weapon type's additional
entries) and adjusts rarity values. Scrying Glass showed item definitions from the item's own
`entries` (and, for generated variants, the runtime's pre-enhancement `_fullEntries`), so
this text was missing for every item definition, not only for generated ones.

## Decisions (user, 2026-11-22)

- Item definitions show the enhanced text, as 5e.tools does.
- Parts in scope: property text, type text (heavy/medium/light armor Stealth and Strength
  lines, spellcasting-focus notes, tool notes, type entries and the additional type entries)
  and weapon mastery.
- Not in scope: the rarity-based suggested value, the "Base items" and item-group lists
  (`magicvariant` entries), `additionalSources`, and the baked `_textTypes`/`_attunement`
  fields.

## Delivered

- `python/scrying_glass_fivetools_items.py`: `ItemReference` (the runtime's property, type,
  additional-type-entry and mastery lookups, with the PHB fallback aliases and the
  `itemType` internal copies of items-base.json) and `enhance_item` (`enhanceItem`, style
  "one", the parts above in the runtime's order). Unsupported data (an `entriesTemplate`, a
  mastery without source, an unknown mastery, a type copy with `_mod`) fails closed.
- Collector: every resolved item is enhanced; item groups are marked as the runtime marks
  them. If the text cannot be built the item keeps its own text and the snapshot is partial
  (`item_text_unavailable`).
- Definitions show `_fullAdditionalEntries` in place of `additionalEntries`; the node builder
  renders `wrapper` entries in place, as the runtime does (this also shows SG-TODO-033's
  base-item note, which was an empty entry before).

## Acceptance criteria

- Enhanced items match the pinned runtime's `enhanceItem` output: `compare.py items`, all
  6,706 items identical in the parts in scope (met).
- Existing limits apply: no real monster becomes partial or exceeds a limit (met; see
  handover 750 for the size effect of the tool note).
