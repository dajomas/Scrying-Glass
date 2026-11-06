# 140. Add Monsters source help text

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-014
- Status: proposed
- Recorded: 2026-11-06
- Priority: not assigned; no change to the [agreed Admin delivery sequence](115-admin-delivery-sequence.md).
- Dependencies: none established. Related source configuration work: [SG-TODO-006](060-fivetools-source-configuration.md).

## Requested change

The user reports that help texts in the Add Monsters panel mention only D&D Beyond as a monster source. Update the relevant help texts to also mention 5e.tools as the backup when no monster can be found on D&D Beyond.

## Acceptance criteria

- Relevant Add Monsters source help texts mention both D&D Beyond and 5e.tools.
- Wording clearly states that D&D Beyond is searched first, with 5e.tools used as the fallback when no matching monster is found.
- Wording remains consistent with configured source availability and does not promise fallback after provider errors.
- This task changes explanatory text only, not lookup order, provider configuration or lookup behavior.

## Validation required

Inspect all source-related help texts in the Add Monsters panel and verify the revised wording in the browser. Update relevant text/UI regression coverage during implementation where applicable.

## Delivery status

Backlog entry only. Help-text implementation and validation have not been performed for this task.
