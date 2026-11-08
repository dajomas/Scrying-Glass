# 310 - Admin roster presentation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Tasks: [SG-TODO-009.4](../todo/090-admin-usability-redesign.md) and [SG-TODO-012](../todo/120-character-hp-editors.md). Status: both completed and closed at the user's explicit request after covering local/CI verification and visual/workflow acceptance. Increment 1 supplied roster presentation/selection; increment 2 implements option 2, read-only character HP with editing through the existing Edit dialog. The requested Turn-control follow-up is also verified and accepted. This supersedes the earlier pending descriptions. SG-TODO-013 and later redesign phases are not implemented by this work; overall SG-TODO-009 remains in progress.

## Included behaviour

Both rosters have selected counts, Clear selection and selected-row outlines. Clear selection calls existing setAllSelected(kind,false), updating actual selection state, then focuses Select all. Bulk mutation options are disabled with zero selected; selection commands remain available and originally disabled options stay disabled. Counts describe the unfiltered table; search/filter, collection Add relocation, row expansion and action menus were considered but not introduced. They are not outstanding requirements for the accepted scope. Existing bulk confirmations/requests and single-line monster-row layout remain; the requested Turn removal leaves 10 visible monster-row and 7 visible character-row buttons.

Names show supplied battle/visibility/life-state text through textContent, not replacement combat rules. Initiative controls retain combatant-specific accessible labels without keyboard remapping. Numeric cells use tabular figures; rows align vertically. Character tables have local scrolling/focus exposure; monster scrolling remains. Removed row Damage/Heal controls and HP-change columns remain removed.

Characters show current/max HP as text, like Monsters. Use existing Edit, change Current HP and/or Max HP, then Save character. The character-hp-display.js enhancement runs after admin-rosters.js, replacing only matching HP input pairs in character cells. Its observer watches direct roster child replacement, not subtree decoration, avoiding self-triggered loops. It is guarded against duplicate installation and makes no network request. Original Edit/save/validation handlers, inline initiative, selection, APIs, permissions, HP rules and persistence remain unchanged. Existing generated inline-HP markup and dormant delegated handlers remain in the unchanged assembled core; the loaded enhancement removes those inputs from the interactive roster.

## Deployment

Deploy matching templates and the complete static tree, restart the correct process because HTML assembles at import, and reload browsers. Include character-hp-display.js and updated admin-rosters.css. No migration, new runtime dependency, core-assembly identity change or failure-marker replacement is needed. README and User Guide explain the Edit-dialog HP workflow. Technical compact-input documentation describes retained stylesheet selectors, not active roster HP editors when this enhancement is loaded. HANDOVER.md links remain accurate and unchanged.

## Requested Turn-control removal - 2026-11-06

Scoped rules in the loaded admin-rosters.css apply display:none to roster
button[data-mt] and button[data-ct]. This excludes Turn from display, keyboard
tab order and accessible button queries, including newly rendered rows. Legacy
DOM and delegated turn API handlers remain; this is not a permission/API
restriction. Other controls, initiative editing, Start/Next/End, turn highlighting
and automatic progression remain unchanged. There is no state mutation or observer.

Preparation passed stylesheet parsing and simplified Chromium at 1440/768/375,
with three replacements per width, forward/reverse focus skipping Turn, retained
Next and zero mutations. Full-Admin regressions measure 10 visible monster controls,
traverse 10 forward/9 reverse, and assert no accessible roster Turn plus 10/7 visible
controls after refresh. Other fixtures' raw DOM counts remain valid because legacy
buttons remain in the DOM, not as visible controls. The covering CI/local results
and user acceptance below supersede the follow-up's preparation-time pending status.

## Increment 1 preparation and local evidence

Original preparation passed JavaScript syntax, stylesheet parsing and regression Python AST parsing. Simplified Chromium checks covered native option.disabled gating, selected count, actual selection clearing, focus return, inline 0/20 HP, retained Edit and idempotence without page errors. Playwright is_disabled disagreed with native option.disabled during diagnostics; regressions use the native property, without bypassing selection logic. These were synthetic fixtures, not authenticated-server tests.

