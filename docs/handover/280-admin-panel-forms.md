# 280 - Consistent Admin panels and forms

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-009.3](../todo/090-admin-usability-redesign.md#sg-todo-0093---consistent-panels-and-forms). Status: implementation included; validation and user visual/workflow acceptance pending. This does not close 009.3 or implement 009.4-009.7.

## User-facing behaviour

Campaign setup, Add character, Battle setups and Add monsters use concise headings and descriptions. Required-field descriptions explain the existing asterisks; native required attributes and validation remain. Character fields are grouped into details and starting statistics. Monster fields are grouped into identity, combat statistics and appearance. The upload form has a separate Import options group. Labels remain above inputs.

Entry-form submit buttons have a dedicated action area. Add character, Add manually, Save setup and Switch campaign receive primary emphasis; destructive styling remains distinct. Blank spacer labels around buttons are removed. Saved setup selection is labelled Saved battle setup rather than repeating the editable setup-name label.

View screen background and Import a .monster file are native details/summary disclosures, both initially open so existing workflows remain immediately accessible. Enter/Space use native keyboard behaviour and the browser exposes expanded/collapsed state without a mirrored aria-expanded attribute that could become stale. Closing these sections does not reset controls or clear files. Disclosure open state is page-local, not a new persisted preference. Viewer access and campaign backups retain their existing disclosure defaults and location. CSV/setup import buttons remain visible.

## Implementation and deployment

static/admin-panel-forms.js moves original nodes; it does not clone/replace inputs, set values, reset forms, assign submit/click handlers, fetch APIs or change storage. It adds fieldsets/legends, descriptions, action wrappers and disclosure containers. Reinstallation is guarded. The existing eight core sources, assembled-script marker, pane visibility, lair gates, roster controls and API/rules/persistence remain unchanged. The existing setup source-order test remains applicable because its template is untouched.

The scoped stylesheet loads after existing Admin styles. The deferred enhancement loads after combatant-row-layout.js; installation runs at DOMContentLoaded after earlier relocation callbacks, or immediately if the document is already ready. Deploy matching templates and the complete static tree, restart the correct server process because HTML assembles at import, then refresh browsers. No database migration is needed. Without the enhancement, original form markup remains available.

## Preparation evidence and pending checks

Executed during preparation: node --check for the drafted enhancement, tinycss2 stylesheet parsing with no stylesheet parse errors, and Python AST parsing of the regression module. The final regression revision was AST-parsed on 2026-11-06. These checks are not executed browser regressions, full-suite results or live-server evidence.

Prepared tests/test_admin_panel_forms.py contains one source-contract and five full-Admin intercepted-HTTP Chromium methods: field groups/required labels and repeat-install identity/handler/form-ownership retention; keyboard disclosures and character/file drafts across refresh; required validation plus failed/successful character submission; rejected monster HP with draft/focus retention and no mutation; fieldset geometry at 1440/768/375 and four desktop/narrow screenshots. Repeat-install identity assertions do not independently prove every node's identity across the first installation. Existing row/header/visibility regressions remain unchanged.

The reviewed .github/workflows/tests.yml discovers test_*.py through tools/run_split_tests.py, installs Chromium, and uploads SG_VISUAL_ARTIFACTS via admin-foundations-visual-fixtures. New screenshot names are 0093-1440-character.png, 0093-1440-monster.png, 0093-375-character.png and 0093-375-monster.png. No workflow change is needed. Screenshot capture and all full-Admin tests remain unexecuted here; no fresh baseline or after image has been visually reviewed during this preparation.

The user requested committing the implementation and triggering CI. The mixed implementation commit omits [skip ci] and relies on the configured branch-push workflow, not a separate dispatch. No new workflow/run/result is claimed before observation. Review covering CI evidence against the delivered commit, then obtain desktop/narrow visual and workflow acceptance before closure. Authenticated server behaviour, exhaustive combat/accessibility checks and screen-reader validation remain outside these fixture claims.

README.md, docs/User-Guide.md and existing indexed handover/TODO documentation were reviewed. README and User Guide retain accurate deployment/workflow instructions and remain unchanged; this section documents the new presentation and disclosure defaults. The redesign TODO consolidates duplicated historical delivery narrative into links and evidence summaries; detailed 009.1/009.2 history remains in the existing 260/270 handovers. No unfinished redesign stages are removed.
