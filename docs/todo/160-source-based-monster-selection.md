# 160. Source-based monster selection

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-016
- Status: completed and closed for the agreed Stage 3 scope on features/perplexity; explicit final user acceptance 2026-11-13 at 13:02 CET: "Proceed with final acceptance and close out SG-TODO-016".
- Recorded: 2026-11-06
- Priority: not assigned; no change to the [agreed Admin delivery sequence](115-admin-delivery-sequence.md).
- Dependencies: Stage 1 catalog feasibility and the accepted Stage 2 provider layer are satisfied for the delivered scope.
- Related tasks: [source configuration](060-fivetools-source-configuration.md), [image previews](110-monster-image-previews.md), [source help text](140-monster-source-help-text.md).

## Requested change

The original request was a source dropdown in Add Monster's Monster identity,
defaulting to None, and a dependent full monster list for the chosen source. It
originally named D&D Beyond and each configured 5e.tools source. The explicitly
accepted 2026-11-13 decisions below supersede that original provider list: D&D
Beyond stays name-search only; Open5e documents join configured 5e.tools sources.
Full original wording and then-open questions remain in the
[pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/49822ee7cacfd3bc4e2bd520b98917aef036db2c/docs/todo/160-source-based-monster-selection.md).

## Acceptance criteria

Completed/accepted for the agreed scope, not a new open checklist:

- Source appears in Monster identity and defaults to None.
- Each configured 5e.tools source and each Open5e document is labelled by provider/source; disabled providers are not offered. D&D Beyond is excluded by agreement and remains usable for name search.
- Choosing a source loads its full catalog, not merely typed-name matches. Open5e follows/validates all pages; incomplete/failing lists are not labelled complete.
- Changing source clears the prior monster pick and uses generation guards against obsolete responses. Returning to None hides the dependent list and preserves manual/name-based entry.
- Loading, empty, unavailable and complete-list states are distinguishable, with retry/manual guidance.
- Choosing a monster fills Name when empty or overwrite is ticked; sets Monster species to the signed candidate's name; statistics/image use the existing selection/preset rules. Form reset clears both selects; changed species invalidates the pick.
- Existing permissions, signed selections/images, upload precedence and initiative-bonus rules remain.

## Implementation questions and feasibility

The historical enumeration/fill-in questions are resolved for this accepted scope.
The [590 history](../handover/590-monster-source-workstream.md) retains dated live
v2/document/pagination observations, 5e.tools file-based enumeration and agreed
fill-in behavior. No provider authentication/entitlement bypass or guessed complete
D&D Beyond catalog is introduced. Live observations are samples at recorded dates,
not perpetual proof of every future provider catalog or image.

## Validation required

The agreed validation is satisfied on the reviewed green covering run, recorded
related tests and dated live checks, with bounded user acceptance and explicit
limits. tests/test_monster_source_catalog.py and tests/test_monster_source_picker_browser.py
cover the catalog/UI paths; recorded local related-browser checks include asset
wiring, image previews, button layout and provider extraction. Prior 590 samples
listed 30 sources, MM 450 and srd-2014 325 monsters and exercised Goblin from both
providers. These are historical samples, not a fresh live-server or completeness
audit. This close-out reviewed run/job outcomes, not every test log/screenshot;
no new manual, authenticated live-server, screen-reader or exhaustive provider
verification is claimed. Local results are not relabelled hosted CI totals.

## Accepted decisions - 2026-11-13

- Coordinated Stage 1 feasibility/design, Stage 2 SG-TODO-017 provider layer and Stage 3 SG-TODO-016 dropdowns; Stage 2 was already accepted and closed.
- D&D Beyond not in the source dropdown because of its access method; retained for name search only.
- Sources: None, configured enabled 5e.tools sources, all enabled Open5e documents.
- Name/statistics/image empty-or-overwrite behavior; Monster species must match the signed selected candidate.

## Delivery status

Stage 3 published as 7e2579efcd3fc2833498edb1bc6e5093612cbc5e. Successful covering
Branch tests 43419501886 attempt 1, job 131865652023, features/perplexity; evidence
publication 49822ee7cacfd3bc4e2bd520b98917aef036db2c under
ci-results-43419501886-attempt-1. Reviewed run.json/jobs.json match branch, tested
SHA, attempt and completed/success; all configured Chromium provisioning,
syntax/import, main Python/browser, pytest regression, JavaScript and standalone
browser/audit stages succeeded. Completion 2026-11-13T11:54:25Z (12:54 CET).
User final acceptance: 2026-11-13 at 13:02 CET. Earlier implementation-outstanding,
CI/acceptance-pending notes are superseded. [590 accepted close-out](../handover/590-monster-source-workstream.md#stage-3-accepted-close-out---2026-11-13).

No further agreed SG-TODO-016 implementation, publication, CI or acceptance action
remains; the three-stage workstream is complete. SG-TODO-017 Stage 2, 009/009.7 and
SG-TODO-019 stay closed. Documentation-only close-out with [skip ci], no fresh tests,
code/test/template/asset/pin/workflow changes or separate dispatch. No new commit
SHA is invented before publication, no merge/deployment or future blanket write
approval; no additional scope or acceptance gate is introduced.
