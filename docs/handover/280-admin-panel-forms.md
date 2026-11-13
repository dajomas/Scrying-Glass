# 280 - Consistent Admin panels and forms

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-009.3](../todo/090-admin-usability-redesign.md#sg-todo-0093---consistent-panels-and-forms). Status: closed (completed) after verified covering local/CI validation and the user's explicit visual/workflow acceptance. Implementation: 588831fb1ece198fefee3a2422410123a8f1f175. This does not implement 009.4-009.7.

## User-facing behaviour

Campaign setup, Add character, Battle setups and Add monsters use concise headings and descriptions. Required-field descriptions explain the existing asterisks; native required attributes and validation remain. Character fields are grouped into details and starting statistics. Monster fields are grouped into identity, combat statistics and appearance. The upload form has a separate Import options group. Labels remain above inputs.

Entry-form submit buttons have a dedicated action area. Add character, Add manually, Save setup and Switch campaign receive primary emphasis; destructive styling remains distinct. Blank spacer labels around buttons are removed. Saved setup selection is labelled Saved battle setup rather than repeating the editable setup-name label.

View screen background and Import a .monster file are native details/summary disclosures, both initially open so existing workflows remain immediately accessible. Enter/Space use native keyboard behaviour and the browser exposes expanded/collapsed state without a mirrored aria-expanded attribute that could become stale. Closing these sections does not reset controls or clear files. Disclosure open state is page-local, not a new persisted preference. Viewer access and campaign backups retain their existing disclosure defaults and location. CSV/setup import buttons remain visible.

## Implementation and deployment

static/admin-panel-forms.js moves original nodes; it does not clone/replace inputs, set values, reset forms, assign submit/click handlers, fetch APIs or change storage. It adds fieldsets/legends, descriptions, action wrappers and disclosure containers. Reinstallation is guarded. The existing eight core sources, assembled-script marker, pane visibility, lair gates, roster controls and API/rules/persistence remain unchanged. The existing setup source-order test remains applicable because its template is untouched.

The scoped stylesheet loads after existing Admin styles. The deferred enhancement loads after combatant-row-layout.js; installation runs at DOMContentLoaded after earlier relocation callbacks, or immediately if the document is already ready. Deploy matching templates and the complete static tree, restart the correct server process because HTML assembles at import, then refresh browsers. No database migration is needed. Without the enhancement, original form markup remains available.

## Historical preparation evidence and validation gates

Executed during preparation: node --check for the drafted enhancement, tinycss2 stylesheet parsing with no stylesheet parse errors, and Python AST parsing of the regression module. The final regression revision was AST-parsed on 2026-11-06. These checks were not executed browser regressions, full-suite results or live-server evidence; the verified results below supersede the original pending validation status.

Prepared tests/test_admin_panel_forms.py contains one source-contract and five full-Admin intercepted-HTTP Chromium methods: field groups/required labels and repeat-install identity/handler/form-ownership retention; keyboard disclosures and character/file drafts across refresh; required validation plus failed/successful character submission; rejected monster HP with draft/focus retention and no mutation; fieldset geometry at 1440/768/375 and four desktop/narrow screenshots. Repeat-install identity assertions do not independently prove every node's identity across the first installation. Existing row/header/visibility regressions remain unchanged.

The reviewed .github/workflows/tests.yml discovers test_*.py through tools/run_split_tests.py, installs Chromium, and uploads SG_VISUAL_ARTIFACTS via admin-foundations-visual-fixtures. New screenshot names are 0093-1440-character.png, 0093-1440-monster.png, 0093-375-character.png and 0093-375-monster.png. No workflow change was needed. Full-Admin tests and screenshot capture were not executed during preparation; later local/CI execution is recorded below. No fresh baseline or after image was visually reviewed by the assistant during preparation.

The user requested committing the implementation and triggering CI. The mixed implementation commit omitted [skip ci] and relied on the configured branch-push workflow, not a separate dispatch. Covering results and acceptance were pending at initial delivery and are recorded below. Authenticated server behaviour, exhaustive combat/accessibility checks and screen-reader validation remain outside these fixture claims.

README.md, docs/User-Guide.md and existing indexed handover/TODO documentation were reviewed. README and User Guide retain accurate deployment/workflow instructions and remain unchanged; this section documents the new presentation and disclosure defaults. The redesign TODO consolidates duplicated historical delivery narrative into links and evidence summaries; detailed 009.1/009.2 history remains in the existing 260/270 handovers. No unfinished redesign stages are removed.

## Verified local results - 2026-11-06

Exact implementation: 588831fb1ece198fefee3a2422410123a8f1f175. Evidence commit b000d0fc753ce6b6d430b10b6e32f07c6c8482bd publishes local-tests-588831f/run-20261106T152634Z-3P6S1l. environment.txt records suite=all, detached local clone of that exact commit, Python 3.14.7, Node 22.23.2, WSL2, completed=1 and timestamps 15:26:34Z-15:31:55Z. Uncommitted working-tree changes are not tested.

Reviewed summary.tsv and exit-code.txt show overall exit 0 and zero exits for compileall/server import, unittest, pytest, all 38 JavaScript commands and all six standalone commands. suites/python/unittest.log explicitly reports all six new panel/forms methods passing and selected existing foundation/header/visibility/shell regressions passing, but the connector truncated it before the final suite summary. suites/pytest/regressions.log reports 43 passes. standalone-inventory.tsv identifies script-2 as tests/audit_connection_lifetime.py; its complete suites/standalone/script-2.log reports the repeated 1,053-test suite OK, 676 connections opened and zero without explicit close. That repeated audit supplies the verified local test count; it is not an additional 1,053 distinct tests. Mocked provider-error tracebacks in the audit are fixture output, not failed results.

## Verified CI results - 2026-11-06

Branch tests run 42242916048 attempt 1 was a push run on features/perplexity for exact source 588831fb1ece198fefee3a2422410123a8f1f175. Evidence is published at 6f57c24e37e65b15675548d1cd411be0f3a69ea7 under ci-results-42242916048-attempt-1. Reviewed run.json records completed/success for workflow, tests job and every configured step, including syntax/import, unittest/browser fixtures, pytest, JavaScript, standalone checks and visual upload.

reader-chunks/index-000001.jsonl.txt maps workflow.log to file-000021. Reviewed chunks:

- part-000022.txt: all six panel/forms methods explicitly pass, plus selected initial-visibility and shell checks.
- part-000078.txt: main unittest summary, 1,053 tests OK.
- part-000079.txt: 14-file visual upload successfully finalised, artifact ID 13515987601.
- part-000080.txt: 43 pytest passes and JavaScript runner command.
- part-000106.txt: repeated 1,053-test audit OK, 676 connections/zero without explicit close, selected standalone audits passing and mocked-transport real-Chromium smoke with no page errors.

artifact-files.txt lists 14 images, including the four expected new 009.3 desktop/narrow character/monster screenshots alongside existing foundation/header views. Their collection/upload and passing screenshot method were verified, not assistant visual inspection of each image. The review covers run/job/step metadata and selected explicit assertions/summaries, not every assertion in all logs. Fixture results are not authenticated live-provider/server evidence.

## User acceptance and close-out - 2026-11-06

After successful local and CI review, the user explicitly accepted SG-TODO-009.3 in response to the desktop/narrow visual and workflow acceptance question. This satisfies the phase's user acceptance gate; it does not claim an assistant-executed live-server or exhaustive accessibility/combat audit. No corrective application or test change was indicated by reviewed results.

SG-TODO-009.3 is closed (completed). Stages 009.1/009.2 remain closed; overall SG-TODO-009 remains in progress; 009.4-009.7 remain proposed and are not implemented. SG-TODO-011 image previews remain separate and proposed; they are not part of this accepted increment.

The close-out updates TODO.md, the existing redesign task and this handover only. README.md and HANDOVER.md were reviewed and remain accurate without edits. No application/test/workflow code changes or new test executions are included. The documentation-only commit contains [skip ci], does not separately dispatch a workflow and does not infer an unobserved new workflow result.