The user published completed local evidence for 720f8763708e9574f905d0ee946c0c5d70174d19 at 2aec821063fca27d9aad2aff3eb51d872cf5ec58, under local-tests-720f876/run-20261106T181310Z-I8wUpT. Reviewed environment/summary/exit records report completed=1 and overall/all 48 command exits zero. Pytest reports 43 passes; the complete connection-audit log reports 1,064 tests OK, 680 connections opened and zero without explicit close. Mocked provider exception tracebacks end in OK/PASS, not test failures. This evidence predates increment 2 and is not its closure evidence.

## Increment 2 preparation

Executed: node --check on the new JavaScript and AST parsing of the new regression module; both passed. Simplified real-Chromium passed zero HP, large values, zero maximum, table replacement, duplicate installation, unchanged initiative/dialog inputs and retained Edit click, with no page errors. Notebook sync-Playwright and evaluate-returned-callback harness issues were corrected before the passing async fixture; no application changes were needed.

Prepared tests/test_character_hp_display.py covers asset/order/size contracts and full-Admin intercepted-HTTP Edit rejection, retained draft, native invalid maximum, retry, 0/20 save and full page reload at 1440/375 widths. Reload reads mock-backed state, not a real database. tests/test_admin_rosters.py covers read-only HP, selection, controls, initiative, focus, idempotence and screenshots 0094-1440-rosters.png/0094-375-rosters.png. Existing test_*.py CI discovery and SG_VISUAL_ARTIFACTS upload covered these without workflow changes. The original pending-full-suite statements are superseded below.

## Verified close-out - 2026-11-06

Implementation sequence: roster increment 1, 834c4c3d0a7d963bb44b17dc6346447ec18dc21b; HP increment 2, 90dcfab919556ac94d05c44c0ec0e775fab32f9d; Turn follow-up, d91f73bfe121870296a1df79f58c58c21bcaeb59.

CI: Branch tests run 42276181187 attempt 1 covered exact SHA d91f73bfe121870296a1df79f58c58c21bcaeb59 on features/perplexity. Evidence publication 386beabbcd6e39378014d4a86df24dd4d68f5b75, folder ci-results-42276181187-attempt-1. run.json and collection.txt confirm completed/success, matching tested SHA and successful collection. Workflow, tests job and configured steps succeeded. Main unittest reports 1,066 tests OK; pytest 43 passed; repeated connection-audit suite 1,066 tests OK with 681 connections opened and zero without explicit close.

Reviewed workflow.log reader chunks under file-000025: part-000022 contains all three roster methods OK; part-000054 the two HP methods OK; part-000070 all four row-layout methods OK; part-000079 main unittest summary; part-000080 successful upload of 18 fixture images; part-000081 pytest summary; part-000107 audit/connection and standalone smoke summaries. Relevant checks include selection preservation, read-only HP, Edit rejection/retry/native validation/save/reload, keyboard/local scrolling, geometry and Turn absence after refresh. Upload/collection includes both roster widths but is not assistant screenshot inspection.

Local: completed suite=all tested 386beabbcd6e39378014d4a86df24dd4d68f5b75, evidence publication 423ab05f08b4ec9f8d5e7c30d1bf600ea07ffb63, folder local-tests-386beab/run-20261106T191207Z-NSLlFY. environment.txt reports completed=1, start 19:12:07Z and finish 19:17:55Z. exit-code.txt and all 48 summary.tsv entries are zero (syntax/import, unittest, pytest, 38 JavaScript and six standalone commands). suites/pytest/regressions.log reports 43 passed; complete suites/standalone/script-2.log reports 1,066 tests OK and 681/0 connections. Main unittest command success is verified from its exit, with the local count taken from the complete repeated audit. Provider fixture exception tracebacks finish in OK/PASS, not failures. Repository root tree/blob identities for application, tests, templates, tools and workflows match between CI implementation d91f73b and current evidence publication 423ab05.

The user explicitly accepted desktop/narrow roster presentation, selection/bulk workflows, Edit-dialog HP values retained after reload and absence of Turn, then requested 009.4 and 012 completed and closed on 2026-11-06. This is user visual/workflow acceptance. It is not an assistant-executed authenticated live-server, real database persistence, screenshot inspection or exhaustive screen-reader/combat audit; fixture transports remain mocked/intercepted. Both tasks and the accepted Turn follow-up are concluded for their agreed scope. Overall 009 remains in progress; 013 and later phases remain separate.

