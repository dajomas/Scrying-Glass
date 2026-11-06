# 160. Source-based monster selection

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-016
- Status: proposed
- Recorded: 2026-11-06
- Priority: not assigned; no change to the [agreed Admin delivery sequence](115-admin-delivery-sequence.md).
- Dependencies: source-catalog enumeration feasibility must be established during implementation planning.
- Related tasks: [source configuration](060-fivetools-source-configuration.md), [image previews](110-monster-image-previews.md), [source help text](140-monster-source-help-text.md).

## Requested change

In the Add Monster panel's Monster identity section, add a source dropdown containing None (selected by default), D&D Beyond, and each configured 5e.tools source as an individual option. When a source other than None is selected, show another dropdown containing all available monsters from that source.

## Acceptance criteria

- The source dropdown appears in Monster identity and defaults to None.
- D&D Beyond and the individually configured 5e.tools sources are selectable, with clear source labels.
- Selecting a source displays and populates the dependent monster dropdown with all available monsters from that source, not merely matches for a typed monster name.
- Changing the source clears the previous monster selection and prevents stale results from a previous source appearing in the new list.
- Returning to None removes the dependent monster dropdown and leaves the existing manual/name-based entry workflow usable.
- Loading, empty-source and failure states are distinguishable; an incomplete or failed catalog load must not be presented as a complete list.

## Implementation questions and feasibility

Verify how complete monster catalogs can be enumerated for each provider, including pagination, source filtering and access restrictions. No catalog API or complete enumeration capability has been verified for this task. If a provider cannot supply the requested complete list through an acceptable mechanism, record the blocker and obtain agreement before narrowing scope.

Define the effect of choosing a monster on identity, statistics and image fields before implementation; the request specifies the two selectors but not the exact field-population or overwrite behavior. Coordinate with existing lookup and image-preview workflows. This backlog entry does not request account authentication, entitlement bypass or changes to the automatic fallback order.

## Validation required

Add relevant provider and UI regression coverage for default None, configured source options, source-specific lists, pagination where applicable, source switching, stale responses, empty catalogs and failures. Manually verify the selectors in Monster identity and preservation of manual entry. Verify live catalog completeness separately from fixture-based tests before claiming all available monsters are listed.

## Delivery status

Backlog entry only. Provider feasibility, implementation and validation remain outstanding.
