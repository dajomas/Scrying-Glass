# 260 - Admin visual foundations

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-009.1](../todo/090-admin-usability-redesign.md).
Status: closed (completed) at the user's request after verified corrective local/CI results and user-confirmed notification behaviour and foundation consistency on the correct server. Stages 009.2-009.7 remain proposed and are not implemented.

## Scope and decisions

The user agreed staged delivery and requested stage 009.1. The new static/admin-foundations.css scopes every rule to body.admin-shell and reuses the established glass-theme.css dark surfaces, gold, blue focus colour, local font stack and radii. It adds a 4/8/12/16/24/32 spacing token scale in rem units, common control-height/radius tokens, a brighter muted label colour, neutral outer panels, restrained teal/amber group borders/headings, tabular table numerals and quieter modal shadows. Product h1 branding remains unchanged; operational h2/h3 headings use the UI font.

The stylesheet loads after admin-shell.css and before monster-button-layout.css. Compact editor widths, local roster overflow, source assembly, existing handlers, control order, action classifications, status colours and combatant/display colour values are unchanged. Checkboxes, radios, colour pickers and specialised icon/turn-order buttons are excluded from the generic control-height rule. Existing specialised ID-scoped component geometry retains precedence. The corrective presentation module is described below; core scripts and their tracked failure marker remain unchanged.

Deploy the matching template fragments and complete static tree, restart for imported HTML changes, then reload browsers. No database/configuration migration is required. README was reviewed and left unchanged because its dark/gold theme, layout/source and deployment descriptions remain accurate.

## Initial preparation evidence

Executed against the initial drafted CSS: tinycss2 parsed 17 rules with zero stylesheet/declaration errors; size 3,254 UTF-8 bytes. Python AST parsing passed for the original 6,515-byte test module. Its two source-contract methods passed against the drafted stylesheet and template in a temporary fixture, not a full checkout. These check asset order, Admin scoping, tokens, size and absence of visibility/width/overflow overrides.

Nominal sRGB contrast on panel #1a202c was computed: text #e6e2d6 12.60:1; muted #b1bacb 8.36:1; campaign #84c5c0 8.34:1; battle #d8b25a 8.11:1; focus #8fb7d8 7.72:1. These selected pairs are not a rendered/full accessibility audit or verification of every state.

No Playwright/browser fixture, authenticated live server, full suite or workflow run was executed during initial preparation. The subsequent initial CI and screenshot review are recorded below; preparation alone was not validation.

## Regression and screenshot coverage

The tests/test_admin_foundations.py module reuses the established intercepted-HTTP full-Admin fixture without inheriting its test cases. At 1440/375 viewport widths it checks unchanged pane/form/action/colour state across stylesheet enable/disable, unsaved character-name retention, 11 monster buttons, absent row HP buttons, computed panel/modal tokens and keyboard focus, plus page errors and non-GET mutations. Existing roster geometry, focus exposure, refresh, initial visibility, compact-input and shell tests are retained unchanged.

Before/after screenshots use the same fixture DOM and manually opened input panes; baseline disables only the foundation stylesheet. CI unittest discovery includes the module. The workflow gives that step SG_VISUAL_ARTIFACTS in runner.temp and uploads admin-foundations-visual-fixtures after it, including after a preceding failure unless cancelled. Missing files produce an artifact warning, not visual validation. The standalone audit may rerun unittest and writes its separate screenshots to the system temporary directory. Local callers may set SG_VISUAL_ARTIFACTS to retain screenshots elsewhere.

## Verified initial CI and visual review - 2026-11-06

Initial implementation: e632eba99e00695c7f002148bde8c0aee386d4fe. Evidence commit 21aa823a6381768c7f2a081597262b7b57d0bfc5 contains ci-results-42209803055-attempt-1. Run 42209803055 attempt 1, Branch tests, tests that exact implementation SHA on features/perplexity. Reviewed run.json records workflow and tests job completed/success and successful configured steps.

Reader index maps workflow.log to reader-chunks/file-000011. Parts 20-21 explicitly show the four original foundations tests passing; part 77 reports 1,033 unittest tests, OK; part 79 reports 43 pytest passes. Part 104 records the audit's repeated 1,033-test suite passing, 674 opened connections and zero without explicit close. Parts 77-78 confirm four uploaded screenshots, artifact ID 13498741414. These are selected log assertions plus run/job/step metadata, not inspection of every assertion. Fixtures do not establish authenticated deployed-server behaviour.

The user supplied the desktop before/after screenshots for visual review. Neutral panels, restrained teal edges and brighter UI-font headings/labels improved readability. Remaining observations were blank coloured notification strips, a crowded/wrapping header, and encounter-tools content partially above the captured workspace. The screenshot alone did not prove an overlap defect. The user requested necessary 009.1 changes after that review, not blanket approval of the generated post-009.7 impression.

## Corrective implementation - 2026-11-06

Root cause of blank strips: initial notification elements contain whitespace; paneNotification clears messages to one space after its existing three-second timeout, and the monster lookup setter also uses a space for its blank state. Existing :empty CSS cannot collapse a whitespace text node.

The new 867-byte static/admin-notification-layout.js is a deferred presentation enhancement for the four existing pane notification elements only. It sets hidden when trimmed text is empty, and removes that hidden state for real text. It preserves text exactly, role=status, aria-live=polite, handlers, timeout duration/replacement behaviour and lookup status content. Each observer watches childList/characterData/subtree, not attributes, so its own hidden updates do not loop. Installation is guarded; missing elements are tolerated. It runs after the other Admin enhancements and before combatant-row-layout.js. No existing core script, source fragment, API or encounter logic changes.

