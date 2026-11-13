# 300 - Add Monsters source help text

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-014](../todo/140-monster-source-help-text.md). Status: completed at the user's request after verified covering CI and wording acceptance. Implementation: 7b7096d2032be36f4b01159521db9bf667c86729.

## User-facing wording

The Add Monsters lookup/image explanation now says D&D Beyond is searched first, followed by 5e.tools after no usable matches when enabled/configured. Provider errors stop the lookup rather than causing fallback. With D&D Beyond disabled, enabled 5e.tools lookup may be used directly. The selected result's image is used only when present, and a manually selected Image file takes precedence. The AC/HP overwrite checkbox label names values from the selected D&D Beyond or 5e.tools result.

The old text mentioned only D&D Beyond and implied an independent image search merely from leaving Image empty. The new explanation reflects the existing candidate-selection flow and does not introduce a new lookup. The .monster file-help modal was inspected and left untouched: it documents JSON import and a statblock generator, not automatic provider selection. Existing dynamic lookup notices and candidate labels already distinguish D&D Beyond and 5e.tools; their JavaScript is unchanged.

## Scope and deployment

Only two text nodes in templates/admin/060_monster_input.html changed. No markup tags/attributes, IDs, fields, default values, native validation, script references, preview layout or form handlers are changed. Provider order, flags, source lists, no-match/error distinctions, raw candidates, selected-image token, local-upload precedence and AC/HP overwrite/edit protection remain owned by existing code. This is application-template wording, not a new provider integration, source dropdown or navigation/roster change.

Deploy the updated fragment with the matching existing application/static tree; restart the correct server process because Admin HTML assembles at import, then refresh the browser. No database/configuration migration or new runtime dependency is required.

## Executed preparation and limits

- Compared original/drafted HTML start/end tags and attributes: all 133 markup tokens matched, leaving only the two intended text replacements.
- Parsed tests/test_monster_source_help_text.py with Python AST.
- Executed its isolated source-content test against the drafted fragment: one test passed, checking provider order, configuration/error/disablement wording, selected-image/upload explanation, updated checkbox label and key unique IDs.
- Simplified real-Chromium fragment rendering passed at 1440/375 for visible explanation and exact checkbox accessible name. No full-Admin script stack or real provider calls were used in that fixture.

These preparation checks did not establish execution of the complete new module, full suite, authenticated live-server behaviour or user visual acceptance. The subsequent covering CI below supplies full-suite evidence, not retroactive execution during preparation. The existing backend candidate flow and previously reviewed selection/source documentation informed wording; no new live-provider capability was researched or claimed.

## Covering regressions and original delivery gates

The module contains two methods: the source-content test and a full-Admin intercepted-HTTP Chromium method at desktop/narrow widths. The latter opens the existing setup/monster panels according to aria-expanded, checks rendered provider/error text, finds the checkbox by its updated accessible name, verifies the existing ID/forms and asserts no page errors or unexpected mutations. It uses the established MonsterButtonLayoutTests fixture and retains all existing lookup, edit-preservation and provider regressions.

The reviewed Branch tests workflow discovers test_*.py through tools/run_split_tests.py, so no workflow update was needed. Full module/suite/CI execution and user acceptance were pending at implementation delivery; verified results and acceptance below supersede that status. No new screenshot artifact was added by this text-only regression method.

README.md, User Guide and indexed TODO/handover documentation were reviewed. README and User Guide remained accurate without edits; this section records the wording and deployment consequences. TODO.md and task status were updated with implementation, and HANDOVER.md links this section. Existing tasks and accepted 009.3/011 behaviour remain unchanged.

The mixed delivery included template and test changes, so its commit omitted [skip ci] and left normal branch-push CI enabled. No separate workflow was dispatched; no run result was inferred at delivery.

## Verified CI and completed close-out - 2026-11-06

Branch tests run 42261491777 attempt 1 was a push run on features/perplexity for exact implementation 7b7096d2032be36f4b01159521db9bf667c86729. Evidence was reviewed at dc4fbb45c99fc1d7db4fb3b24e3cb88fdc6b5720 under ci-results-42261491777-attempt-1. run.json records completed/success for workflow, tests job and every configured step: dependencies, syntax/server import, unittest/browser fixtures, visual upload, pytest, JavaScript, standalone browser/audit checks and post-job cleanup.

reader-chunks/index-000001.jsonl.txt maps workflow.log to file-000023. Reviewed chunks include:

- part-000073.txt: test_help_and_checkbox_label_render_without_mutation and test_lookup_help_explains_order_configuration_errors_and_images both explicitly pass; selected existing lookup/marketplace/name-layout tests also pass.
- part-000079.txt: main unittest summary, 1,061 tests OK.
- part-000080.txt: successful upload of 16 existing fixture screenshots, artifact ID 13523994701, and 43 pytest passes.
- part-000074.txt: selected existing reset/role/setup tests pass.
- part-000107.txt: standalone audits and mocked HTTP/WS real-Chromium smoke report passing output/no page errors, followed by cleanup.

The review covers metadata and selected assertions/summaries, not every assertion in all logs. Successful screenshot upload is not assistant inspection of image appearance. No 014-specific screenshot capture was introduced. Intercepted fixtures do not establish authenticated live-server/provider availability or exhaustive accessibility coverage. No separate full local-suite evidence for this implementation was supplied/reviewed; only the documented preparation checks and covering CI are claimed. Earlier 011 local/CI results are not substituted for 014 evidence.

The user requested full completion, recorded here as acceptance of the delivered wording and a request to close the task. Covering CI was verified before preparing this close-out. This is user acceptance, not an assistant-executed deployed browser audit. No further correction is indicated. SG-TODO-014 is completed; other tasks remain unchanged and the next agreed redesign work remains 009.4 with 012/013 coordination. The recorded sequencing revision remains a proposal outside specific user-started work; no unrelated design or implementation approval is inferred.

The close-out updates TODO.md, docs/todo/140-monster-source-help-text.md and this existing handover only. README.md, User Guide and HANDOVER.md were reviewed and remain accurate without edits. No application, tests, workflows or runtime configuration change, and no new tests are executed for this documentation-only update. Its commit contains [skip ci], does not dispatch a separate workflow and does not infer a new run outcome from the marker.
