# 160. Source-based monster selection

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-016
- Status: in progress - Stage 1 (joint feasibility/design) recorded 2026-11-13; this task is Stage 3 of the accepted workstream and is not started.
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

## Accepted decisions - 2026-11-13

The user accepted the coordinated plan (Stage 1 feasibility, Stage 2 SG-TODO-017 provider layer, Stage 3 this task) and decided:

- D&D Beyond is **not** in the source dropdown because of how it is accessed. It remains available for name search only. This narrows the original "D&D Beyond" option by explicit agreement.
- Source options are None (default), each configured 5e.tools source and every Open5e document, each labelled with its source.
- Picking a monster fills in name, statistics and image only when those fields are empty or the overwrite check is ticked.

Findings and the proposed design are in the [590 handover](../handover/590-monster-source-workstream.md).

## Delivery status

Stage 1 findings recorded 2026-11-13 (documentation only). Implementation and validation are outstanding and depend on the Stage 2 provider layer. The Stage 2 layer (ordered providers, Open5e provider, provider switches) was delivered 2026-11-13 with CI pending; see [590 Stage 2](../handover/590-monster-source-workstream.md#stage-2-delivery---2026-11-13). Stage 3 is not started.
