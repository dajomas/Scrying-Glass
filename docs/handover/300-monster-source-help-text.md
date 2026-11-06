# 300 - Add Monsters source help text

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-014](../todo/140-monster-source-help-text.md). Status: implementation included; covering CI and user browser acceptance pending.

## User-facing wording

The Add Monsters lookup/image explanation now says D&D Beyond is searched first, followed by 5e.tools after no usable matches when enabled/configured. Provider errors stop the lookup rather than causing fallback. With D&D Beyond disabled, enabled 5e.tools lookup may be used directly. The selected result's image is used only when present, and a manually selected Image file takes precedence. The AC/HP overwrite checkbox label names values from the selected D&D Beyond or 5e.tools result.

The old text mentioned only D&D Beyond and implied an independent image search merely from leaving Image empty. The new explanation reflects the existing candidate-selection flow and does not introduce a new lookup. The .monster file-help modal was inspected and left untouched: it documents JSON import and a statblock generator, not automatic provider selection. Existing dynamic lookup notices and candidate labels already distinguish D&D Beyond and 5e.tools; their JavaScript is unchanged.

## Scope and deployment

Only two text nodes in templates/admin/060_monster_input.html change. No markup tags/attributes, IDs, fields, default values, native validation, script references, preview layout or form handlers are changed. Provider order, flags, source lists, no-match/error distinctions, raw candidates, selected-image token, local-upload precedence and AC/HP overwrite/edit protection remain owned by existing code. This is application-template wording, not a new provider integration, source dropdown or navigation/roster change.

Deploy the updated fragment with the matching existing application/static tree; restart the correct server process because Admin HTML assembles at import, then refresh the browser. No database/configuration migration or new runtime dependency is required.

## Executed preparation and limits

- Compared original/drafted HTML start/end tags and attributes: all 133 markup tokens match, leaving only the two intended text replacements.
- Parsed tests/test_monster_source_help_text.py with Python AST.
- Executed its isolated source-content test against the drafted fragment: one test passed, checking provider order, configuration/error/disablement wording, selected-image/upload explanation, updated checkbox label and key unique IDs.
- Simplified real-Chromium fragment rendering passed at 1440/375 for visible explanation and exact checkbox accessible name. No full-Admin script stack or real provider calls were used in that fixture.

These checks do not establish execution of the complete new module, full application suite, authenticated live-server behaviour or user visual acceptance. The existing backend candidate flow and previously reviewed selection/source documentation informed wording; no new live-provider capability was researched or claimed.

## Prepared covering regression and delivery gates

The module contains two methods: the source-content test and a full-Admin intercepted-HTTP Chromium method at desktop/narrow widths. The latter opens the existing setup/monster panels according to aria-expanded, checks rendered provider/error text, finds the checkbox by its updated accessible name, verifies the existing ID/forms and asserts no page errors or unexpected mutations. It uses the established MonsterButtonLayoutTests fixture and retains all existing lookup, edit-preservation and provider regressions.

The reviewed Branch tests workflow discovers test_*.py through tools/run_split_tests.py, so no workflow update is needed. Full module/suite/CI execution and user browser acceptance remain pending; retain in-progress TODO status until reviewed. No new screenshot artifact is added by this text-only regression method.

README.md, User Guide and indexed TODO/handover documentation were reviewed. README and User Guide remain accurate without edits; this section documents the exact wording and deployment consequences. TODO.md and the task status are updated with this increment, and HANDOVER.md links this new section. Existing tasks and accepted 009.3/011 behaviour remain unchanged.

The mixed delivery includes template and test changes, so the commit omits [skip ci] and leaves normal branch-push CI enabled. No separate workflow dispatch or unobserved new run result is claimed.
