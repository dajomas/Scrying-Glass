# 220 - Initial Admin input visibility

[Back to handover index](../../HANDOVER.md)

Prepared: 2026-11-02 against 6637a39ef21e0e035b849a7848ad0302c7ac7c33.
Task: [SG-TODO-005](../todo/050-admin-initial-visibility.md), in progress.

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

## Validation and delivery status

Eight focused Chromium unittest methods passed locally (four initial-condition
subtests included in that count). They cover cached/delayed/invalid state, manual
choices before/after initialization, later scopes, hidden lair controls, already
collapsed panes, no-active initial state and duplicate install. Pane handlers and
state transport are stubs; these are not full production-script integration checks.
Both prepared Python test sources compiled.

The separate test_admin_initial_visibility_page.py uses the real assembled HTML,
all real static scripts and intercepted HTTP with the established SQLite feature
fixture. It verifies real toggle/model integration and load(true) behavior, captures
pageerrors and forbids unexpected API mutations. That fixture and full suite remain
pending CI; neither a passing application integration nor authenticated live run
is claimed. Existing layout, visibility, setup/lair and complete-page smoke checks
remain unchanged and must run normally. No workflow changes or skip marker.

Deploy the new script with the changed document-end fragment, restart and reload.
After CI review, manually test a saved active campaign/setup, unsaved setup, reload
and manual reopening. Keep SG-TODO-005 open until acceptance is reviewed. README
was reviewed; its general Admin description remains accurate. Detailed behavior
is documented here and in the linked task, with root indexes updated. Other tasks
and the SG-TODO-004 hold remain unchanged.
