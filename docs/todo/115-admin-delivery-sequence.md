# 115 - Agreed Admin delivery sequence

[Back to TODO index](../../TODO.md)

## Current agreement - 2026-11-06

The user explicitly accepted the revised remaining-work sequence after clarifying
[SG-TODO-018 monster initiative bonus](180-monster-initiative-bonus.md):

018 -> 009.5 -> 015 -> 009.6 -> 009.7 -> coordinated 016/017 workstream.

This is now the agreed order, not merely the earlier recommendation. It supersedes
older sequencing statements where they differ. It orders work; it does not start
implementation, close tasks, assign owners/deadlines or approve unspecified design
and migration decisions. Each delivery retains its own tests, documentation,
validation, user acceptance and bound external-write approval requirements.

## Agreed remaining-work sequence

| Order | Work | Delivery intent and gates |
|---|---|---|
| 1 | [SG-TODO-018 - Monster initiative bonus](180-monster-initiative-bonus.md) | Next, before 009.5. Settle and validate monster raw roll, separately stored bonus, total/order updates, creation/import, Edit-modal-only bonus changes and persistence before reorganizing preparation/live views. Resolve remaining legacy, missing-data and shared-roll decisions first. |
| 2 | SG-TODO-009.5 - Workflow-based navigation | Continue the [Admin redesign](090-admin-usability-redesign.md) after 018. Agree the visibility mapping and tab/view design; preserve drafts, current context, pane preferences, independent lair gating and tools restoration. |
| 3 | [SG-TODO-015 - Battle Actions combatant statistics](150-battle-actions-combatant-statistics.md) | Add read-only available AC/current HP/HP MAX below target and Reaction source selectors before 009.6. Preserve missing-versus-zero handling, selection clearing and action resolution. |
| 4 | SG-TODO-009.6 - Focused live encounter workspace | Build and review against the settled initiative workflow, navigation and Battle Actions summaries. Preserve combat actions, Next/End/Reset, lairs and activity history. |
| 5 | SG-TODO-009.7 - Feedback, responsive and accessibility hardening | Consolidate the preceding work. This does not defer basic keyboard, responsive or accessibility checks from earlier increments. Feedback timing changes require explicit review of existing behaviour. |
| 6 | Coordinated [SG-TODO-016 - Source-based selection](160-source-based-monster-selection.md) / [SG-TODO-017 - Open5e API source](170-open5e-monster-source.md) workstream | Joint feasibility/design first; exact internal implementation order depends on verified catalog/API capabilities and the common data contract. Keep implementation after 009.7 rather than block redesign on unverified provider assumptions. |

## Why 018 comes next

The agreed change affects monster initiative input semantics, creation/import,
persisted roll/bonus/total representation, roster presentation and order updates.
Delivering it separately before navigation restructuring makes that behaviour the
baseline for subsequent preparation/live views and their final hardening, rather
than revisiting the new views to add it later. This is a delivery rationale, not a
claim that every later task technically depends on 018.

The user-agreed 018 rules are recorded in its task document and were saved at
da484d68d5ad39ef371ec8eeecb958149778fd8a. They include raw-roll replacement,
exactly-once bonus application, no refresh compounding, read-only roster bonus,
Edit-modal-only existing-monster bonus edits and immediate total/order updates.
Characters retain announced-final-total entry. This sequencing agreement does not
resolve additional legacy/default/shared-roll decisions or start implementation.

018 does not assume 016 or 017 is a prerequisite. Map available existing source
and .monster data during 018 planning; later integrations must reuse the resulting
contract without changing agreed calculation semantics. Do not claim unverified
provider bonus fields or derive a bonus from Dexterity without an agreed rule.

## Preserved compatibility and delivery gates

- Retain the accepted 009.1-009.4 foundation/header/forms/roster work and completed
  011/012/013/014 scopes. SG-TODO-013's wrap/Escape rules and validation close-out
  are settled; old planning text calling its boundaries unresolved is historical.
