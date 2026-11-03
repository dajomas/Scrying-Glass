# 060 - 5e.tools sources and descriptive names

[Back to TODO index](../../TODO.md)

## SG-TODO-006 - Expand configurable 5e.tools defaults and display book names

- Status: in progress; stage 1 and stage 2A delivered; stage 2B popup labels/browser regressions prepared, delivery/CI/live validation pending.
- Requested: 2026-11-02. Original two-stage delivery approved: 2026-11-02.
- Remaining UI stage split into two commits approved: 2026-11-03.
- Priority, owner and deadline: not assigned.
- Stage 2A: c49a890d198098622f40f1d22e5e92db6e8914c4 on features/perplexity.
- Current preparation base: the stage-2A commit above.
- Identifier decision: user corrected XPBH to XPHB on 2026-11-02.

### Agreed delivery and compatibility

1. Configuration/providers/tests/docs: delivered.
2A. Notification labels/shared formatter/source guards/tests/docs: delivered.
2B. Popup labels using the same formatter, browser regressions/final docs: prepared.
Each write needs bound approval and normal CI. Implementation delivery alone is not
validation or task closure. SG-TODO-004 stays on hold and is not a dependency here.

Omitted display.fivetools_sources uses MM, XMM, PHB, XPHB, DMG, XDMG, in order.
Explicit lists replace defaults; duplicates retain first occurrence. [] searches no
5e.tools source/index without disabling D&D Beyond. IDs are case-sensitive nonempty
strings without surrounding whitespace; max 32 input entries. Invalid/null/scalar/
malformed settings or display mappings fail loading. Existing MM/XMM overrides
remain restricted; remove/expand and restart for all six. No migration, new key,
credentials, data bundling or provider-order change.

| Identifier | Exact label |
|---|---|
| MM | Monster Manuals 2014 |
| XMM | Monster Manuals 2024 |
| PHB | Player Handbook 2014 |
| XPHB | Player Handbook 2024 |
| DMG | Dungeon Master Guide 2014 |
| XDMG | Dungeon Master Guide 2024 |

Notifications and popup choices use these names. Raw IDs in URLs, matching,
deduplication, responses and selected-candidate tokens remain unchanged. Custom IDs
stay raw without guessed names/year; missing popup sources use Source unavailable.
D&D Beyond notification and popup edition wording is unchanged.

### Validation and remaining acceptance

Stage 1 had twelve local offline helper/config/candidate checks. All six upstream
index entries were found; live usable stats/images remain unverified. Stage 2A had
seven source/reader/runner methods and three Node subtests pass locally. Its CI has
not been inspected. See [handover](../handover/230-fivetools-sources.md) for provenance.

Stage 2B has seven candidate-browser tests (four retained, three added) and three
unchanged typing/focus tests pass locally in Chromium with intercepted HTTP. Checks
cover exact labels, unknown/prototype/HTML-like fallback, untouched source links/raw
response/token, selected AC/HP, notifications, cancel/Escape/focus, pending submits,
edits and no extra lookups. Syntax/compilation passed. This is fixture coverage, not
authenticated full-server or live-provider verification. Stage-2A unit checks were
not rerun for 2B. Full CI and authorized live/browser acceptance remain pending.

- [x] User confirmed XPHB.
- [x] User agreed separate notification/popup commits.
- [x] Deliver notification-label increment (stage 2A).
- [ ] Deliver popup increment after exact bound approval and record actual SHA.
- [ ] Review complete exact-SHA regression CI for the combined implementation.
- [ ] Verify actual live stats/images and browser behavior for configured sources.
- [ ] Obtain acceptance before marking SG-TODO-006 completed.

README guidance now covers both label surfaces. Backend/provider/API behavior,
schema, configuration and raw identity remain unchanged in stage 2B.
