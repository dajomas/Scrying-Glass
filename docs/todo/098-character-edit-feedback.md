# 098 - Stage 2 character Edit feedback

[Back to TODO index](../../TODO.md)

## Current Stage 2 reconciliation - 2026-11-12

SG-TODO-009.7-S2. Status: in progress; all named Stage 2 implementation groups
are delivered through 09c2f0912c77efdeffcd00f007470aae57b80622. Final combined
composition-test/status integration is prepared; combined validation and bounded
acceptance remain pending. No further planned handler migration was identified
in the bounded source/delivery reconciliation. This is not Stage 2 acceptance.

| Delivered group | Implementation reference / effective owner |
|---|---|
| Candidate selection / pending submit | d87579b; monster-candidate-selection.js |
| Source review | 9ab6df2; monster-refresh-review.js |
| Shared roster mutations / row patches | e4a2626; 010-source.js |
| Character/monster creation and .monster import | 37137b6, lookup fixture 8841bf0; 060-source.js |
| CSV and saved-setup imports | 9764fea; active 040-source.js bindings |
| Character Edit | fd13991, composition corrections; character-edit-feedback.js |
| Monster raw-roll | 162a389; monster-initiative-roll.js |
| Monster Edit | 31bb7c4, fixture correction cd1599e7; monster-initiative-edit.js |
| Roll-all | ed6a211; effective 040-source.js handler |
| Select-dead | ab730d4; bulk-select-all.js |
| Bulk Join pane success | 09c2f091; late initiative-join-gate.js wrapper |

The 11 rows group delivered work, not new acceptance requirements. Detailed
behavior, failed runs, preparation counts, limitations and earlier criteria remain
in handovers 380/480/490/500/510 and the
[pre-reconciliation task record](https://github.com/dajomas/Scrying-Glass/blob/09c2f0912c77efdeffcd00f007470aae57b80622/docs/todo/098-character-edit-feedback.md).
Earlier prepared/unfinished wording must not be read as requiring these features
to be reimplemented. 4A.1-4A.13 remain closed for their accepted scopes.

## SG-TODO-009.7 - Current checkpoint status - 2026-11-11

Historical checkpoint details are preserved in the pre-reconciliation task record
linked above and numbered handovers. The dated current reconciliation supersedes
those implementation-status notes, not their acceptance/evidence boundaries.
No priority, owner, deadline, order or unrelated task status changes.

## Preservation and remaining gates

Preserve JSON/FormData, HP/dice/bonus/source tokens, selected files, drafts,
selection behavior, server authorization/validation and accepted global Join
ownership. Retain explicit identities, persistent independent errors, matching
recovery, 3s pane successes, distinct no-replay refresh guidance, duplicate
protection and stale scope/session/timer suppression. Native File/FormData/events,
focus, loaded-Admin and retained reader/runner/tamper/browser suites still require
covering evidence where specified. Focused mocked checks do not establish native
or authenticated live-server acceptance; state any unperformed manual/accessibility
checks explicitly and seek bounded acceptance rather than inventing results.
Equivalent successful local or hosted evidence counts for its exact revision/scope;
both are not required. Keep accepted 009.6 behavior and all existing gates intact.

## Select-dead - 2026-11-12

SG-TODO-009.7-S2-SELECT-DEAD. Implementation delivered at
ab730d4498ac1e7a4cadb321ea8f391f45a60eef; combined validation and acceptance pending.
Historical preparation passed 13 tests (12 new plus retained regression file) and
three negative controls. [Scope, criteria and limits](../handover/500-select-dead-feedback.md).

## Bulk Join pane success - 2026-11-12

SG-TODO-009.7-S2-BULK-JOIN. Implementation delivered at
09c2f0912c77efdeffcd00f007470aae57b80622; combined validation and acceptance pending.
Historical preparation passed 49 tests (37 core/Join and 12 retained gate cases)
and four negative controls. [Scope, criteria and limits](../handover/510-bulk-join-pane-feedback.md).

## Final composition reconciliation - 2026-11-12

SG-TODO-009.7-S2-RECONCILIATION. Status: in progress; test/status payload prepared.
The existing loaded-Admin fixture gains one combined case covering selection,
roll-all, bulk Join rejection/recovery, separate refresh failure, unrelated Reset
error, draft/selection retention and no mutation replay. All 15 existing class
method ASTs remain unchanged. Full module compilation and five AST-isolated
inventory tests passed; no browser/full-suite run is claimed for this preparation.
[Reconciliation findings and limits](../handover/510-bulk-join-pane-feedback.md#final-stage-2-reconciliation---2026-11-12).

Remaining actions:
1. Obtain exact-content approval and push this final test/status integration.
2. Run the complete configured suite against that committed revision and review
   completed evidence, including the new loaded-Admin scenario; correct actual
   failures with fresh approval if needed. Earlier green cd1599e7 does not cover
   ed6a211, ab730d4 or 09c2f091.
3. Obtain bounded Stage 2 acceptance and reconcile its status without closing
   Stage 1, Stages 3-4, either whole feedback deliverable or phase 009.7.

Retain [skip ci] for this push as requested; no workflow changes or separate
dispatch. Combined validation remains pending until a final exact-revision run
is arranged. Inactive-source/pane-compatibility retirement and deferred test-suite
cleanup remain outside this scope. Do not mark completed solely because code is
pushed or metadata sizes agree with pins. No merge or deployment.
