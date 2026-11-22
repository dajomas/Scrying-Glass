# 750 - 5e.tools item type and property text (SG-TODO-034)

[Back to HANDOVER index](../../HANDOVER.md) · [Task 340](../todo/340-fivetools-item-enhancement.md) · [730 - magic-item variants](730-fivetools-magic-item-variants.md)

On `features/claude`, 2026-11-22, after the five planned groups closed. User decisions: show
the text "as 5e.tools"; property text, type text and weapon mastery; not the rarity-based
value (details in task 340).

## Changes

- `python/scrying_glass_fivetools_items.py`: `ItemReference` and `enhance_item`, a port of
  `Renderer.item.enhanceItem` (style "one") limited to the parts in scope. The lookups follow
  the runtime: lower-case abbreviation and source with the PHB alias for sourceless
  references, and the `itemType` internal copies of items-base.json (`_meta.internalCopies`,
  copied by abbreviation; for example the Airship type gets the Ship type's text). The added
  text is kept in `_fullEntries` and `_fullAdditionalEntries` as runtime `wrapper` entries.
- `python/scrying_glass_fivetools_collector.py`: every resolved item definition is enhanced;
  item groups get `_isItemGroup` (the ERLW arcane-focus rule needs it); the reference is
  built once per preparation from items-base.json. A failure restores the stored item and
  adds the partial warning `item_text_unavailable`. `_fullAdditionalEntries` is scanned for
  references.
- `python/scrying_glass_fivetools_preparation.py`: item definitions show
  `_fullAdditionalEntries` when present.
- `python/scrying_glass_fivetools_nodes.py`: `wrapper` entries render their `wrapped` or
  `wrappeds` in place, as `Renderer._recursiveRender` does. Before, a wrapper became an
  empty entry, which also hid SG-TODO-033's base-item note on generated variants.
- `tools/fivetools_oracle/item_oracle.mjs`: also enhances every item, item group, base item
  and generated variant and writes the in-scope result (`enhanced`). items.json is loaded
  once: a second `DataUtil.loadJSON` of the same file returns it without its copies merged.
- `tools/fivetools_oracle/compare.py items`: compares the port with that output. Where the
  site builds `_fullEntries` only to add the out-of-scope item lists (56 item groups, 218
  generic variants), the filtered result equals the record's own entries, so an absent
  `_fullEntries` counts as the own entries.
- `tests/test_fivetools_item_enhancement.py`: 12 tests (lookups and type copies, each part
  and its order, fail-closed cases, wrapper rendering, preparation with and without the text).

## Evidence

- Oracle at the pinned runtime (`32ef600`): `compare.py items` enhanced 6,706 of 6,706
  identical; generic 230 and specific 3,513 variants and 90 item copies still identical;
  `copies` 1,161 and `versions` 368 identical.
- All 4,683 monsters of the pinned dataset prepared before and after: no errors; completeness
  unchanged (4,682 available, 1 partial for the known missing legendary group); warnings
  unchanged. 131 of the 283 monsters with item definitions show more item text.
- Size: the tool note links `{@variantrule Tool Proficiencies|XGE}`, whose text links every
  tool, so the 38 monsters with a tool definition gain 27-34 tool definitions (+100 to
  +404 KB). Largest snapshot 1,034,860 bytes (limit 2 MiB; before 660,081); largest node
  count 5,111. No limit is reached. This is the same link the site shows.
- Full unittest suite here: 2,170 tests, the same 92 known FastAPI failures (compared module
  by module with HEAD); connection audit counts identical to HEAD; Node tests unchanged.

## Notes

- Statblocks prepared earlier keep their old item text until they are prepared again
  (Refresh from source); the adapter version is unchanged, as for SG-TODO-033.

## Close-out - 2026-11-22

Delivered in 12fa87e (with the separate run_e2e.sh push fix 60d5d40). Closed at the user's
request: CI 45018908380 green; e2e 20261122T160750Z: 136 passed, 0 failed, 1 not run (`test_global_success_clears_after_five_seconds[firefox]`: its server did not start because the e2e setup gave two listeners the same port, fixed in f5dc0d6). The run tested b22ce69, the CI publish commit on top of 12fa87e.