This close-out changes five documentation files only, runs no new tests and changes no application, test, dependency or workflow files. README/User Guide and HANDOVER.md remain accurate and unchanged. Commit message contains [skip ci]; no separate workflow is dispatched and no new run outcome is inferred.

## SG-TODO-018 stage B compact status spacing - 2026-11-08

This later correction is separate from the accepted 009.4/012 scope above.
Branch features/perplexity-018 only. [Current correction plan](../todo/185-monster-correction-plan.md) and [stage-B history](340-combined-monster-lookup.md).
The colour-only/single-line correction was delivered as
1d4815d8f0e89840687ba13136ce88b3b631b9f3. Its covering CI was unreviewed at the
spacing delivery; the subsequent covering run is verified below. Delivery is not
stage-B acceptance. The user's follow-up screenshot showed an empty-looking line
above the status.

At spacing commit 9cfcbb26106fa95c5e28f58cba45e7234b47220f the shared CSS bottom-
aligned the name/species cell and reduced all main-row data-cell bottom padding
from 1.85rem to 1.6rem. This brought the name block against the status strip rather
than centering it beside taller initiative controls. The later primary-alignment
request below supersedes that bottom-alignment choice, while keeping the compact
footer lane, single-line status and colour-only controls. No data or API change.

Spacing preparation: the original stylesheet was reconstructed and verified against
blob 23d8e79ee7a990081d9bab3b1fafa457774a299e. Local isolated Chromium compared
old/new CSS using synthetic two-row tables in both rosters at 375/768/1440 and
16/20 px root font sizes, three replacements per configuration. Gaps fell from
about 25-28 px to 2.7-3.4 px; rows shrank by 4-5 px in that fixture. Single-line
status, clearance from adjacent content, within-row bounds, no glyphs, no page
widening and no page errors passed. These are historical component measurements,
not deployed or full-Admin results.

The original assembled-Admin/intercepted-HTTP spacing method checked short/long
names in both rosters at six viewport/font configurations over three refreshes,
reused line/non-overlap assertions and limited name-glyph-to-status gap to half
a rem. Python compilation/AST parsing and both embedded JS syntax checks passed.
It was not run locally because FastAPI was absent. Its covering CI is below.
The primary-alignment follow-up deliberately replaces the name-glyph gap criterion
with a compact gap after the lowest occupied row content plus measured primary
centres; shorter text cannot be forced against the footer while also centred
beside taller controls. Historical preparation is not relabelled.

## Covering spacing CI - 2026-11-08

Branch tests run 42522294918 attempt 1 succeeded on features/perplexity-018 for
exact tested SHA 9cfcbb26106fa95c5e28f58cba45e7234b47220f. Evidence read at
publication 883f1c832815789e8faebd265821a359402d3784 /
ci-results-42522294918-attempt-1. Run/job metadata agrees; all listed steps and
cleanup succeeded, none skipped. Main and repeated suites each report 1,411 tests
OK. Connection audit: 763 opened/0 without explicit close, PASS. Syntax/server
import, pytest, JavaScript, artifact upload and standalone checks succeeded.
No setup/collection failure is reported. Repetition is not unique tests and green
fixture CI is not deployed visual acceptance. Older failed runs remain failed.

## SG-TODO-018 primary row alignment - 2026-11-08

The user requested vertical centring of the primary checkbox/name/HP items in
Characters and checkbox/name/AC/HP/bonus/raw-input items in Monsters against the
main action-button line. Species, Total output and status are secondary lines,
not part of the primary alignment reference. The screenshots show the character
name too low and the monster input above the primary line.

Production changes CSS only: align main roster data cells on their first content
baseline and remove the name cell's bottom-alignment override. Native text/input/
button baselines then align the primary content rather than centring complete
name/species or input/Total blocks. The 1.6rem footer padding, absolute single-line
status, local scrolling, colour-only states, input sizes and all HTML/JS/data/API
semantics remain unchanged. No per-monster pixel offsets, new renderer or migration.
Short text may have normal air below it beside a taller control; the footer must
not add an empty strip after the row's lowest content or overlap values/controls.

