# 310 - Admin roster presentation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-009.4](../todo/090-admin-usability-redesign.md). Status: approved increment 1 included; covering CI and user acceptance pending. The user approved two commits: roster presentation/selection first, then SG-TODO-012 option 2 with read-only character current/max HP and editing through the existing Edit dialog. This first increment retains inline HP and does not complete 009.4 or implement 012/013.

## Included behaviour

Both rosters gain selected counts, Clear selection and selected-row outlines. Clear selection calls existing setAllSelected(kind,false), updating actual selection state, then focuses Select all. Bulk mutation options are disabled with zero selected; selection commands remain available and originally disabled options stay disabled. Counts describe the current unfiltered table; no search/filter or changed selection scope is introduced. Existing bulk operations and their confirmation/request logic remain intact.

Names gain concise In battle/Not in battle, Visible/Hidden and supplied life-state text. Status uses textContent and original state snapshots, not inferred replacement combat rules. Initiative controls gain combatant-specific accessible labels without keyboard remapping. Numeric cells use tabular figures; rows are vertically aligned. Character tables gain local scrolling and focus exposure like existing monster scrolling. Original row controls, column counts, names/species lines, initiative editors, inline character HP and removed HP-change columns remain.

## Implementation and deployment

New admin-rosters.js/.css are loaded after existing preview assets by the ordered document fragments. The module observes only each table container's direct child replacement, so row decoration does not recursively trigger itself. Selection context updates after pane click/change events via microtasks. Original controls and core handlers are not replaced; selection sets, APIs, persistence, permissions, pane preferences, lair gates, core assembly and failure marker remain unchanged. The installer is guarded against duplication. Character regions receive labels/tab focus and local focus scrolling; the existing monster focus handler is retained.

Deploy matching templates and the complete static tree, restart the correct process because HTML assembles at import, and reload browsers. No migration or new runtime dependency is needed.

## Validation and limits

Executed preparation: node --check, stylesheet parsing and regression Python AST parsing. Simplified real-Chromium fixture checks passed native option.disabled gating, selected count, actual selection-set clearing, focus return to Select all, unchanged inline 0/20 HP, existing Edit handler and idempotence with no page errors. During diagnostics the Playwright is_disabled helper disagreed with the native option.disabled property; regression assertions use the native property directly. No application selection logic was bypassed. These are synthetic fixtures, not full-Admin or authenticated-server execution.

Prepared tests/test_admin_rosters.py has three methods: source/asset/size contracts, actual full-Admin selection sets and refresh/Select dead/Clear selection, and desktop/narrow row controls/inline HP/character focus/idempotence/screenshots. Existing test_*.py CI discovery and SG_VISUAL_ARTIFACTS upload cover them without workflow changes. Expected new fixtures are 0094-1440-rosters.png and 0094-375-rosters.png. Full new module/suite/CI execution, screenshot generation/inspection and user acceptance remain pending.

The second approved commit remains outstanding: SG-TODO-012 removes inline character HP editors and supplies read-only current/max with editing via the existing dialog, save/reload coverage and corrected README/User Guide instructions. The first increment intentionally does not make that workflow change, so existing inline-HP instructions remain accurate. README and User Guide were reviewed and left unchanged for this increment. Search/filter, collection Add relocation, row expansion and alternative action menus were evaluated but not introduced; existing access/actions remain. Do not silently replace the accepted 11 single-line monster-row controls. Stage 013 navigation remains separate with boundaries unresolved.

TODO.md and the detailed 009.4 section record partial implementation and pending validation. HANDOVER.md links this section. The mixed commit omits [skip ci] and relies on normal push-triggered CI; no separate dispatch or unobserved result is claimed.
