# 220 - Initial Admin input visibility

[Back to handover index](../../HANDOVER.md)

## Completion - 2026-11-02

[SG-TODO-005](../todo/050-admin-initial-visibility.md) is completed at the user's
request after their green-CI confirmation on 2026-11-02 at 22:37 CET.
Implementation: ee9a4bd56439d8a5e7d5a94e5d9d1c1788c4c9e4, prepared against
6637a39ef21e0e035b849a7848ad0302c7ac7c33 on features/perplexity.

The user did not supply a workflow ID, logs or tested SHA with this confirmation.
Record user-reported CI success rather than inventing an independently verified
run or borrowing a previous task's workflow. Deployed first-opening/reload/manual
checks were not separately reported; closure records the user's CI-based acceptance,
not a claim that the assistant ran authenticated live checks. The former pending
status is superseded on this explicit acceptance basis. Documentation only; no
runtime, tests or workflow changes and no new test execution for this close-out.

## Accepted scope and user behavior

The user accepted related input groups: active campaign hides Campaign setup and
Character input; active saved setup hides Battle setup, Monster input and Lair
input. Battle controls, Character/Monster display and Activity log are unaffected.
This applies once after initial authoritative state on every page opening/reload,
not on each refresh or subsequent campaign/setup change. Manual Show/Hide choices
remain usable, including choices made while waiting for initial data. No stored
browser/database preference is introduced. False conditions keep existing defaults.

## Implementation

admin-initial-visibility.js is included once at the end of fragment 190 after
Admin/lair extensions, preserving the dependency order learned from SG-TODO-003.
It chains scryingLairsRender with receiver/arguments/return value preserved, then
initializes from the snapshot; it also catches up from latest if already populated.
No extra API requests, polling, MutationObservers or mutations are introduced.
Missing/malformed state waits for a later valid render. A valid null/null initial
state consumes the decision so a later activation does not unexpectedly collapse.

The script clicks only currently expanded, enabled existing input toggles. This
updates the Admin's own per-page hidden model, button label and aria-expanded;
it does not create conflicting hidden flags. A capture listener tracks any prior
non-initializer interaction per input. Already-collapsed inputs are left alone.
An enabled lair toggle can record the collapsed preference even when CSS hides
its button; the independent has-lair gate is not changed. The install guard makes
accidental repeat asset evaluation harmless. No large admin.js rewrite, server,
authorization, schema, configuration or migration changes are included.

## Validation evidence and boundaries

Eight focused Chromium unittest methods passed locally (four initial-condition
subtests included in that count). They cover cached/delayed/invalid state, manual
choices before/after initialization, later scopes, hidden lair controls, already
collapsed panes, no-active initial state and duplicate install. Pane handlers and
state transport are stubs; these are not full production-script integration checks.
Both prepared Python test sources compiled.

The separate test_admin_initial_visibility_page.py uses the real assembled HTML,
all real static scripts and intercepted HTTP with the established SQLite feature
fixture. It verifies real toggle/model integration and load(true) behavior, captures
pageerrors and forbids unexpected API mutations. The assistant did not run that
fixture or the full suite locally. User-confirmed green CI is recorded separately
above and does not turn mocked HTTP into authenticated live coverage. Existing
layout, visibility, setup/lair and complete-page smoke checks were left unchanged.

## Operation and continuity

Deploy the new script with the changed document-end fragment, restart and reload.
No migration or configuration change is needed. Per-page defaults do not imply
persistent browser preferences. README and HANDOVER.md index were reviewed and
remain accurate; the existing TODO index and section record completion. Other task
statuses, including the SG-TODO-004 hold, are unchanged. The next requested task is
SG-TODO-006; its XPBH/XPHB identifier discrepancy must be resolved before defaults
are implemented. No SG-TODO-006 runtime work is claimed by this close-out.
