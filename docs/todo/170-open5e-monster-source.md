# 170. Open5e API monster source

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-017
- Status: in progress - Stage 2 implementation delivered 2026-11-13 on features/perplexity; CI validation and user acceptance pending.
- Recorded: 2026-11-06
- Priority: not assigned; no change to the [agreed Admin delivery sequence](115-admin-delivery-sequence.md).
- Dependencies: verify the current Open5e API contract during implementation planning.
- Related tasks: [source-based monster selection](160-source-based-monster-selection.md), [source help text](140-monster-source-help-text.md), [image previews](110-monster-image-previews.md).

## Requested change

Add Open5e.com, accessed through its API, as a monster source in Scrying Glass.

## Proposed acceptance criteria

- Open5e monsters can be retrieved through the API and used in the Add Monster workflow.
- Supported monster fields map consistently to the application's monster model; missing data is handled explicitly rather than invented.
- Source attribution and distinct candidates remain identifiable when names overlap across providers or documents.
- API failures and empty results are distinguishable, with bounded requests and appropriate pagination handling.
- Existing D&D Beyond, 5e.tools and manual-entry workflows remain usable.
- Relevant source labels, configuration documentation and help texts reflect the delivered integration.

## Implementation decisions to resolve

Verify the supported API version, endpoints, available fields, document/source filtering, pagination, usage requirements and attribution/licensing requirements from current provider documentation. No specific API contract has been verified for this backlog entry.

Agree how Open5e is enabled and configured, its position (if any) in automatic fallback lookup, and how it participates in SG-TODO-016's source/monster dropdowns. Do not assume a new fallback order or default enablement from this request alone. Coordinate image handling with available provider data and SG-TODO-011.

## Validation required

Prepare provider and UI regression tests covering lookup, candidate selection, field mapping, missing data, pagination, empty results and provider failures. Verify representative live API responses separately from fixture-based tests and document any limits on catalog completeness or image availability.

## Accepted decisions - 2026-11-13

- All Open5e documents are included. When several options match, the source is shown with each choice.
- Open5e is enabled by default.
- Add toggles to enable or disable D&D Beyond, 5e.tools and Open5e search.
- Picking a monster fills in name, statistics and image only when those fields are empty or the overwrite check is ticked.

Stage 1 verified the v2 API contract against the live service: document filtering, field selection and pagination work; unsupported filters are silently ignored; no images were seen on sampled creatures; and content carries per-document licences. Details, configuration and toggle proposals and the candidate order (D&D Beyond, 5e.tools, Open5e) are in the [590 handover](../handover/590-monster-source-workstream.md). The proposals remain open for review with the Stage 2 payload.

## Delivery status

Stage 1 recorded 2026-11-13 (documentation only).

Stage 2 implemented 2026-11-13 on the proposed design the user approved for implementation ("Start Stage 2 on the proposed design"): Open5e v2 provider, ordered provider layer, `display.open5e_lookup`/`display.open5e_base_url`, and superadmin provider switches. Details, decisions and local results are in [590 Stage 2](../handover/590-monster-source-workstream.md#stage-2-delivery---2026-11-13).

Remaining for this task:

- CI results for the Stage 2 commit, then user acceptance.
- Refresh: decided by the user on 2026-11-13 ("Yes include it if it is enabled"). Open5e takes part in monster Refresh when its provider switch is enabled; a retained Open5e identity is re-resolved exactly and reports "Provider disabled" when Open5e is off.
- Name fill-in from a picked monster is delivered with the SG-TODO-016 dropdowns (Stage 3); Stage 2 keeps the existing AC/HP/initiative empty-or-overwrite rules and image snapshot behaviour.