The screenshot fixture previously filled an off-screen character field before capture, allowing focus-induced workspace scrolling. Each capture now explicitly resets adminScroll.scrollTop to zero and asserts workspace top is at or below header bottom. This improves evidence framing; no production header positioning or user scroll restoration is changed, and no production overlap fix is claimed. New before/after images remain CSS-only comparisons with the notice correction enabled in both; they are not whole-commit before/after comparisons.

Four new Node VM tests cover blank/meaningful initial text, subsequent changes and clearing, observer configuration, idempotence and missing nodes. Browser coverage adds initial zero-height notices, real-message visibility and exact text, existing timeout clearing, in-place text edits, live-region attributes and reinjection at 1440/375 widths. A source test verifies the deferred script inclusion/order. The updated Python module has six test methods and is 10,237 UTF-8 bytes; the Node test is 2,509 bytes. All are below the 20,000-byte source limit.

Executed corrective preparation: node --check passed for the exact new module; all four Node VM tests passed with zero failures/skips; Python AST parsing passed for the updated browser/source module; the new script-inclusion source test passed against the drafted end fragment in a temporary fixture. No corrective Playwright, full suite or CI run was executed during preparation. Existing workflow discovery covers the new .cjs test and updated unittest module without a workflow change.

## Historical pending review and retained limits

At corrective preparation, the initial green run did not validate the corrective payload. The subsequent verification and acceptance below supersede that pending status. Representative screen-reader announcement behaviour was not manually established; preserved ARIA attributes alone do not prove announcements. Full encounter operations, delayed/failed requests, lair gating and exhaustive authenticated deployment behaviour are not newly established by this visual fixture.

Crowded header/action hierarchy remains 009.2; workflow tabs and live-workspace restructuring remain later phases. No arbitrary density reduction or removal of accepted controls is included.

## Verified corrective validation and close-out - 2026-11-06

Corrective implementation: 9a96b5a125c0b22b18218769c9c5cf2508a60ac0. Full local evidence is published at 01bd4b232c51aefb7ee185c4099b0e3c381692c7 under local-tests-9a96b5a/run-20261106T122845Z-ogPIRn. environment.txt identifies the exact source, suite=all, Python 3.14.7, Node 22.23.2, WSL2 and completed=1. summary.tsv records zero exits for syntax/import, unittest, pytest, all 38 JavaScript commands and six standalone checks; exit-code.txt is 0. All six foundations methods explicitly pass in the reviewed unittest excerpt. The main log was truncated by the connector before its final summary; the complete audit log reports a repeated 1,035-test suite OK, 674 connections opened and zero without explicit close. The mapped notification-module log reports four passes without skips, and pytest reports 43 passes.

CI run 42216373147 attempt 1, Branch tests, tests that same exact corrective SHA on features/perplexity. Evidence commit 7adfe04748b300a3f6686af6714121ea8a0853bb contains ci-results-42216373147-attempt-1. Reviewed run.json reports workflow and tests job completed/success and all configured steps successful. Reader chunks map workflow.log to file-000011: parts 20-21 explicitly show all six foundations methods passing; part 77 reports 1,035 tests OK; part 79 reports 43 pytest passes; parts 80-81 show all four notification-module Node tests passing without skips; part 105 reports the repeated 1,035-test connection audit OK, 674 opened and zero without explicit close. Part 78 confirms four uploaded visual fixtures, artifact ID 13502146827, also listed in artifact-files.txt. This is selected log and metadata review, not inspection of every individual assertion.

Additional standalone-only evidence: commit 2e116451ec9f674367ac090c821834c87ab9d02d publishes local-tests-7adfe04/run-20261106T125644Z-run00o for source 7adfe04748b300a3f6686af6714121ea8a0853bb. All six command exits and overall exit are zero; its complete audit reports 1,035 tests OK and 674/0 connections, and its Chromium smoke reports no page errors with mocked HTTP/WS. Commit b40ea1be5e6f717cfe42aa1e4de05e5b453ba4d6 publishes local-tests-2e11645/run-20261106T130214Z-sIU6WM for source 2e116451ec9f674367ac090c821834c87ab9d02d. Only its environment, summary and exit code were reviewed: standalone suite completed, all six command exits zero, overall exit zero. Do not describe either invocation as another independent all-suite run.

The user supplied fresh 1440/375 screenshots. Their top-of-workspace framing is clean; header crowding remains later-phase work. A subsequent report of persistent blank strips was investigated using browser diagnostics showing no script reference and no installed enhancement, while the correction files were present on disk. The user then confirmed they had viewed the wrong server. On the correct server they explicitly confirmed that notification areas exist only for a message and that foundation consistency is accepted. No extra code patch was needed for that report. This is user-reported deployed visual/notification acceptance, not an assistant-executed live-server test or a screen-reader audit.

The user explicitly requested closing SG-TODO-009.1. It is closed (completed) on the verified corrective local/CI evidence and that acceptance. SG-TODO-009 remains in progress, with 009.2-009.7 proposed. This close-out updates TODO.md and the existing TODO/handover sections only. README and HANDOVER.md were reviewed and remain accurate without edits. No application, test or workflow code changes, test execution during close-out preparation, or separate workflow dispatch are included. No CI skip was requested; the commit omits the skip marker and does not claim a new workflow state before it is observed.