Preparation: original CSS/test reconstructed against live blobs
83e7858fe5e3233e389dd40e2a05004f76b0c3ee and
b7f160ae3222bdcc83886d61f3fbaad97d055986. Isolated Chromium compared old/new
CSS in synthetic Characters/Monsters tables at 375/768/1440 and 16/20 px root
fonts. Before, character name centres were about 13-17 px below buttons and the
monster input about 9.5 px above; after, measured primary centres were within
0-1 px of the buttons and footer clearance remained at least 2.7 px. The original
font/markup stub limits remain: this is component geometry, not full Admin,
authenticated server, persistence or deployed acceptance.

The assembled-Admin regression checks primary centres for selection, first-line
name, initiative input, available monster AC/HP/bonus and character HP against the
Edit-button centre within .2rem. It retains short/long names, six viewport/font
configurations, three refreshes, no mutations/page errors and shared one-line/
non-overlap checks. A half-rem maximum footer gap is measured from the lowest
occupied row content, excluding status. Initial Python parsing and both embedded
JS syntax checks passed, but the first CI exposed the wrapped-name measurement
error below. The correction uses the first nonempty rendered text fragment without
changing tolerance, production CSS or the first-line contract.

Alignment implementation was delivered as 96adeb4012492b6618aabfa0f9dd803cc9b5d58d.
Its first covering run failed. This increment includes the fixture correction and
evidence/status notes; its SHA only after push. Corrective CI and user stage-B
visual/workflow acceptance remain pending. README/User Guide, root indexes and
340 were reviewed/reused unchanged: links, workflows and overall open status
remain accurate. SG-TODO-018 is not closed; no merge or other-branch write.

## Alignment CI failure and wrapped-name measurement correction - 2026-11-08

Branch tests 42525208958 attempt 1 failed for exact
96adeb4012492b6618aabfa0f9dd803cc9b5d58d on features/perplexity-018. Evidence
was read at publication fcc2e5133c289b2b4f237e866cf8b1f1db992c08 /
ci-results-42525208958-attempt-1. Run/job metadata agrees. Main and audit-repeat
suites each ran 1,411 tests with six subcase assertion failures in one method:
test_primary_centres_and_compact_status_after_refresh, characters name, for
375/768/1440 and 16/20 px root sizes. Narrow cases reported 258.5 px differences;
desktop reported 33.5/44.75 px. These repeat executions are not twelve independent
defects. This is not a setup/collection error. Later assertions/refreshes in the
failed subcases were not reached. Syntax/server import, pytest, JavaScript, upload
and checkout cleanup succeeded; Node/Python post-setup cleanup was skipped.
Connection tracking reports 763 opened/0 without explicit close, but the audit
step remains failed because its repeated suite failed. Subsequent log/round audits
and mocked-transport browser smoke completed; smoke reports no page errors.
Keep the historical run failed, regardless of later corrections.

The existing metric selected the long character-name text node and used its
getBoundingClientRect union. A wrapped name's whole-block centre is below its
first line even when that line is correctly aligned. Correction selects the first
nonzero-width/height getClientRects fragment for name alignment, errors explicitly
if none exists, and asserts the narrow long-character-name case really wraps.
Do not force character names onto one line or widen .2rem tolerance. All numeric/
input/checkbox centres, footer/line/non-overlap, mutation and page-error checks
remain. No production file, style, server/API or workflow changes are included.

Preparation: the original test matches live blob
2d1275ba9c27d0392b1dd62a6904212386e680a8. Revised Python compiles/parses; both
embedded JavaScript expressions pass Node syntax. An isolated native-Chromium
text-range fixture at the six viewport/root-size configurations reproduced the
union error for wrapped names: 17 narrow/4 wide fragments gave false offsets of
152/28.5 px, while the first-line metric gave 0 px; a deliberate 12 px shift was
still detected. Short single-line names passed and there were no page errors.
These are minimal-markup geometry checks, not exact CI typography reproduction,
full Admin, authenticated HTTP, provider, persistence or deployed acceptance.
The full-Admin regression was not executed locally (FastAPI absent); normal CI
discovers it. Fresh covering CI and manual visual acceptance remain required.
No skip marker, workflow edit/dispatch, overall close-out, merge or other-branch
write. Earlier successful CI remains tied to its earlier exact tested SHA.
