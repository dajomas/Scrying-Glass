# 330 - 5e.tools monster versions and generated magic-item variants

[Back to TODO index](../../TODO.md) · [SG-TODO-022](220-admin-statblock-viewer.md) · [04e resolution](224-fivetools-statblock-resolution.md)

## Task and status

SG-TODO-033 - proposed, split off from SG-TODO-022 by the user's decision on 2026-11-20 so
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

## Open decisions

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
