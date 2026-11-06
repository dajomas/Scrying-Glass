# 310 - Admin roster presentation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Tasks: [SG-TODO-009.4](../todo/090-admin-usability-redesign.md) and [SG-TODO-012](../todo/120-character-hp-editors.md). Status: the two approved increments are included; neither task is closed. Increment 1 supplied roster presentation/selection; increment 2 implements the selected option 2, read-only character HP with editing through the existing Edit dialog. This current status supersedes the earlier increment-1-only pending-HP descriptions in the 009.4 delivery history. SG-TODO-013 and later redesign phases are not implemented. The subsequent requested Turn-control removal is included with its own validation pending below.

## Included behaviour

Both rosters have selected counts, Clear selection and selected-row outlines. Clear selection calls existing setAllSelected(kind,false), updating actual selection state, then focuses Select all. Bulk mutation options are disabled with zero selected; selection commands remain available and originally disabled options stay disabled. Counts describe the unfiltered table; search/filter, collection Add relocation, row expansion and action menus were considered but not introduced. Existing bulk confirmations/requests and single-line monster-row layout remain; the user subsequently removed Turn, leaving 10 visible monster-row and 7 visible character-row buttons.

Names show supplied battle/visibility/life-state text through textContent, not replacement combat rules. Initiative controls retain combatant-specific accessible labels without keyboard remapping. Numeric cells use tabular figures; rows align vertically. Character tables have local scrolling/focus exposure; monster scrolling remains. Removed row Damage/Heal controls and HP-change columns remain removed.

Characters now show current/max HP as text, like Monsters. Use existing Edit, change Current HP and/or Max HP, then Save character. The character-hp-display.js enhancement runs after admin-rosters.js, replacing only matching HP input pairs in character cells. Its observer watches direct roster child replacement, not subtree decoration, avoiding self-triggered loops. It is guarded against duplicate installation and makes no network request. Original Edit/save/validation handlers, inline initiative, selection, APIs, permissions, HP rules and persistence remain unchanged. Existing generated inline-HP markup and dormant delegated handlers remain in the unchanged assembled core; the loaded enhancement removes those inputs from the interactive roster.

## Deployment

Deploy matching templates and the complete static tree, restart the correct process because HTML assembles at import, and reload browsers. Include the new character-hp-display.js asset and updated admin-rosters.css. No migration, new runtime dependency, core-assembly identity change or failure-marker replacement is needed. README and User Guide explain the Edit-dialog HP workflow. Technical compact-input documentation describes the retained stylesheet selectors; they no longer imply active roster HP editors when this enhancement is loaded. HANDOVER.md links remain accurate and unchanged.

## Requested Turn-control removal - 2026-11-06

The user requested removing Turn for both Monsters and Characters. Scoped rules
in the already loaded admin-rosters.css apply display:none to roster button[data-mt]
and button[data-ct]. This excludes those controls from display, keyboard tab order
and accessible button queries, including newly rendered rows. It deliberately
retains legacy DOM and delegated turn API handlers; it is not a permission/API
restriction. Other controls, initiative editing, Start/Next/End, turn highlighting
and automatic progression are unchanged. There is no state mutation or observer.

Preparation passed stylesheet parsing and a simplified Chromium fixture at
1440/768/375 pixels, with three replacements per width, inaccessible Turn controls,
forward/reverse focus skipping Turn, retained Next and zero mutations. Full-Admin
regressions now measure 10 visible monster controls, traverse 10 forward/9 reverse,
and assert no accessible Turn in either roster plus 10/7 visible controls after
refresh. Other fixtures' raw DOM counts remain valid because the legacy buttons
remain in the DOM; they are not visible-control counts. Full application/local/CI
execution and live workflow acceptance remain pending for this follow-up.

README and the existing 007 task section record the new scope; 007's original
closure and old 11-button history are not new validation evidence. User Guide,
root indexes and CI workflow were reviewed/reused and remain accurate without
changes. Normal push-triggered CI is configured to discover the updated tests;
this mixed commit omits [skip ci], with no dispatch or unobserved result claimed.

## Increment 1 preparation and local evidence

Original preparation passed JavaScript syntax, stylesheet parsing and regression Python AST parsing. Simplified Chromium checks covered native option.disabled gating, selected count, actual selection clearing, focus return, inline 0/20 HP, retained Edit and idempotence without page errors. Playwright is_disabled disagreed with native option.disabled during diagnostics; regressions use the native property, without bypassing selection logic. These were synthetic fixtures, not authenticated-server tests.

The user published completed local evidence for 720f8763708e9574f905d0ee946c0c5d70174d19 at 2aec821063fca27d9aad2aff3eb51d872cf5ec58, under local-tests-720f876/run-20261106T181310Z-I8wUpT. Reviewed environment/summary/exit records report completed=1 and overall/all 48 command exits zero. Pytest reports 43 passes; the complete connection-audit log reports 1,064 tests OK, 680 connections opened and zero without explicit close. Mocked provider exception tracebacks end in OK/PASS, not test failures. This evidence predates increment 2; it must not be represented as its validation or live-server acceptance.

## Increment 2 preparation and pending validation

Executed: node --check on the new JavaScript and AST parsing of the new regression module; both passed. A simplified real-Chromium fixture passed zero HP, large values, zero maximum, table replacement, duplicate installation, unchanged initiative/dialog inputs and retained Edit click, with no page errors. Preparation harness issues with notebook sync Playwright and evaluate returning a callback were corrected before the passing async fixture; they did not require application changes.

Prepared tests/test_character_hp_display.py covers asset/order/size contracts and full-Admin intercepted-HTTP Edit rejection, retained draft, native invalid maximum, retry, 0/20 save and full page reload at 1440/375 widths. Reload reads mock-backed state, not a real database. Existing tests/test_admin_rosters.py expects read-only HP while retaining selection, original controls, initiative, focus, idempotence and screenshots 0094-1440-rosters.png/0094-375-rosters.png.

The existing test_*.py CI discovery and SG_VISUAL_ARTIFACTS upload cover these tests/images without workflow changes. Full-Admin regression execution, covering local/CI results, fresh screenshot generation/inspection, real persisted save/reload and user visual/workflow acceptance remain pending for increment 2. The mixed commit omits [skip ci] and relies on normal push-triggered CI; no dispatch or unobserved CI result is claimed. Obtain acceptance and review remaining criteria before closing 009.4/012. Stage 013 and later navigation remain separate.
