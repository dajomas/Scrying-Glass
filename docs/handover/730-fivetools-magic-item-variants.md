# 730 - 5e.tools magic-item variants (SG-TODO-033 part 2)

[Back to HANDOVER index](../../HANDOVER.md)

Implementation group 4, part 2, on `features/claude`, 2026-11-22. Scope decided by the user:
generate the variants now; the runtime's item type/property text is
[SG-TODO-034](../todo/340-fivetools-item-enhancement.md).

## Before

55 of 4,683 real monsters (pinned data) were partial because of 45 references to items the
runtime generates from `magicvariants.json`: specific variants such as "+1 Shortsword" or
"Plate Barding" and generic variants such as "Vorpal Sword".

## Runtime behaviour reproduced (`Renderer.item`, js/render.js at 32ef600)

- `DataUtil.loadJSON` merges the internal `_copy` records of `magicvariants.json` (5 here);
  their source may be only in `inherits` (`SourceUtil.getEntitySource`).
- `_genericVariants_addInheritedPropertiesToSelf`, then `_createSpecificVariants` over
  `items-base.json` in file order: edition match (outside a VTT), `requires`/`excludes`,
  `packContents` skipped, and `_createSpecificVariants_createSpecificVariant` (name prefix,
  suffix and removal, injected entries, value/weight expressions, barding, property add and
  remove, vulnerable/resist/immune merge, fluff, generic back-link, linked loot tables, and the
  "base item can be found in …" note for non-core base items).
- `Renderer.applyProperties`/`applyAllProperties` with the runtime's quirks: modifiers apply
  in written order (the sort result is discarded), arrays are rebuilt but objects rewritten in
  place, so a nested entry keeps the first substitution for later variants; damage types in
  style "one" (the site default) are title case.
- Not ported: `_enhanceItems` (SG-TODO-034).

## Code

- New `python/scrying_glass_fivetools_items.py`: `generate_variants(base_data, variant_data)`
  and its helpers. Unsupported data fails closed (`ItemVariantError`): unknown property
  modifiers, expressions other than "number * / + number", unknown editions or damage types,
  base items from a non-core source without a known full name.
- `FiveToolsData`: keeps the base-item list in file order; on the first item lookup that
  misses, fetches `magicvariants.json` (now allowlisted), generates the variants once and
  indexes them by name and entity source. If generation fails, references stay unavailable as
  before.
- Item definitions use the variant's `_fullEntries` (inherited text and the note) when
  present, as the runtime renders it; reference collection scans it too.
- `python/scrying_glass_fivetools_resolution.py`: preserve rules per kind
  (`PRESERVE_KINDS`: monster as before; item and magicvariant keep `lootTables` and `tier`
  only when preserved, `DataUtil.item/magicvariant._MERGE_REQUIRES_PRESERVE`), and the entity
  source fallback to `inherits.source` for item and magicvariant identities. With the old rule
  13 of the 90 `items.json` copies differed from the runtime; now all 90 match.

## Evidence (pinned runtime, local checkout of 5etools-src 32ef600)

- `tools/fivetools_oracle/item_oracle.mjs` + `compare.py items`: 230 of 230 generic and
  3,513 of 3,513 specific variants identical in order, key order included; 90 of 90 item
  copies identical. Copies (1,161) and versions (368) unchanged.
- All 45 formerly missing references are generated; none collides with an existing item;
  one generated name (Stygian Spear|COA) occurs twice and is reported ambiguous, as for any
  duplicate.
- All real monsters prepared: partial 55 → 1. The remaining one, Umbraxakar|WDMM, misses
  its legendary group, unrelated to items.
- Generation takes about 1.5 s with a peak of about 11 MB, once per preparation that misses
  an item.

## Tests

- New `tests/test_fivetools_items.py` (10): property injection and modifiers, in-place
  rewriting, generic and specific variants, the non-core note, editions, requirements, loot
  tables, failing closed, the item preserve rule, and a preparation whose generated item is a
  full definition (and stays unavailable without `magicvariants.json`).
- Full unittest suite here: 2,157 tests, no new failures; Node tests as on HEAD; connection
  check clean. CI and the user's check pending.
