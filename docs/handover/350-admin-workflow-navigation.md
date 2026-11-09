# 350 - Admin workflow navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.5](../todo/095-admin-workflow-navigation.md).
Status: implementation prepared; external write, execution, covering CI and user acceptance pending. Do not mark completed from a commit alone.

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

## Delivery and validation

New assets load after existing enhancements in 190_document_end.html and install at DOMContentLoaded, after prior form/backup setup. Deploy the matching template and full static tree, restart the correct server because HTML assembles at import, and reload Admin. The eight core fragments, assembly and failure marker are unchanged.

Prepared tests/test_admin_workflow_navigation.py uses the existing full-page intercepted-HTTP fixture and production assets. It targets destination mapping, unchanged native hidden flags/node identity, drafts/selection/manual collapse, keyboard/ARIA/idempotence, refresh/tab stability, encounter-tools restoration, lair-disabled gating and fixed-header boundaries. It prepares six screenshots at 1440/375 through SG_VISUAL_ARTIFACTS. Existing unittest discovery and artifact upload include this test and its images; no CI workflow change is required.

No tests, syntax checks or browser screenshots were executed during this preparation. CI status and screenshot appearance are not claimed. Full start/end/reset interactions, lair-enabled/parent-dependent scenarios, delayed/failed initial state, file-input retention, source-refresh/modal continuation, actual initiative saves, keyboard initiative restoration and authenticated desktop/narrow visual/workflow acceptance still need execution/review. Fixture coverage is not a live provider, password-login, TCP server, process-restart or exhaustive accessibility audit.

Known compatibility review: older all-panel browser tests may need explicit workflow selection now that production navigation scopes panes. Do not remove assertions, force hidden controls or disable production navigation merely to make them pass. Review failures against the new destination contract and retain their original behavioral checks. Existing fixture tests have not been changed or executed in this proposal.

README and User Guide were reviewed: existing deployment, HP and initiative contracts remain unchanged. This section and the linked navigation task document the new destinations. Existing historical 090 planning remains available; the dedicated 095 entry is authoritative for the current 009.5 agreement and status.
