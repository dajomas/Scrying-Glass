# 210 - Next from Battle Actions

[Back to handover index](../../HANDOVER.md)

Initial implementation: f9fa3c76b6f7c078b3d0a5c63679eea2892dff9a.
Script-order correction prepared 2026-11-02 against b2b2023417489d73796cff1e99381d8cc609bd18.
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

The template adds a type=button Next control. The deferred standalone controller
must load in fragment 190 after admin.js and the other Admin extensions. Its
readyState check waits for DOMContentLoaded only while loading; parser-deferred
execution normally sees interactive and installs immediately. Therefore deferred
script order, not just the attribute, is part of its dependency contract. The
initial placement before admin.js in fragment 180 was incorrect and is removed.
The original large admin.js and controller logic are not rewritten by this repair.

Both Next buttons use one guarded composition of the existing /api/battle/next
endpoint and load(true), not a new turn engine. The modal shortcut additionally
uses existing closeBattleActions/openBattleActions paths. The controller chains
the current request helper, tracking action POSTs and turn advances. It checks
battleActionsApplying and disabled submit controls to cover Apply/start-of-turn
refresh windows. Capture-phase submission suppression blocks both forms during
Next; controls restore previous disabled states. Preflight checks scope/actor;
after POST, rendered and fresh state must agree with returned actor, round and
statistics token. Scope changes/conflicting screens do not reopen a stale actor.
Failed/uncertain responses reconcile but never automatically POST again. Errors
remain visible in notifications. Already-discarded drafts are not restored.

No server, authorization, transaction, schema or turn/effect rules change. The
server still owns round wrap, eligibility, expiry, persistence and broadcasts.
Guards are same-browser coordination, not server-side idempotency or cross-admin
compare-and-swap. A scope change racing a request can still have the normal
endpoint's effects; the UI declines stale reopening rather than claiming rollback.

## CI diagnosis and prepared repair - 2026-11-02

Run 41522989190, attempt 1, tested f9fa3c76b6f7c078b3d0a5c63679eea2892dff9a.
Inspected evidence is in ci-results-41522989190-attempt-1 at
b2b2023417489d73796cff1e99381d8cc609bd18. run.json shows completed failure, despite
successful syntax/server import, unittest/browser, pytest and JavaScript steps.
The standalone step failed at browser_smoke_272cc73.py's unchanged pageerror
assertion: admin: request is not defined (workflow chunk 000096). The same chunk
records the connection audit's rerun of 953 tests as OK and 647 connections with
zero missing explicit close. Those are observed results of the failed original
run, not a passing post-correction run.

The initial twelve interaction fixtures inserted their helpers before the controller
and missed its actual page boot order. The new test_battle_actions_next_boot.py
loads the real modal and document-end fragments via parser-inserted deferred
scripts, the real controller, and stub Admin helpers/other scripts. It asserts
no startup pageerrors, a bound Next handler, one mutation and opening actor b.
The existing complete assembled-page smoke remains unchanged as the full-script
integration gate; no test or workflow is disabled to obtain a passing result.

The new boot regression passed locally on the corrected ordering. Reverting the
fragment placement to the old ordering made it fail with request is not defined.
The controller and original end-fragment reconstructions were verified against
Git blobs dfa305352daf297e87c018879fb48e9fbcb0effd and
cfaa08d1399f9208b74b9266d8ec81e0c7d8d4b9. Python test source compiled. This is a
focused Chromium parser/defer fixture, not the full application, all scripts or
live authenticated provider/player validation. Corrective CI remains pending.

Earlier five minimal local controller checks used stub close/open/render/transport
helpers and did not test script boot. They remain limited historical evidence.
The unchanged twelve interaction fixtures and new boot test must run in normal CI.

## Deployment and remaining work

Deploy both modified HTML fragments and the existing controller together, restart
the server for imported markup and reload browsers. No migration is required.
The include must occur exactly once after its Admin dependencies. Verify the live
button and connected player display, then review the remaining acceptance cases
in the TODO. Do not mark SG-TODO-003 complete before supporting validation.

README and root indexes were reviewed and remain accurate; this repair updates
the existing task and handover sections without changing their links. Modal help
still documents Next. SG-TODO-001/002 completion and deferred SG-TODO-004 remain
unchanged. No new successful full-suite or workflow result is claimed.
