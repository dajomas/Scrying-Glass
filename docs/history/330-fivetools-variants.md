# 330 - 5e.tools monster versions and generated magic-item variants

[Back to history index](../../HISTORY.md) · [SG-TODO-022](220-admin-statblock-viewer.md) · [04e resolution](224-fivetools-statblock-resolution.md)

## Task and status

SG-TODO-033 - implemented 2026-11-22 on `features/claude`: part 1 monster versions ([handover 720](../handover/720-fivetools-monster-versions.md), CI 44960931606 green), part 2 generated magic-item variants ([handover 730](../handover/730-fivetools-magic-item-variants.md)); completed and closed 2026-11-22 after CI 44964454668 and e2e 20261122T073821Z (137 passed). The runtime's item type/property text was split off as [SG-TODO-034](340-fivetools-item-enhancement.md) by the user 2026-11-22. Decided 2026-11-21 (implementation group 4); proposed 2026-11-20, split off from SG-TODO-022 by the user's decision on 2026-11-20 so
that SG-TODO-022 can close without it. No owner, priority or deadline has been agreed.

## Scope

1. **Monster versions (`_versions`).** 5e.tools records can carry versions built on the
   base creature (for example lair versions or alternative builds). Find statblock offers
   only the base creature; discovery reports `omitted_versions` and the chooser says how
   many were left out. Needs version expansion in the 5e.tools adapter (the runtime's
   version generation, including variable substitution) and version candidates in
   discovery, labelled so they can be told apart.
2. **Generated magic-item variants (04e.2).** References to items that 5e.tools generates
   from `magicvariants.json` (for example "+1 Longsword") are `reference_unavailable`
   partial warnings: 55 of 4,683 real monsters at the 2026-11-17 measurement. Needs the
   runtime's specific/generic variant generation and item enhancement.

## Decisions (2026-11-21)

Implementation group 4 on `features/claude`. Measured in the pinned data
(5etools-src 32ef600): 85 monsters with `_versions` (286 basic versions, plus 1 template
version with 5 implementations) and 69 monsters whose `variant` entries carry `_version`
(77 versions); about 368 versions in total.

1. Delivery: one after the other, monster versions first, then magic-item variants (plan
   order agreed 2026-11-21).
2. Chooser: versions are grouped under their base creature: one entry for the base, with
   its versions in a sub-list opened under it, in 5e.tools order.
3. Matching: a version is found by its base creature's name (with the base) and by its own
   name (directly).
4. Original source: a monster whose 5e.tools link names a version uses that version as its
   original source (marked "original source" and auto-loaded like other originals).
5. Part 2 scope (2026-11-22): generate the generic and specific magic-item variants now,
   built like the runtime before `_enhanceItems`; the runtime's type/property text for all
   items becomes [SG-TODO-034](340-fivetools-item-enhancement.md).

## Open decisions as proposed (2026-11-20)

- How versions are labelled and ordered in the chooser, and whether a version can be the
  tracker's original source.
- Whether both parts are delivered together or one after the other.

## Acceptance criteria (proposed)

- Versions: every version of a matching creature is offered (no `omitted_versions` for
  supported cases) and prepares identically to the pinned 5e.tools runtime (oracle
  comparison, as for the other modes).
- Magic items: generated variants match the pinned `Renderer.item._createSpecificVariants`
  output for every referenced item, item text includes the runtime's property/type
  entries, and the partial count drops accordingly (04e.2 acceptance in TODO 224).
- Existing limits apply (`dataset_files`, reference and snapshot limits).

## Validation requirements

Oracle comparison against the pinned runtime for the affected real data, unit tests for
discovery and labels, browser test of the chooser. Changes to code or tests run CI
normally.
