# 590 - Monster source workstream (SG-TODO-016/017)

[Back to HANDOVER index](../../HANDOVER.md) · [016 task](../todo/160-source-based-monster-selection.md) · [017 task](../todo/170-open5e-monster-source.md) · [delivery sequence](../todo/115-admin-delivery-sequence.md#source-integration-workstream-investigate-before-fixing-internal-order)

## Stage 3 accepted close-out - 2026-11-13

SG-TODO-016 / Stage 3 is completed and closed for the agreed source/catalog/
dropdown scope after the user's explicit request "Proceed with final acceptance
and close out SG-TODO-016" at 13:02 CET on 2026-11-13. Stage 2 / SG-TODO-017 was
already accepted and closed; Stage 1 was the recorded documentation-only feasibility
stage. The agreed three-stage workstream is complete. No further acceptance
request or implementation/publication/covering-CI action remains within its scope.

Stage 3 implementation 7e2579efcd3fc2833498edb1bc6e5093612cbc5e on
features/perplexity has successful Branch tests 43419501886 attempt 1,
job 131865652023; evidence publication 49822ee7cacfd3bc4e2bd520b98917aef036db2c,
directory ci-results-43419501886-attempt-1. Reviewed run.json/jobs.json agree on
branch, tested SHA, attempt and completed/success. All configured Chromium
provisioning, syntax/import, main Python/browser, pytest regression, JavaScript
and standalone browser/audit stages succeeded. Run completion:
2026-11-13T11:54:25Z (12:54 CET). Review did not individually re-review every test
log/screenshot or recount tests. Local counts/samples below are not new executions
or verified CI counts. No new authenticated live-server, human visual, screen-reader
or exhaustive catalog/accessibility verification is claimed by this close-out.

Accepted boundaries include D&D Beyond as name search only, None/manual entry,
configured 5e.tools sources and all Open5e documents when enabled, completeness/
failure distinctions, stale-choice protection and the agreed signed selection,
image/upload, empty-or-overwrite and species-identity rules. Older proposal and
CI/acceptance-pending language is historical and superseded, not reopened work.
009/009.7 and SG-TODO-019 remain closed. Deferred test-suite cleanup stays separate.

This close-out changes documentation only and uses [skip ci]. No application,
tests, templates, assets, pins, permissions or workflows change; no fresh tests or
separate dispatch, merge, deployment or release operation. No new close-out commit
SHA is invented before publication or future blanket write approval implied.

## Accepted plan and decisions - 2026-11-13

The accepted sequence was Stage 1 live feasibility/design (documentation only),
Stage 2 SG-TODO-017 Open5e/provider/settings integration, then Stage 3 SG-TODO-016
catalog selectors. User decisions: D&D Beyond excluded from the dropdown, retained
for name search; every Open5e document included, source shown on matching choices;
Open5e enabled by default; provider switches; name/statistics/image filled only when
empty or overwrite is ticked. A selected candidate sets species for signed identity.
The plan did not authorize unspecified future writes, merges or deployments.

Detailed original findings, URLs, licensing, payloads, source identities, all local
counts, screenshots, follow-ups and failures/corrections are preserved verbatim in
the [complete pre-close-out handover](https://github.com/dajomas/Scrying-Glass/blob/49822ee7cacfd3bc4e2bd520b98917aef036db2c/docs/handover/590-monster-source-workstream.md).
Existing section headings below preserve incoming links, including duplicate
Delivered behaviour / Validation anchors. Compact summaries do not delete evidence
or relabel historical failures as successful runs.

## Stage 1 findings - 2026-11-13

Dated live observations, not CI/fixture claims; full responses and references are
in the immutable record above. Open5e v2 document/name filtering, selected fields,
pagination and result validation informed the design; unsupported filters were
silently ignored. Per-document licences and mostly absent sampled illustrations
were recorded. 5e.tools can enumerate configured bestiary files. D&D Beyond uses
public HTML name search and was explicitly excluded from catalog enumeration.

### Open5e API (v2)

The original check saw 24 documents and 3,541 creatures, multiple name matches,
source-filtered lists and null illustrations in sampled creatures. The undocumented
page cap requires following next, not assuming a single page. These are dated
samples, not a new or perpetual exhaustive catalog guarantee. Full API references,
licence distinctions and image restrictions remain in the preserved record.

### Existing providers and code

The original combined lookup had two providers and a fail-closed/32-candidate bound.
Stage 2 generalized ordered lookup; Stage 3 adds a distinct full-catalog path.
The lookup candidate bound is not presented as a complete-catalog size limit.

## Proposed Stage 2 design (for review with the Stage 2 payload)

Historical proposals subsequently settled by accepted Stage 2 delivery, not open
decisions: default-on display.open5e_lookup, HTTPS display.open5e_base_url,
superadmin saved provider switches, ordered fail-closed candidate lookup,
field/bonus mapping, labels and exact retained identity. Refresh was initially
excluded pending agreement, then included after the user's "Yes include it if it
is enabled" decision. Earlier contradictory wording is superseded by that decision.

## Stage 3 notes

Accepted source options: None/default/manual, configured enabled 5e.tools sources,
then enabled Open5e documents with provider/document labels. All pages must load
and validate before a list is complete; fill-in follows the accepted rules.

## Stage 2 delivery - 2026-11-13

SG-TODO-017 is already accepted and closed, explicitly recorded in publication
7e2579efcd3fc2833498edb1bc6e5093612cbc5e. Final Stage 2 tested revision
e5227f423f21cb1d4ed6aa9ac59e40cbd6207f86 has successful Branch tests 43416936427
attempt 1, job 131857079482; evidence ff40ee72efaebf84a102f57a3904d7240e59eb5a.
The user's earlier "I accept stage 2 please close it and move on to the next item"
request remains its acceptance; this Stage 3 close-out does not reopen it.

### Delivered behaviour

Ordered D&D Beyond / 5e.tools / Open5e lookup retains fail-closed behavior and
32-candidate provider limits. Open5e v2 validates normalized names, document and
key identities, follows bounded same-host next links, maps AC/HP/explicit bonus
without invented values, and supplies document/publisher/licence attribution.
Configuration defaults Open5e on with an HTTPS base URL. Superadmin-only saved
provider switches override config; unreadable settings disable optional providers.
Refresh includes enabled Open5e and exactly re-resolves retained identities, or
reports Provider disabled, never silently substitutes. D&D Beyond book labels,
provider/book sorting, image availability, overwrite default, signed image picker
and Choose again/cancel-preservation follow-ups are preserved as delivered.

### Validation (local, 2026-11-13)

Complete local counts, live contract samples and follow-up ordering remain in the
preserved handover; they are not newly run or relabelled CI. Earlier successful
runs: 43398379138, 43402863879 and 43405683876. Failed 43408459349 on 6b92277d
remains a function-extraction fixture failure repaired by copying attribution
helpers. Failed 43411555344 on c92119d7 remains a script-inventory fixture failure
(44 versus 45 after image picker), repaired before final e5227f42 / green
43416936427. No historical failure or initial pending-acceptance statement overrides
that final covering run/acceptance. Earlier limits on Users-switch/Open5e attribution
browser coverage remain explicit in the full record, not silently claimed tested.

## Stage 3 delivery - 2026-11-13

Published and accepted as the Stage 3 implementation identified at the top.

### Delivered behaviour

- Admin-only python/scrying_glass_source_catalog.py routes: GET /api/monsters/catalog/sources, /monsters?provider=&source= and /monster?provider=&source=&id=. Unknown provider 400, disabled 409, unusable stats 404; incomplete/failing lists report error, not a guessed complete list.
- Sources: configured enabled 5e.tools sources, then enabled Open5e documents. D&D Beyond is not listed. Failed-provider availability is explicit.
- 5e.tools enumerates source entries; Open5e document_monsters follows/validates all pages/document keys and rejects duplicates. Single candidate detail is signed through the existing signing contract.
- static/monster-source-picker.js?v=1 adds labelled Source/Monster controls to Monster identity; None default, hidden dependent list for None, loading/empty/unavailable/complete states, generation guards, retry/manual guidance.
- Picking a monster fills Name if empty or overwrite is ticked, sets species to the signed candidate name and presets the normal lookup (monster-candidate-selection.js?v=10); existing statistics/image/upload/bonus behavior remains. Source/form/species changes invalidate the appropriate pick. Admin inventory is 46 scripts.

### Validation (local, 2026-11-13)

Recorded related tests: test_monster_source_catalog.py, test_monster_source_picker_browser.py,
image-preview/button-layout, Admin composition/asset-wiring, provider extraction and
related browser modules. Earlier recorded live samples: 30 sources (6 5e.tools,
24 Open5e), MM 450 monsters, srd-2014 325; Goblin selected from both providers.
A recorded 1440px screenshot placed selectors in Monster identity. These are local/
dated samples, not fresh final execution or universal live-catalog completeness.
Current hosted-CI run/job review and user acceptance are separately recorded above.

## Status

All three agreed workstream stages are complete: Stage 1 recorded feasibility/design;
Stage 2 / SG-TODO-017 accepted/closed; Stage 3 / SG-TODO-016 accepted/closed on
2026-11-13 at 13:02 CET. No agreed workstream implementation/CI/acceptance action
remains; no new scope/gates, owner/deadline or future blanket write approval.
