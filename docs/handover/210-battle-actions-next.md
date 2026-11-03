# 210 - Next from Battle Actions

[Back to handover index](../../HANDOVER.md)

## Completion and backlog update - 2026-11-02

SG-TODO-003 is completed at the user's request after verified successful corrective
CI. Run 41525439558, attempt 1, tested 0759cc4b7bd78c4a7439c330d97c0661a6c4d864.
Inspected run.json is under ci-results-41525439558-attempt-1 at evidence commit
b49c1068301c505331ec0836e53dbf8a583771c6. It records completed success for syntax/
server import, unittest/browser, pytest, JavaScript and standalone browser/audit
steps, including the step that previously failed on the assembled-page smoke.
No test counts are invented from metadata. No new tests were run for this close-out.

The user's acceptance authorizes closure based on the successful run. Authenticated
live/player-display checks were not separately reported in this request and must
not be described as executed/passed. The prior acceptance checklist's manual
requirement is superseded for this user-requested CI-based close-out, not relabelled
as evidence. Fixture boundaries and same-browser concurrency limitations below
remain explicit. See [completed SG-TODO-003](../todo/030-battle-actions-next.md).

The same user request places [SG-TODO-004](../todo/040-dndbeyond-account-access.md)
on hold until further notice. Requirements and the underlying integration blocker
remain; do not resume that work without the user lifting the hold.

Three requested tasks are now indexed, not implemented:

- [SG-TODO-005](../todo/050-admin-initial-visibility.md): initial campaign/setup section visibility.
- [SG-TODO-006](../todo/060-fivetools-source-configuration.md): six configurable default sources and descriptive book/year names; preserve and resolve the literal XPBH versus X-prefix XPHB discrepancy before coding.
- [SG-TODO-007](../todo/070-monster-button-layout.md): single-line monster controls, retaining operations/accessibility and documenting responsive behavior.

This commit is documentation only: no runtime, config, test or workflow change.
No skip request was given for this update, so the proposed commit permits normal
CI. README and HANDOVER.md index remain accurate and unchanged; only the TODO
index gains new entries. Previous pending/failure notes below are historical.

## User workflow and implementation

Initial implementation: f9fa3c76b6f7c078b3d0a5c63679eea2892dff9a.
Script-order correction: 0759cc4b7bd78c4a7439c330d97c0661a6c4d864.

Next in Battle Actions discards pending drafts through normal Close, advances once
and opens the new active participant's ordinary action screen. It never submits
drafts, replays applied rows or undoes committed effects. Normal initial rows and
fresh actor/target/token context replace the old drafts. Apply and Close retain
their purpose. No active participant leaves the modal closed; lairs use the normal
openBattleActions delegation.

The deferred controller include occurs once in fragment 190 after admin.js and
other extensions. Parser-deferred execution sees interactive, so install runs
immediately; script order is a dependency contract, not guaranteed merely by defer.
The original early fragment-180 placement was incorrect. Controller logic and the
large admin.js were not rewritten by the script-order repair.

Both Next buttons use guarded composition of /api/battle/next and load(true),
with existing close/open helpers. The chained request helper tracks action POSTs
and advances; battleActionsApplying and disabled submits cover Apply/start-of-turn
refresh intervals. Capture-phase suppression blocks modal submissions during Next.
Controls restore prior disabled states. Preflight checks scope/actor; rendering and
fresh state must agree with returned actor, round and statistics token before
reopening. Conflicts leave no stale screen. Errors reconcile without automatic
POST retries, and discarded drafts are not restored.

No server, authorization, transaction, schema or turn/effect rules change. The
server owns round wrap, eligibility, expiry, persistence and broadcasts. Guards
are same-browser coordination, not server idempotency or cross-admin compare-and-
swap. Scope changes racing a request may still have the normal endpoint's effects;
no rollback or globally exactly-once claim is made.

## Historical CI failure and repair evidence

Run 41522989190, attempt 1, tested f9fa3c76. The failed evidence was inspected at
ci-results-41522989190-attempt-1 in b2b2023417489d73796cff1e99381d8cc609bd18;
use that historical commit because later evidence snapshots replace old folders.
Syntax/import, unittest/browser, pytest and JavaScript steps succeeded. The
standalone step failed at browser_smoke_272cc73.py's unchanged assertion with
admin: request is not defined (chunk 000096). The same chunk recorded an audit
rerun of 953 tests as OK and 647 connections with zero missing explicit close.
Those counts belong to the failed original run, not the successful corrective run.

The twelve isolated interaction fixtures supplied helpers before loading the
controller and missed page boot order. The added test_battle_actions_next_boot.py
uses actual modal/end fragments, parser-inserted deferred scripts, the real
controller and stub Admin helpers/other scripts. It checks no startup pageerrors,
a bound handler, one mutation and opening actor b. The unchanged complete assembled
page smoke remains a separate full-script integration gate.

The boot test passed locally after the move and failed with request is not defined
when the old order was restored. Reconstructed controller/end sources matched
Git blobs dfa305352daf297e87c018879fb48e9fbcb0effd and
cfaa08d1399f9208b74b9266d8ec81e0c7d8d4b9. Python test source compiled. Earlier five
local controller checks used stub normal helpers and did not exercise boot. These
are focused fixture results, not full authenticated server/player validation.
The previously pending corrective-CI status is superseded by run 41525439558 above.

## Deployment and retained limitations

Deploy both HTML fragments and the controller, restart the server for imported
markup and reload browsers. No migration is required. Unknown cross-client races
can prevent reopening. Browser fixtures use mocked transport/helper boundaries;
real authenticated use and connected-player behavior remain distinct from CI.
SG-TODO-001/002 completion is unchanged. The new proposed tasks do not silently
alter current visibility, source configuration/defaults or monster button layout.
