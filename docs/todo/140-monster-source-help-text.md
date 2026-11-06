# 140. Add Monsters source help text

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-014
- Status: in progress; implementation included, covering CI and user browser acceptance pending.
- Recorded: 2026-11-06. Implementation requested: 2026-11-06.
- Priority: no rank relative to unrelated work assigned. The [recorded sequencing proposal](115-admin-delivery-sequence.md) recommends this correction next; the user subsequently requested starting 014.
- Dependencies: none established. Related source configuration work: [SG-TODO-006](060-fivetools-source-configuration.md).

## Requested change

The user reports that help texts in the Add Monsters panel mention only D&D Beyond as a monster source. Update the relevant help texts to also mention 5e.tools as the backup when no monster can be found on D&D Beyond.

## Acceptance criteria

- Relevant Add Monsters source help texts mention both D&D Beyond and 5e.tools.
- Wording clearly states that D&D Beyond is searched first, with 5e.tools used as the fallback when no matching monster is found.
- Wording remains consistent with configured source availability and does not promise fallback after provider errors.
- This task changes explanatory text only, not lookup order, provider configuration or lookup behavior.

## Implementation and preparation - 2026-11-06

The static lookup/image explanation now names D&D Beyond first and 5e.tools after no usable matches when enabled/configured. It explicitly distinguishes provider errors (stop, no fallback), primary disablement (enabled fallback may be used directly), and selected-result image use with local-file precedence. The overwrite checkbox label names both providers rather than implying that only D&D Beyond values can be selected.

Only two text nodes in templates/admin/060_monster_input.html are changed. Preparation compared 133 start/end markup tokens and attributes before/after; all were identical. Original IDs, form fields, controls, validation, preview layout, scripts, lookup requests, selection tokens, provider settings and overwrite/edit guards are unchanged. The .monster file-help modal was reviewed and left unchanged because it describes file import and an external generator, not automatic provider lookup.

Prepared tests/test_monster_source_help_text.py includes a source-content/ID test and a full-Admin intercepted-HTTP browser method covering text and the checkbox's accessible label at 1440/375 with no mutations. Executed preparation: Python AST parsing; one isolated source test passed against the drafted fragment; simplified Chromium rendering of the fragment passed visible text and checkbox accessible-name checks at both widths. These are not execution of the full-Admin regression method or full suite. Existing CI discovery covers the module; full covering CI and user browser acceptance remain pending. See [handover](../handover/300-monster-source-help-text.md) for deployment and review limits.

## Validation required

Inspect all source-related help texts in the Add Monsters panel and verify the revised wording in the browser. Review covering regression CI and obtain user browser acceptance before marking completed. Preserve existing lookup/order/configuration behaviour; no live provider capability or availability claim is made by text fixtures.

## Delivery status

Implementation included with validation pending, not completed. README and User Guide remain accurate without edits; the indexed handover records the wording changes. This delivery includes a template and tests and is not documentation-only, despite changing only application wording. It omits [skip ci] and relies on normal push-triggered CI; no workflow result is inferred and no separate dispatch is included.
