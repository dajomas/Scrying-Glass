# 350 - Admin workflow navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.5](../todo/095-admin-workflow-navigation.md).
Status: implementation delivered in 1beff730580b17551ae5c95115ad31badf39b3f1; first covering CI failed. Corrective stage 1 of 2 is prepared; corrected execution, covering CI and user acceptance remain pending. Do not mark completed from a commit alone.

## Agreed approach and destinations

The user accepted a compact three-view layer retaining the existing pane controls, DOM, form drafts and independent visibility state. Preparation uses features/perplexity after SG-TODO-018 was merged at b0630effbe99db8a40b27bb00cca007b198d4055. No initiative rules, source refresh semantics, API, permissions or persistence change here.

- Campaign: campaign selection/access/backups, Add character and Characters roster.
- Battle preparation: saved setups/background/imports, Add monsters, both rosters for participation/initiative, and lair configuration subject to existing gates.
- Live encounter: both existing rosters, encounter tools, lair controls and activity log. This does not filter rosters or implement 009.6's focused participant layout.
- Shared: the existing Battle/order/Danger zone section remains available in every view; header context, Start/Next/End, More/logout/viewer controls and global feedback stay available.

The existing View panels strip shows controls applicable to the selected view. Native dependent-button rules and lair gating still apply. Hidden input panes may need opening through their existing controls. A workflow tab never opens a collapsed pane, joins combatants, saves, starts/ends/resets a battle or applies an action.

## State and accessibility

Campaign is the stable initial view on every page load; no saved tab preference or auto-switch on battle transitions is added. Refresh/rerender does not change the chosen view. Existing per-page initial collapse and automatic battle collapse/restoration remain authoritative, including their existing supersession of manual state on battle transitions. Encounter tools still auto-show for a battle and restore their prior preference afterward, independently of the selected workflow.

The view layer writes data-workflow-excluded, never pane.hidden or controller aria-expanded. Scoped display:none excludes out-of-view panes and controls from rendering and focus without cloning/reparenting forms. Original listeners, file inputs, drafts and selection sets remain in place. No polling, fetch, synthetic toggle clicks, renderer replacement or state mutation is introduced.

Tabs use role=tab, aria-selected and roving tabindex, with Left/Right wrapping and Home/End. Click/keyboard selection retains focus on the selected tab. The existing main becomes the shared tabpanel labelled by the active tab. Each view remembers its scroll offset within that page. Narrow screens use a locally scrolling tab strip with exposed focused tabs. Missing prerequisites leave the prior UI intact; installation is idempotent.

## Delivery and original preparation

New assets load after existing enhancements in 190_document_end.html and install at DOMContentLoaded, after prior form/backup setup. Deploy the matching template and full static tree, restart the correct server because HTML assembles at import, and reload Admin. The eight core fragments, assembly and failure marker are unchanged.

The navigation regression module uses the existing full-page intercepted-HTTP fixture and production assets. It targets destination mapping, unchanged native hidden flags/node identity, drafts/selection/manual collapse, keyboard/ARIA/idempotence, refresh/tab stability, encounter-tools restoration, lair-disabled gating and fixed-header boundaries. It prepares six screenshots at 1440/375 through SG_VISUAL_ARTIFACTS. Existing unittest discovery and artifact upload include this test and its images; no CI workflow change is required.

No tests, syntax checks or browser screenshots were executed during original implementation preparation. Full start/end/reset interactions, lair-enabled/parent-dependent scenarios, delayed/failed initial state, file-input retention, source-refresh/modal continuation, actual initiative saves, keyboard initiative restoration and authenticated desktop/narrow visual/workflow acceptance still require execution/review. Fixture coverage is not a live provider, password-login, TCP server, process-restart or exhaustive accessibility audit.

README and User Guide were reviewed: existing deployment, HP and initiative contracts remain unchanged. This section and the linked navigation task document the destinations. Existing historical 090 planning remains available; the dedicated 095 entry is authoritative for the current 009.5 agreement and status.

## First covering CI and approved correction split - 2026-11-09

Branch tests 42586178034 attempt 1 tested exact 1beff730580b17551ae5c95115ad31badf39b3f1 on features/perplexity and completed/failure. Evidence publication c01beaf5dcfdb931ab1c2a271e717f02cc7d4b6b contains ci-results-42586178034-attempt-1. Main suite and repeated connection-audit suite each report 1,416 tests with 31 failures and 31 errors; the repeated audit is not another independent set of defects. It reports 762 opened connections, zero without explicit close. Dependencies, syntax/server import, pytest and JavaScript steps succeeded. Eighteen screenshots were uploaded, including six navigation images; collection is not assistant visual inspection.

Inspected traces show out-of-view setup/monster controls, inaccessible monster regions, zero visible row counts/geometry, cross-view notice/focus assumptions and secured Refresh setup interactions without destination selection. Four of five new navigation methods passed. Tools restoration failed because the original test sampled an already battle-forced visible value, rather than establishing an inactive preference. Do not infer that every failure is fixture-only before corrective coverage has run.

The user approved two corrective commits. Stage 1 changes only shared roster fixture entry, explicit header/navigation entry and deterministic tools restoration, plus this handover/task status. The shared fixture asserts the initial Campaign tab before selecting Battle preparation through its actual button; consumers can explicitly choose Campaign or retain the untouched initial view with workflow=None. No production script is blocked, controller state forced or original roster assertion removed. Header tests explicitly choose Campaign. Navigation tests retain and assert production Campaign startup.

Tools restoration now controls the intercepted state response, awaits actual load(true) completion, establishes inactive state and a known open/closed preference via the existing toggle, then covers active rounds, off-view filtering, inactive restoration and repeated refresh at 1440/375. No server mutation is generated by these staged state responses.

Executed corrective preparation: Python AST parsing of the four changed method/signature snippets passed. Complete replacement modules, Chromium methods, full suite and corrected CI were not executed here; snippet parsing is not module or browser validation. Existing workflow discovery covers the changed test modules.

Stage 1 is partial: foundation/form tests still need per-view setup and geometry/notice traversal, and the secured Refresh fixture still needs explicit preparation navigation. The shared fixture's new preparation default also requires the foundation character-draft path to explicitly choose Campaign in stage 2. A stage-1-only full run may therefore remain red. Stage 2 retains original draft/file/save/rejection/layout and secured Apply assertions. No closure, corrected pass count or new workflow outcome is claimed. No production code, workflows or combat rules change in stage 1. README and root index contents were verified/reused and left unchanged; detailed current status is in the linked task and this section.
