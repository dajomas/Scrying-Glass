# 260 - Admin visual foundations

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-009.1](../todo/090-admin-usability-redesign.md).
Status: implementation included; CI/browser validation and user visual acceptance pending. Stages 009.2-009.7 are not implemented.

## Scope and decisions

The user agreed staged delivery and requested stage 009.1. The new static/admin-foundations.css scopes every rule to body.admin-shell and reuses the established glass-theme.css dark surfaces, gold, blue focus colour, local font stack and radii. It adds a 4/8/12/16/24/32 spacing token scale in rem units, common control-height/radius tokens, a brighter muted label colour, neutral outer panels, restrained teal/amber group borders/headings, tabular table numerals and quieter modal shadows. Product h1 branding remains unchanged; operational h2/h3 headings use the UI font.

The stylesheet loads after admin-shell.css and before monster-button-layout.css. Compact editor widths, local roster overflow, source assembly, all scripts, IDs, handlers, control order, action classifications, status colours and combatant/display colour values are unchanged. Checkboxes, radios, colour pickers and specialised icon/turn-order buttons are excluded from the generic control-height rule. Existing specialised ID-scoped component geometry retains precedence.

Deploy the matching template fragment and complete static tree, restart for imported HTML changes, then reload browsers. No database/configuration migration is required. README was reviewed and left unchanged because its dark/gold theme, layout/source and deployment descriptions remain accurate.

## Preparation evidence

Executed against the exact drafted CSS: tinycss2 parsed 17 rules with zero stylesheet/declaration errors; size 3,254 UTF-8 bytes. Python AST parsing passed for the 6,515-byte new test module. Its two source-contract methods passed against the drafted stylesheet and template in a temporary fixture, not a full checkout. These check asset order, Admin scoping, tokens, size and absence of visibility/width/overflow overrides.

Nominal sRGB contrast on panel #1a202c was computed: text #e6e2d6 12.60:1; muted #b1bacb 8.36:1; campaign #84c5c0 8.34:1; battle #d8b25a 8.11:1; focus #8fb7d8 7.72:1. These selected pairs are not a rendered/full accessibility audit or verification of every state.

No Playwright/browser fixture, authenticated live server, full suite or workflow run was executed during preparation. No screenshots have yet been captured or visually reviewed. Do not infer CI success from workflow configuration or commit delivery.

## Prepared regression and screenshot coverage

The new tests/test_admin_foundations.py reuses the established intercepted-HTTP full-Admin fixture without inheriting its test cases. At 1440/375 viewport widths it checks unchanged pane/form/action/colour state across stylesheet enable/disable, unsaved character-name retention, 11 monster buttons, absent row HP buttons, computed panel/modal tokens and keyboard focus, plus page errors and non-GET mutations. Existing roster geometry, focus exposure, refresh, initial visibility, compact-input and shell tests are retained unchanged.

Before/after screenshots use the same fixture DOM and manually opened input panes; baseline disables only the new stylesheet. CI unittest discovery includes the module. The workflow gives that step SG_VISUAL_ARTIFACTS in runner.temp and uploads admin-foundations-visual-fixtures after it, including after a preceding failure unless cancelled. Missing files produce an artifact warning, not visual validation. The standalone audit may rerun unittest and writes its separate screenshots to the system temporary directory. Local callers may set SG_VISUAL_ARTIFACTS to retain screenshots elsewhere.

## Outstanding review

Review covering CI and screenshot evidence before declaring 009.1 validated. Check representative campaign/setup states, manual pane choices, fixed header/message/workspace separation, compact editors, row scrolling/focus, modal geometry and colour semantics at desktop/narrow widths and zoom. Full encounter operations, delayed/failed requests, lair gating and authenticated deployment are not newly established by the visual fixture. Obtain user visual/workflow acceptance before completion or structural redesign.

Normal push-triggered CI is intended; no skip marker or separate workflow dispatch is included. The existing CI handover remains the general suite reference; this section records the new screenshot upload configuration. No commit SHA or workflow identifier is invented before it exists.
