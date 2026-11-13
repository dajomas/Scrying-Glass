# 095 - Admin workflow navigation

[Back to TODO index](../../TODO.md)

## SG-TODO-009.5

- Status: completed and closed, 2026-11-09, on the user's explicit sign-off and request to close this item and move to the next scheduled task.
- Branch: features/perplexity. No merge, other-branch write or new owner/deadline. Overall 009 remains in progress; 009.6/009.7 remain proposed.
- Evidence: successful Branch tests 42616924220 attempt 1 covers c7c51725c5ac7724fc78ffd1931173cd1d19e0b8; publication 1c1c6323b119b1a7e71a93571985c214183819de. See [350 close-out](../handover/350-admin-workflow-navigation.md#sg-todo-0095-close-out---2026-11-09) for checked results and limits.

## Completed agreed scope

Campaign contains selection/access/backups, Add character and Characters; preparation contains setups/background/imports, Add monsters, both rosters and gated lair; live contains existing rosters, tools, lair and log. Header/context/actions/feedback and Battle/order/Danger zone stay shared. View filtering preserves native pane collapse, parent/child preferences, independent lair/tools restoration, DOM/drafts/files/selections and keyboard operation. No automatic tab switching, persistent preference, roster filtering or 009.6 focused layout.

Accepted follow-ups: removed bonus-help paragraph; original optional signed bonus field in Combat statistics between HP Range end/Quantity; species blur fills only a currently blank name from trimmed nonempty species; source overwrite includes bonus with missing/null clearing to default zero, distinct from explicit source zero, retaining invalid/failure/edit guards and candidate identity. Bulk Refresh behavior remains unchanged. Concise lookup copy and the current AC/HP/bonus checkbox label are delivered.

The user manually chose the final wording in cfc7b0f16f929041bc6107dd1f895d24492261c5: While entering Monster species, D&D Beyond and configured 5e.tools sources will be searched. Choose a version when prompted. Uploaded images override source images. Template and regression LOOKUP_HELP both match this wording; do not revert it to the assistant's earlier paragraph.

## Acceptance and evidence boundary

The user explicitly signs off 009.5 and requests closure. No agreed workflow-acceptance item remains open after that direction. Successful CI covers c7c51725, including 1,421 main/repeated tests OK, 766/0 audited connections, 43 pytest passes, JavaScript and full standalone smoke with no page errors. The later copy-only cfc7b0f1 revision has matching template/test text by source inspection, but no separate covering CI result is supplied or claimed. User acceptance of this later copy is not a fabricated post-edit run or checklist-by-checklist manual execution log.

Transport/provider/session mocks, fixture screenshot collection and storage reopen do not establish password login, live TCP/provider, new-process restart or exhaustive accessibility validation. Prior failed runs remain failed historical records. [Immutable pre-close-out task](https://github.com/dajomas/Scrying-Glass/blob/cfc7b0f16f929041bc6107dd1f895d24492261c5/docs/todo/095-admin-workflow-navigation.md) and handover retain preparation history and original open gates; this close-out supersedes their current-status wording.

## Transition

The [agreed sequence](115-admin-delivery-sequence.md) places [SG-TODO-015](150-battle-actions-combatant-statistics.md) next, before 009.6. The user explicitly requested moving on; live selector/row inspection has begun. 015 implementation/tests and validation are not delivered by this documentation update.

This update changes documentation only, runs no new tests, includes [skip ci] and does not modify or dispatch a workflow. Application behavior and the user's copy revision are unchanged.
