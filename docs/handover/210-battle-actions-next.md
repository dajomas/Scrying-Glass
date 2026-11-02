# 210 - Next from Battle Actions

[Back to handover index](../../HANDOVER.md)

Prepared 2026-11-02 against c858a92709c456c8a1c62e8a73e60614e469cfb6.
Task: [SG-TODO-003](../todo/030-battle-actions-next.md), in progress, validation pending.

## User workflow

Next in Battle Actions discards pending drafts exactly as Close does, advances
combat once and opens the new active participant's ordinary action screen. It
never submits drafts, replays applied rows or undoes committed effects. The new
screen has normal initial rows rather than copied actions, reaction sources,
critical flags, statistics selections or concurrency tokens. Apply and Close keep
their original purpose. If no active participant remains, the modal stays closed.
Lair turns use the existing openBattleActions lair delegation.

## Implementation and integration

The template adds a type=button Next control and a deferred standalone controller.
Installation waits for DOMContentLoaded so the main Admin helpers and other
deferred extensions exist. The original large admin.js is not rewritten. Both
Next buttons are bound to one guarded composition of the existing /api/battle/next
endpoint and load(true), not a new turn engine. The modal shortcut additionally
uses the existing closeBattleActions/openBattleActions paths.

The controller chains the current request helper, tracking action POSTs and turn
advances. It checks battleActionsApplying and disabled modal submit controls to
cover Apply/start-of-turn refresh windows. Capture-phase submission suppression
blocks both forms during Next. Controls restore their previous disabled states.
Preflight fetch checks scope/actor; after POST, refreshed rendering and a fresh
state snapshot must agree with the returned actor, round and statistics token.
Scope changes or conflicting screens do not reopen a stale actor. Failed/uncertain
responses trigger reconciliation but never a second automatic POST. Errors remain
visible in main/modal notifications. Already-discarded drafts are not restored.

No server, authorization, transaction, schema or turn/effect rules change. The
server still owns round wrap, eligibility, expiry, persistence and broadcasts.
Guards are same-browser coordination, not server-side idempotency or cross-admin
compare-and-swap. A scope change racing a request can still have the normal
endpoint's effects; the UI declines stale reopening rather than claiming rollback.

## Validation and delivery status

The prepared test_battle_actions_next.py has twelve Chromium interaction fixtures
using production action helpers/template/controller and mocked server responses.
Existing Apply, reaction, reduction, turn, initiative and effect tests remain
unchanged and must run in CI. Browser fixtures are not full authenticated server
or player-display end-to-end coverage. Returned round/lair tests check client
composition, not execution of the real progression engine.

Five minimal local Chromium controller checks passed: success, duplicate-button
requests, lost response, scope change and refresh failure. They used stub normal
close/open/render helpers, not the full production action-helper integration.
Python test source compiled. The complete twelve tests and full suite have not
been executed locally. No CI result is claimed; use normal push-triggered CI.
After results, perform authenticated manual checks listed in the linked TODO.

Deploy the new JS and changed template together, restart for imported markup and
reload browsers. No migration is required. Help text in the modal documents Next.
README and existing statistics handovers were reviewed; their descriptions remain
accurate. The new indexed handover and TODO hold the detailed feature/validation
notes without expanding the root indexes. SG-TODO-001/002 completion and deferred
SG-TODO-004 are unchanged. Do not mark SG-TODO-003 complete before validation.