- Preserve character HP editing, current/max HP mechanics, single-line roster
  controls, local scrolling/focus exposure and the accepted Turn/Damage/Heal row
  removals. Action menus or replacement row-control designs need explicit agreement.
- Preserve source assembly and size constraints, backend/API/persistence boundaries
  except where a task explicitly requires a reviewed change, and campaign/security
  permissions. Do not overwrite the Admin script failure marker.
- Obtain a visibility mapping before replacing pane toggles. Switching views must
  not lose drafts, submit forms or mutate encounters. Preserve initial collapse,
  manual choices, dependent controls and automatic battle behaviour unless an
  explicit replacement is agreed.
- Prepare targeted regressions and retain existing coverage. Review actual CI
  results, distinguish fixture checks from live-server validation, and obtain
  task-specific visual/workflow acceptance before closure.
- Sequence approval is not blanket approval of later implementation payloads or
  external writes. Each coherent increment includes proportionate documentation
  and TODO updates and requires its own complete bound approval.

## Source-integration workstream: investigate before fixing internal order

1. Assess 016's complete source-catalog enumeration requirements and 017's current
   API requirements together. Verify pagination, filtering, access limits,
   attribution/licensing, missing fields and image availability.
2. Agree provider/source/document/monster identity and which selected-monster
   fields are populated or overwritten. Preserve selected-image continuity, upload
   precedence, manual entry and stale-response protection; reuse 018's bonus contract.
3. Implement 017 first where its provider integration establishes the contract
   needed by 016. Agree configuration/default enablement and any automatic fallback
   position; the request to add Open5e does not imply those decisions.
4. Implement 016's selectors against verified capabilities. Default None/manual
   entry stays usable. If a provider cannot supply the requested complete catalog
   through an acceptable mechanism, record the blocker and obtain agreement before
   narrowing scope or presenting a partial list as complete.
5. Recheck source help text, previews, responsive layout and keyboard behaviour.
   Completion of 009.7 does not exempt later integrations from their own hardening.

Accepted 2026-11-13: the user adopted this as three stages - (1) joint feasibility/design,
documentation only; (2) SG-TODO-017 Open5e provider with the generalized provider layer
and provider toggles; (3) SG-TODO-016 selectors. D&D Beyond is excluded from the dropdown
by explicit agreement. Decisions and Stage 1 findings: [590 handover](../handover/590-monster-source-workstream.md).

Open5e is not assumed technically necessary for existing-provider selectors. An
independent coherent 016 increment remains possible if investigation supports it.
Early bounded research is not silently inserted as a blocker before redesign.

## Earlier decisions and historical record

The original agreed sequence was 011; 009.4 with 012; 013 within that work or
immediately afterward; then 009.5, 009.6 and 009.7. It kept image previews separate,
HP/roster presentation coordinated, and initiative navigation against the resulting
roster. It did not authorize alternative row-control designs or defer accessibility.

The later recorded proposal added 014 first, placed 015 between 009.5 and 009.6,
and put coordinated 016/017 after 009.7. At that time it remained a proposal, not
acceptance of implementation details or changed task statuses. The current explicit
agreement above adopts the remaining proposed order and inserts 018 first. Earlier
completed increments stay completed; SG-TODO-009 remains in progress and remaining
phases/tasks keep their individual statuses.

The complete previous agreement, proposal, rationale and dated recording notes are
preserved in the [pre-update sequencing document](https://github.com/dajomas/Scrying-Glass/blob/da484d68d5ad39ef371ec8eeecb958149778fd8a/docs/todo/115-admin-delivery-sequence.md).
Historical statements that 011-013 were proposed or initiative boundaries unresolved
are not current blockers. Individual task/handover records remain authoritative
for delivered scope and validation evidence.

## Documentation-only recording

This update changes TODO.md, this sequencing section and 018's placement notes.
It does not implement, start or complete any task. No application, tests,
dependencies, runtime configuration or workflows change and no new tests ran.
README and HANDOVER index were reviewed/reused and remain accurate without edits;
links and runtime behaviour are unchanged. The commit message includes [skip ci],
with no workflow modification, separate dispatch or inferred workflow outcome.
