# 320 - Initiative keyboard navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-013](../todo/130-initiative-keyboard-navigation.md).
Status: wrapping/Escape correction included; covering local/CI and acceptance pending.
Initial delivery: d23ee70d6beea3f6c5031f0102c27e5f537edbc8. Correction base:
5992362c478c7763432268b8fd0b33d72140ddab; relevant tree/blob identities match d23ee70.

## Current decision and implementation

The user initially approved native first/last exit, then reported it unintuitive
and requested first/last wrapping. They approved Escape as the loop exit. The
current rule is within-roster, displayed-row-order cyclic Tab/Shift+Tab, never a
forced jump between Characters and Monsters. Single-editor Tab stays on that field.
Hidden/disabled/readonly/inert/negative-tabindex fields are skipped; modified keys
and composition remain native. Empty rosters do not intercept navigation.

Escape from an initiative editor focuses the roster scroll region, clears the
refresh anchor and enables normal Tab/Shift+Tab within that roster. This pass-
through survives table replacement, so Tab through the first editor can reach Edit
and other controls instead of re-entering the loop immediately. Leaving/re-entering
the roster or pointer interaction re-enables looping. The enhancement supplies a
tabindex only if the region lacks one; existing roster labels/focus remain.

The enhancement still loads after character-hp-display.js and observes only direct
table replacement. Its navigation anchor identifies destination combatant and
campaign/setup, restoring focus after reorder only if the old node disconnected
and focus fell to body/region. Pointer/external focus, window blur, changed scope
or missing destination cancel restoration; Escape explicitly cancels it as well.
Existing local focus exposure is retained, and installation is idempotent.

WeakMaps retain destination drafts and track emitted/attempted values. A restored
draft missing native change emits one bubbling change in a blur microtask through
the original delegated handler; native change clears the fallback, and attempt
tracking propagates across replacements to avoid replay/automatic rejected-value
retry. No network code, replacement save API, validation or combat-order rule is
added. Admin core fragments, marker/assembly identities, backend rules, permissions,
HP workflow and Turn removal remain unchanged. This is not 009.5 navigation.

## Validation, history and limits

Initial preparation passed syntax/AST and five isolated Chromium methods. An
intermediate duplicate-change assertion exposed a defect, corrected by propagating
attempt tracking before all five methods passed. Those original checks and the
initially prepared seven-method suite did not validate the later wrapping change.

Correction preparation passed node --check, regression AST parsing and all five
updated isolated Chromium methods. They cover 1440/375 navigation in both rosters,
forward/reverse wrap, Escape to region, normal forward/reverse navigation after
Escape, pass-through across rerender, re-entry/pointer reactivation, single/empty/
unavailable fields, modifier noninterception, refresh identity/drafts, exact change
counts, missing-change fallback and pointer/scope/deletion cancellation. These are
isolated DOM fixtures, not the full application or an authenticated server.

The module now prepares three additional full-Admin methods: asset/order/size,
native change/PATCH/save-refresh/rejected-fraction checks, and new single-editor
wrapping/Escape/checkbox/initiative/Edit access at 1440/375 in both rosters. HTTP
state and saves are intercepted, not real storage or backend validation. Those
three methods and the complete application suite were not executed in correction
preparation. Existing CI test_*.py discovery covers all eight without workflow edits.
Covering local/CI results and user workflow acceptance remain pending for this
revision; no CI pass or triggered-run state is inferred. Normal push-triggered CI
is allowed by omitting [skip ci], with no separate dispatch.

Deploy the full matching static tree, reload Admin browsers and retain matching
templates; no migration/dependency change is needed. User Guide and task/index now
state wrapping/Escape, superseding native-boundary exit. README and HANDOVER index
were reviewed/reused and remain accurate without edits. 009.4/012 remain closed;
013 stays in progress. Preparation notes are not a claim of live persistence,
exhaustive screen-reader testing or full manual combat acceptance.
