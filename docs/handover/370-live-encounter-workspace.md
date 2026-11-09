# 370 - Focused live encounter workspace

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.6](../todo/090-admin-usability-redesign.md#sg-todo-0096---focused-live-encounter-workspace). Status: revised full-width/dialog code, tests and documentation prepared for bound approval. The user revoked Admin-page verification and then replaced the sidebar/participant-list direction. Covering CI and renewed acceptance remain pending. Overall 009 stays in progress; 009.7 stays proposed; 009.5/015 remain closed.

## Revised user workflow

Battle, Characters, Monsters and Activity log keep their original full-width main-page flow. The duplicate Participants in turn order overview, readonly cards, split grid and reserved sidebar space are removed. Native battleInfo order/current-turn action access remains, as do fixed header context, Next, End and Danger zone/Reset. Original roster nodes, visibility preferences, selections, single-line actions and local overflow remain in place rather than being moved between columns.

Encounter tools is an on-demand Live-view popup opened by the existing button. It is closed initially and battle transitions/refresh do not open it. The original encounterFeatures section moves once into a named dialog outside adminScroll, preserving form nodes/IDs/handlers, target/effect drafts, input files, native disclosures and scoped viewer/Undo/health/effect/checkpoint/backup actions. Close/reopen does not save/reset/rebuild controls. Independent lair tools/controllers and modal actions stay in their original location.

The dialog scrolls internally within the viewport, has a sticky Close, role/aria-modal/name, focus containment, background inertness and focus return. Escape is captured only when the parent dialog is topmost. A running existing tools operation or visible nested modal blocks parent dismissal; existing nested overlays remain interactive above the dialog. Background inert flags are restored to their original values on close. Clicking the backdrop does not dismiss or discard drafts. Existing state refresh may still intentionally reset target-scoped drafts when the actual target/campaign changes, as before.

## Controller and integration changes

static/admin-live-workspace.js no longer wraps the state renderer or moves Battle/rosters/lair sections. It creates only the tools dialog and retained activity-log disclosure; installation is guarded. The old inline UI controller is replaced in encounter-visibility.js with the original opener delegating to the dialog; updateEncounterToolsVisibility remains a non-opening compatibility function so core load calls do not change. The pure createEncounterVisibility helper is retained for compatibility but is not used by the Admin shell.

Navigation records the original opener's workflow filter before the dialog changes aria-controls, preserving the Live-only mapping without cloning buttons. Original input/roster collapse and independent lair gates are unaffected. features.js adds only window.scryingEncounterToolsBusy as a readonly getter of the existing busy flag; save/error/refresh behavior, scopes, polling, payloads and campaign-scoped connection correction remain unchanged.

CSS removes the split geometry and constrains the popup, with compact natural-height connection status and nested-overlay layering. It retains the single visible log heading. Workspace CSS/JS and features JS are version 3; visibility JS is version 2. No backend, API, permissions, grants, schema, socket protocol, initiative or combat change is included. Eight Admin core fragments and tracked failure marker remain untouched.

## Executed preparation versus pending tests

Executed: Node syntax checks for the complete 5,704-byte workspace and 1,387-byte visibility modules, parsing the 1,378-byte stylesheet, and AST parsing of all four updated Python browser regression files. Small Node checks confirmed the retained helper's initial/transition/restoration compatibility. The unchanged large features module was inspected; its new getter and full module are not claimed executed here.

Isolated real Chromium checks at 1440/375 loaded the proposed workspace/visibility/CSS against synthetic DOM/state. They passed absence of split/list, tools outside main, default-closed and non-auto-open behavior, dialog bounds (960px desktop, 352.5px narrow in those fixtures), internal overflow, focus return/background inertness, draft retention, busy/nested close guards and repeated-installation safety, with no page errors. The busy getter was stubbed for those checks; they are not actual saves, full Admin, authenticated server or backend evidence.

Prepared full-Admin/intercepted-HTTP regression updates:

- test_admin_live_workspace.py: full-width Battle/log and no duplicate overview; default-closed/tools geometry screenshots; original control/draft/focus/inert/idempotence checks; held feature-save request blocks Close/Escape, nested modal dismissal, native Next single request/Battle Actions and history persistence.
- test_live_roster_widths.py: equal Battle/Characters/Monsters/log edges with popup closed/open/refreshed at 1440/768/375, plus unchanged native parents/preferences/selections across tabs.
- test_live_sidebar_corrections.py: compact connection status in the popup, single log heading/buttons, one/zero/unavailable/failure/recovery rendering. The old forced sidebar-stack expectation is superseded by the requested wider popup.
- test_admin_workflow_navigation.py: retain mapping/forms/drafts/selections/manual roster collapse/keyboard tabs/lair/header checks; replace automatic inline-tools opening with explicit dialog choice across battle start/round/end refreshes without tab stealing.

These complete modules and the full existing suite were not run locally. Existing CI discovery and SG_VISUAL_ARTIFACTS collection cover them; revised captures are 0096-WIDTH-full-width-main.png and 0096-WIDTH-tools-dialog.png. No workflow changes or skip marker. Obsolete UI expectations are explicitly replaced, not silently skipped; backend viewer-isolation and unrelated combat/security tests are retained.

## Historical delivery and superseded design

Initial 8228b649c47f5df2b293608bd88e8153248c93bb had successful Branch tests 42627843410 attempt 1, published at a9e6b1bc321596eff2d660a80cc7d35f7b5fc9a6. That result covers the old design only. 110e210e16bcabe002718805443af807f210ef88 introduced compact sidebar/viewer-status/log corrections; 73de987ba87fbc63af4766f379bdf366c13db80f delivered full-width rosters. No new covering outcome is invented for the revision.

Detailed initial implementation, image review, revocation, correction rationale and prior preparation measurements are retained in the [pre-dialog handover](https://github.com/dajomas/Scrying-Glass/blob/73de987ba87fbc63af4766f379bdf366c13db80f/docs/handover/370-live-encounter-workspace.md). The user's later request removes the redundant participant list and sidebar because they add insufficient value. Previously positive comments are not renewed acceptance. The new dialog supersedes old inline auto-opening and tools-restoration expectations, not lair behavior or campaign privacy.

## Remaining gates and deployment

Review covering CI/fresh main and popup screenshots; verify actual campaign display status and real tool operations; obtain renewed desktop/narrow/keyboard acceptance including drafts, busy/nested closing, focus, roster controls, Next/End/Reset, Battle Actions/Next, history and independent lairs. Do not close on code preparation/push/older CI alone. No new password-login, live TCP/provider, process-restart or exhaustive accessibility verification is claimed.

Deploy matching static files and template, restart the process for assembled HTML and reload Admin; no migration/configuration change. README, root indexes and existing documentation were reviewed/reused; generic runtime descriptions, links and in-progress status remain accurate without cosmetic edits. Task/this section are updated together. No unrelated task is started/closed and no implementation SHA is invented before delivery.
