# 310 - Admin roster presentation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-08. SG-TODO-009.4 and SG-TODO-012 remain completed/closed by the user's 2026-11-06 acceptance. The later SG-TODO-018 roster corrections are now completed as part of its explicit overall close-out. Overall 009 and separate later redesign tasks are unaffected.

Complete earlier delivery records, local/CI evidence, geometry measurements, original anchors and failed results remain in the [immutable pre-close-out record](https://github.com/dajomas/Scrying-Glass/blob/17932b9b5ac1f02ccdc4cb53e39277fb589e6d96/docs/handover/310-admin-rosters.md). Current acceptance/evidence supersedes delivery-time pending wording, not historical outcomes.

## Included behaviour

Both rosters retain selected counts, actual Clear selection with focus return, selected-row outlines and disabled bulk mutation without selection. Names/status use supplied state, not new combat rules. Characters/Monsters show read-only HP; character HP editing uses the existing Edit dialog. Initiative controls retain combatant-specific accessible labels, numeric tabular figures and local scrolling/focus exposure. Row Damage/Heal and HP-change columns remain removed; visible monster/character row controls remain 10/7 after Turn removal.

character-hp-display.js enhances generated roster HP controls after admin-rosters.js, is guarded/idempotent and watches direct roster replacement, not self-decoration. Existing validation/save/permissions/persistence remain. Legacy generated markup and dormant handlers remain but do not constitute active roster HP editors.

## Deployment

Deploy matching templates and complete static assets, including character-hp-display.js and admin-rosters.css. Restart the correct process for imported HTML changes and reload browsers. No new migration, runtime dependency, core-assembly identity or failure-marker replacement arises from these roster corrections. README/User Guide retain the Edit-dialog HP workflow.

## Requested Turn-control removal - 2026-11-06

Scoped CSS hides button[data-mt]/button[data-ct] from display, tab order and accessibility queries, including replacement rows. Legacy DOM/delegated APIs remain; this is not a permission restriction. Start/Next/End, turn highlighting and progression remain unchanged.

## Increment 1 preparation and local evidence

Original static/isolated-browser preparation and the user's published local evidence remain in the immutable record. They are not relabelled as later increment validation.

## Increment 2 preparation

The HP enhancement retained Edit rejection/draft/native-validation/retry/save/reload checks with mocked backing state, plus roster keyboard/local scrolling/Turn absence. Original preparation limits remain archived.

## Verified close-out - 2026-11-06

Roster 834c4c3d0a7d963bb44b17dc6346447ec18dc21b, HP 90dcfab919556ac94d05c44c0ec0e775fab32f9d and Turn d91f73bfe121870296a1df79f58c58c21bcaeb59 had covering CI 42276181187 attempt 1 and published local verification; the user accepted the agreed desktop/narrow presentation and workflows and requested 009.4/012 closure. Complete counts/paths remain archived. This accepted scope is not reopened by 018.

## SG-TODO-018 stage B compact status spacing - 2026-11-08

Separate from 009.4/012. Colour-only/single-line correction 1d4815d8f0e89840687ba13136ce88b3b631b9f3 removes minus/check decorations while retaining colours, fixed captions, aria-pressed and keyboard semantics. Status stays one line in a reserved footer lane, may extend beneath adjacent columns without covering content and remains within local scrolling. Display alive does not rename stored standing or change life rules.

Spacing 9cfcbb26106fa95c5e28f58cba45e7234b47220f used 1.6rem bottom padding and initially bottom-aligned the name cell. The later primary-alignment request supersedes that name-cell choice, not its historical evidence.

## Covering spacing CI - 2026-11-08

42522294918 attempt 1 succeeded for 9cfcbb26106fa95c5e28f58cba45e7234b47220f; publication 883f1c832815789e8faebd265821a359402d3784. This covered the earlier spacing correction, not the later exact alignment SHA.

## SG-TODO-018 primary row alignment - 2026-11-08

96adeb4012492b6618aabfa0f9dd803cc9b5d58d aligns main cells on their first content baseline and removes name-cell bottom alignment. Primary checkbox/name/numeric/raw-input items align with action buttons; species/Total/status remain secondary. No per-monster offsets, new renderer, data/API/migration change. Short primary text may leave normal space beside taller controls; the footer follows lowest occupied row content. Regression tolerance remains .2rem for centres and half a rem for footer gap.

## Alignment CI failure and wrapped-name measurement correction - 2026-11-08

42525208958 attempt 1 failed for the alignment implementation: six repeated width/font subcases in one method measured the union of wrapped character-name lines rather than the first line. It remains failed. Correction f5808a2dfbc9b8d8bd4de9706956dbe8312815a5 selects the first nonempty Range.getClientRects fragment, errors if none exists and requires actual wrapping in the narrow long-name case. No production CSS or tolerance relaxation. Original isolated-browser diagnostics and unexecuted-local/full-Admin limitation remain historical in the immutable record.

Covering 42526295799 attempt 1 succeeded for that exact correction; publication 790a32b0f86eb60a86319d7c3158f9a7c22f489b, ci-results-42526295799-attempt-1. The alignment method explicitly passed. The user confirmed the roster visual check successful, then requested overall SG-TODO-018 close-out after the remaining-work review. CI/visual gates are no longer pending. See [overall acceptance, reconciliation and fixture limits](340-combined-monster-lookup.md#sg-todo-018-close-out---2026-11-08) and [completed correction plan](../todo/185-monster-correction-plan.md). No new tests/live audit, merge or other-branch write occurs in this documentation-only close-out.

## Managed rejection notice regression repair - 2026-11-10

This test-only correction is part of the [approved 009.7 CI repairs](380-feedback-delivery-plan.md#ci-repair-stages---2026-11-10), not a reopening of accepted roster features. Run 42780869296 attempt 1 tested ae050ea62aaca544912fcbca90cf2fbf0a223904; published evidence 80c565db0ec67a72d2141da380f6e800016e4526 records the remaining Python error at test_stage_b_rosters.py's exact-text rejection wait. The renderer prefixes message text and adds a separate Dismiss control, so bare exact text no longer identifies the notice.

The revised test captures the final monster PATCH by path and method before the Enter keypress, requires HTTP 409, the exact show_ac=true JSON payload and expected rejection detail, then waits for one matching .sg-feedback-text inside #monsterAddNotification. It requires exactly one additional PATCH and retains all unchanged-state, aria-pressed=false, AC-label, browser-error and unexpected-mutation assertions. Production handlers, permissions, rendering and feedback severity are unchanged; the unmigrated producer still uses the temporary information route.

Executed preparation: the complete revised test module passed Python AST parsing and is 9,995 UTF-8 bytes; its reconstructed original matched live blob 3ff601c83180567c4b45fda50169b0f80db7585a. An isolated Chromium smoke using the exact production feedback renderer with a stub subscription and intercepted HTTP captured status 409 and payload show_ac=true, matched information/error-prefixed notices, rejected identical text outside the monster region, and confirmed the old exact-text locator matched zero elements. The renderer reconstruction matched its live blob identity. This validates locator/request mechanics, not the full Admin roster fixture, controller integration or live-server behavior. Those remain pending covering CI.

Normal CI applies without a skip marker. No CI success, corrective commit SHA, full-suite repair or 009.7/4A.1 completion is claimed here. README and root TODO/HANDOVER indexes were reviewed against unchanged live identities and remain accurate without edits; existing task statuses and links are unchanged. Other managed-notification, bundle-identity and layout repairs remain within the approved stages.
