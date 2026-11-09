# 370 - Focused live encounter workspace

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.6](../todo/090-admin-usability-redesign.md#sg-todo-0096---focused-live-encounter-workspace). Status: completed/closed after successful corrective CI and explicit renewed user sign-off/close request. The renewed acceptance supersedes the earlier revocation; it does not invent individually performed manual checks. Overall 009 remains in progress; 009.7 inspection/scoping begins at the user's request. 009.5/015 closure remains intact.

## Accepted final workflow

Battle, Characters, Monsters and Activity log retain full-width main-page flow. The duplicate participant overview/cards, split grid and sidebar space are removed. Native battleInfo current-turn access, fixed context/Next/End/Danger zone/Reset, original roster controls/selections and local overflow remain.

Campaign and Preparation expose independently available panel controls on their tab. Campaign Setup, Add Character, Add Monsters, setup and roster panels each respond only to their own toggle. Native dependency-map entries and parent-hidden CSS were retired; separate has-lair eligibility and workflow exclusion remain. Initial saved-context collapse/touched-before-response and renderer contracts remain. Successful Start/restart closes input/roster panes after accepted POST; failed Start keeps them; refresh/Next preserves manual reopening, with existing eligibility/ties/payloads/error and End/Reset behavior.

Encounter tools is an explicit Live-view popup using the original section/control nodes outside adminScroll. It retains target/effect drafts/files, native disclosures and scoped status/Undo/health/effect/checkpoint/backup operations. It is closed initially and not auto-opened by battle transitions. Internal scrolling, sticky Close, naming/ARIA, focus containment/inertness/return and busy/nested-modal guards remain; background inert flags are restored and backdrop clicks do not discard inputs. Actual target/campaign changes still apply original intentional draft-scoping rules. Independent lair controllers and activity disclosure/single visible heading remain.

No backend/permissions/schema/provider/socket/initiative/combat change was introduced by the final layout/control revision. Earlier campaign-scoped viewer metadata correction remains, excluding unauthorized/unselected/other-campaign/revoked/disconnected sockets and distinguishing unavailable from zero. Eight Admin source fragments, assembly size/hash and tracked failure marker remain untouched.

## Delivery and retained history

- Initial 8228b649c47f5df2b293608bd88e8153248c93bb and successful run 42627843410 attempt 1 covered the original, later superseded design.
- 110e210e16bcabe002718805443af807f210ef88 delivered compact sidebar/campaign-scoped viewer/log corrections.
- 73de987ba87fbc63af4766f379bdf366c13db80f delivered full-width rosters.
- 540ab598d65bb7002d3e8184e59cd5c596e2c90f replaced the sidebar/participant list with an on-demand tools dialog.
- 85c2cdfa365560d382522865aef41ba2ac65b2bc delivered independent controls and Start-collapse handling.
- e512dd24a42dde0141193e860b383125248f2f06 corrected the active-combatant Node VM fixture.

Detailed implementation/preparation measurements and failure diagnosis are retained in the [pre-close-out handover](https://github.com/dajomas/Scrying-Glass/blob/a7c7614f23acb7a502c3e8c48f579faacfe1fc12/docs/handover/370-live-encounter-workspace.md) and earlier immutable links there. Pending wording in that historical file is superseded by this dated close-out, not retroactively relabelled as evidence available during preparation.

## Failed run and fixture correction

Run 42649656592 attempt 1 on 85c2cdfa365560d382522865aef41ba2ac65b2bc failed overall. Publication 445f5d88dd54998a219974ebf1842a8cd590f6a6 contained ci-results-42649656592-attempt-1. Python/browser, syntax/import, pytest, standalone browser/audit and artifact steps succeeded, while JavaScript failed. Reader file-000038 part-000121/122 identified tests/encounter-active-combatant.test.cjs stopping with ReferenceError: window is not defined at the new busy accessor.

The fixture supplied document/fetch/FormData/Option but no browser global. Its correction sets context.window=context and asserts window===globalThis, an initialized busy getter and idle false. All original selection/manual override/monster/downed/dirty-field/lair/scope/no-turn assertions and early-return isolation remain. Production features code was not weakened or changed for the fix.

Before delivery, reconstructed full features.js and original test matched Git blob SHAs 140b87b5f4e55cfbedd33ce59c5780bfd289e732 and 18fbfd5c9b753b1b68d9d614cf3f087071d4c082. Node --test reproduced the old error and passed the corrected complete fixture: 1 TAP test, 0 failed, 0 skipped. That targeted DOM/HTTP mock result was not full-suite or live-server verification. The failed run remains historical failure; the later covering result below resolves the gate.

## SG-TODO-009.6 close-out - 2026-11-09

Verified successful corrective evidence:

- Workflow: Branch tests; run 42654298154, attempt 1, completed/success.
- Branch: features/perplexity.
- Tested SHA: e512dd24a42dde0141193e860b383125248f2f06.
- Publication SHA: a7c7614f23acb7a502c3e8c48f579faacfe1fc12.
- Evidence directory: ci-results-42654298154-attempt-1.
- Reviewed run.json/jobs.json confirm exact branch/SHA, successful test job and all configured validation stages: syntax/server import, Python suite including browser fixtures, pytest, JavaScript, standalone Python browser/audit checks and visual-artifact upload.

The user explicitly signed off on SG-TODO-009.6 after that verification and requested documentation closure and moving to 009.7. This renewed sign-off supersedes their earlier Admin-page verification revocation and supplies final overall acceptance for the revised full-width/dialog/independent-control scope. No remaining agreed 009.6 implementation item is identified. Do not carry old pending acceptance/CI text forward as a current blocker.

Evidence limits remain: fixtures use mocked/intercepted DOM/HTTP/state as documented; upload is not assistant screenshot inspection; overall user acceptance is not an invented checklist of individually executed viewer-count, keyboard, busy/nested, End/Reset or other manual scenarios. No new authenticated live TCP/provider, process-restart or exhaustive accessibility audit was performed for closure. These are evidence boundaries, not invented unfinished accepted requirements.

## Transition to SG-TODO-009.7

009.7 is in progress for inspection/scoping at the user's explicit move-on request; no application increment is delivered here. The [current task scope](../todo/090-admin-usability-redesign.md#sg-todo-0097---feedback-and-final-usability-hardening) retains actionable feedback/near-field validation, connection recovery, destructive confirmation and responsive/accessibility hardening. Preserve the accepted 009.6 layout and independent controls. Existing message-expiry changes require explicit review before implementation.

Initial live inspection read static/admin-notification-layout.js: it observes text in four pane notices and hides whitespace-only notices without changing messages/timers. Further global timer/error/Join-battle/connection/modal/test inspection and concrete behavior/acceptance planning remain. This source read is not an executed usability/accessibility audit. 016/017 stay proposed after 009.7; overall 009 is not closed by this transition.

## Documentation-only delivery

Update the root TODO/HANDOVER indexes, parent task and this section together. README was reviewed/reused and left unchanged because runtime descriptions remain accurate. Existing indexed paths and unrelated task statuses are retained. No application, tests, dependencies, runtime configuration or workflows change; no fresh tests are run. The proposed commit contains [skip ci]; no workflow is modified or separately dispatched and no close-out workflow outcome is inferred. No commit SHA is invented before delivery.
