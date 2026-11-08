# 185. Monster provider and roster correction plan

[Back to TODO index](../../TODO.md)

- Updated: 2026-11-08. Tracking: SG-TODO-018 follow-up and adjacent lookup/roster corrections.
- Status: completed for the agreed correction scope; SG-TODO-018 closed at the user's explicit request after review of the three remaining reconciliation/acceptance/close-out actions.
- Branch: features/perplexity-018. No merge or other-branch write included.
- Related: [018 contract](180-monster-initiative-bonus.md), [lookup](010-monster-lookup.md), [configuration](060-fivetools-source-configuration.md), [rosters](../handover/310-admin-rosters.md), [A.1 history](../handover/335-fivetools-initiative-correction.md), [close-out evidence](../handover/340-combined-monster-lookup.md#sg-todo-018-close-out---2026-11-08).

## Decision and current state

A.1 remains accepted; A.2/A.3 have covering corrective CI and the user's manual sign-off. The final roster correction has successful covering CI and the user's successful visual check. After review distinguished stale task text from remaining workflow acceptance, the user explicitly requested all three actions and SG-TODO-018 close-out. Record this as overall acceptance/closure, not an invented per-check manual test log. No owner/deadline assigned. The previously rejected close-out draft is not reused.

Detailed historical preparation, acceptance checklists, source/commit hashes and failed/passing results are preserved in the [immutable pre-close-out record](https://github.com/dajomas/Scrying-Glass/blob/17932b9b5ac1f02ccdc4cb53e39277fb589e6d96/docs/todo/185-monster-correction-plan.md), including its linked earlier snapshots. Historical pending gates describe their delivery dates and are superseded only by the acceptance/evidence here. No unrelated task is completed.

## Processing order

A before B was followed. Every corrective external write required exact-content approval; this close-out is documentation only.

### Stage A: provider correctness and candidate selection

1. A.1 extraction: accepted. The user confirmed Noble Prodigy XMM +7, creation, Refresh/apply/reload and raw 16+7=23. Preserve signed values, exact identity/provenance and explicit-zero versus missing; no Dexterity guess or source-backed default zero.
2. A.2 combined search: accepted. Search enabled providers/configured books; keep provider/book/edition candidates and their statistics separate. Any enabled-provider failure or incomplete book search blocks candidates rather than offering partial results as exhaustive. Preserve exact selected identity. fivetools_fallback independently enables candidate search; legacy image/stats fallback stays unchanged.
3. A.3 sole-candidate Refresh: accepted. One usable signed candidate resolves automatically; multiple require choice, zero remain unresolved. Never substitute retained identity, auto-select fields, mutate live state or bypass Apply. Preserve other rows' choices.

### Stage B: compact and consistent roster presentation

Accepted for close-out on the basis of covering CI, the user's visual check and subsequent overall close-out direction.

4. Visible Roll heading/(legacy) suffix removed, accessible raw labels/separate totals/internal legacy semantics retained.
5. Single-line status may extend under AC/HP without covering values/controls/next row or widening the page. Compact footer follows occupied row content. Primary checkbox/name/HP in Characters and checkbox/name/AC/HP/bonus/raw input in Monsters align with the action-button line; species/Total/status remain secondary. Short/long names, narrow layout, local scrolling/focus and colour-only fixed-caption controls retain aria-pressed and keyboard semantics. Wrapped-name geometry uses its first rendered line, not the whole text union.
6. Display standing as alive without changing stored identifiers or down/stable/dead rules.

### Final validation and acceptance

Reconciled: CI/fixture evidence covers behaviour checks; user sign-offs cover A.1/A.2/A.3 and roster appearance; the subsequent explicit close-out direction accepts the agreed overall scope. Retained criteria include fixed-toggle request/state/rejection handling, selection/bulk/Edit/statistics preservation, raw labels/totals/legacy semantics, life-state semantics, scrolling and focus. These are not asserted to have each received a new manual run. No new tests or live audit were executed during close-out. See the handover for exact fixture limitations.

## Current four-commit plan and validation - 2026-11-08

Historical four-increment preparation/activation/help delivery is complete; full per-increment evidence is preserved in the immutable record above. Backend correction e2d06aac12dabbdc7d4febe7be1efc3b3a2b2b29 has successful CI 42504619218 attempt 1; failed run 42503436253 remains failed.

## Historical references

A.1 evidence remains in 335. Original foundation contract remains in 180. Earlier records and anchors remain in the immutable snapshot; current status is completed, not the old pending delivery state.

## Commit 5 initiative overwrite follow-up - 2026-11-08

7c760064aaa3484974362fb423f89245e4eb55fa removed the separate bonus confirmation, not candidate choice or Refresh Apply. Available bonuses follow the AC/HP overwrite option, preserving intervening edits, missing/invalid source data and exact signed offers. Covering CI 42514703672 attempt 1 succeeded; publication 8c7ce113ee00548ac3126744dd98a6c25d2a3579. Earlier preparation and detailed workflow checklist remain archived; they are not newly executed checks.

## A.3 implementation and validation - 2026-11-08

Implementation c62d203d3b92aa277eb7e34f4c90da789ab0e58b; correction 1c289d485bffcf8197fb32238349729e52b822ed. Explicit Apply, authentication, stale/expiry/replay/transaction guards and unaffected-row choices remain.

### First A.3 CI failure and fixture correction

42516636403 attempt 1 failed because an explicit-choice fixture supplied only one candidate. It remains failed. The correction supplies two distinct candidates and adds sole-candidate review/Apply coverage at desktop/narrow widths. No production auto-resolution failure is inferred from that stale expectation.

### Corrective CI and user acceptance - 2026-11-08

42517614512 attempt 1 succeeded for 1c289d485bffcf8197fb32238349729e52b822ed. Publication 73183fd70d6111083b2ca0048c6a029c0c04fed8. The user manually tested and signed off A.2/A.3 on 2026-11-08.

## Stage B delivery and validation gate - 2026-11-08

Initial 11f104058efb2a56365b0309ce8c6ee829d84c18 had failed CI 42520146312 (rejection feedback hidden in a collapsed input pane). Colour-only/single-line correction 1d4815d8f0e89840687ba13136ce88b3b631b9f3 and spacing 9cfcbb26106fa95c5e28f58cba45e7234b47220f have successful covering CI 42522294918 attempt 1. Failed runs remain failed.

### Compact spacing follow-up - 2026-11-08

Spacing initially bottom-aligned the name cell with 1.6rem footer padding. The later primary-alignment request superseded bottom alignment, not the historical measurements.

### Covering spacing CI and primary alignment - 2026-11-08

42522294918 attempt 1 covered 9cfcbb26106fa95c5e28f58cba45e7234b47220f; publication 883f1c832815789e8faebd265821a359402d3784. Alignment 96adeb4012492b6618aabfa0f9dd803cc9b5d58d uses the first main-cell baseline, .2rem primary-centre tolerance and a half-rem footer gap from lowest occupied content.

### Alignment CI failure and wrapped-name fixture correction - 2026-11-08

42525208958 attempt 1 failed for 96adeb4012492b6618aabfa0f9dd803cc9b5d58d because the fixture measured the union of wrapped name lines. It remains failed. Test correction f5808a2dfbc9b8d8bd4de9706956dbe8312815a5 measures the first nonempty Range.getClientRects fragment and asserts real wrapping without widening tolerance or changing production CSS.

Covering run 42526295799 attempt 1 completed successfully for that exact corrected SHA on features/perplexity-018. Publication 790a32b0f86eb60a86319d7c3158f9a7c22f489b, ci-results-42526295799-attempt-1. The corrected alignment method explicitly passed. The user confirmed the roster visual check successful, then explicitly requested overall close-out after the remaining-work review. All three reviewed actions are resolved for the agreed scope. Documentation-only message includes [skip ci]; no workflow edit/dispatch or merge.
