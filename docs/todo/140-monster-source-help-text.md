# 140. Add Monsters source help text

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-014
- Status: completed, 2026-11-06, at the user's request after verified covering CI and acceptance of the wording.
- Implementation: 7b7096d2032be36f4b01159521db9bf667c86729.
- Recorded: 2026-11-06. Implementation requested: 2026-11-06.
- Priority: no rank relative to unrelated work assigned. The [recorded sequencing proposal](115-admin-delivery-sequence.md) recommended this correction next; the user subsequently requested starting 014.
- Dependencies: none established. Related source configuration work: [SG-TODO-006](060-fivetools-source-configuration.md).

## Requested change

The user reported that help texts in the Add Monsters panel mentioned only D&D Beyond as a monster source. Update the relevant help texts to also mention 5e.tools as the backup when no monster can be found on D&D Beyond.

## Acceptance criteria

- Relevant Add Monsters source help texts mention both D&D Beyond and 5e.tools.
- Wording clearly states that D&D Beyond is searched first, with 5e.tools used as the fallback when no matching monster is found.
- Wording remains consistent with configured source availability and does not promise fallback after provider errors.
- This task changes explanatory text only, not lookup order, provider configuration or lookup behavior.

## Implementation and preparation - 2026-11-06

The static lookup/image explanation now names D&D Beyond first and 5e.tools after no usable matches when enabled/configured. It explicitly distinguishes provider errors (stop, no fallback), primary disablement (enabled fallback may be used directly), and selected-result image use with local-file precedence. The overwrite checkbox label names both providers rather than implying that only D&D Beyond values can be selected.

Only two text nodes in templates/admin/060_monster_input.html changed. Preparation compared 133 start/end markup tokens and attributes before/after; all were identical. Original IDs, form fields, controls, validation, preview layout, scripts, lookup requests, selection tokens, provider settings and overwrite/edit guards are unchanged. The .monster file-help modal was reviewed and left unchanged because it describes file import and an external generator, not automatic provider lookup.

The added tests/test_monster_source_help_text.py includes a source-content/ID test and a full-Admin intercepted-HTTP browser method covering text and the checkbox's accessible label at 1440/375 with no mutations. Executed preparation: Python AST parsing; one isolated source test passed against the drafted fragment; simplified Chromium rendering of the fragment passed visible text and checkbox accessible-name checks at both widths. These were not execution of the full-Admin method or full suite during preparation. Existing CI discovery covers the module; later covering results and user acceptance below supersede the initial pending status. See [handover](../handover/300-monster-source-help-text.md) for deployment and review limits.

## Verified completion - 2026-11-06

Branch tests run 42261491777 attempt 1 tested exact implementation 7b7096d2032be36f4b01159521db9bf667c86729 on features/perplexity via push. Evidence commit dc4fbb45c99fc1d7db4fb3b24e3cb88fdc6b5720 contains ci-results-42261491777-attempt-1. Reviewed metadata records completed/success for workflow, tests job and every configured step. Main unittest reports 1,061 tests OK; both new source-help methods explicitly passed, including the browser method's desktop/narrow cases; pytest reports 43 passes. The visual upload succeeded for 16 existing fixture screenshots; no new 014-specific screenshot method was added and no assistant visual inspection is claimed.

The user requested marking 014 fully completed. That request is recorded as acceptance of the delivered wording and a close-out request; covering CI evidence was supplied and verified before preparing completion. It is not an assistant-executed authenticated deployment/browser acceptance claim. No separate full local-suite evidence for 014 has been supplied or reviewed; do not confuse preparation checks or earlier 011 evidence with this implementation's local validation. Covering CI supplies the reviewed full-suite evidence.

No corrective change is indicated by reviewed results. This closes only SG-TODO-014; other task statuses and accepted 009.3/011 behaviour remain unchanged. Next agreed redesign work remains 009.4 with 012/013 coordination. Preserve task-specific design agreements and fixture/live-provider limitations.

## Delivery status

Completed after covering CI and the user's acceptance/completion request. README.md, User Guide and HANDOVER.md remain accurate without edits for this close-out. This close-out updates TODO.md and the existing task/handover only, with no application, test or workflow code changes and no new test execution. The documentation-only commit includes [skip ci], dispatches no separate workflow and does not infer an unobserved workflow result. The original template/test implementation was a mixed delivery and correctly omitted that marker.
