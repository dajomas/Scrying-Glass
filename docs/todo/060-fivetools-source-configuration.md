# 060 - 5e.tools sources and descriptive names

[Back to TODO index](../../TODO.md)

## SG-TODO-006 - Expand configurable 5e.tools defaults and display book names

- Status: in progress; stage 1 delivered; UI stage 2A notifications prepared, approval/CI pending; stage 2B popup names pending.
- Requested: 2026-11-02. Original two-stage delivery approved: 2026-11-02.
- Remaining stage 2 split into two coherent commits approved: 2026-11-03.
- Priority, owner and deadline: not assigned.
- Current preparation base: 24a7c18ead4203d21aa79f2b740a51799d3ef118.
- Identifier decision: user corrected XPBH to XPHB on 2026-11-02.

### Agreed delivery

1. Configuration/providers/tests/docs: already delivered; raw codes remain internal.
2A. Descriptive notification labels and shared formatter, source guards/tests/docs.
2B. Popup labels using that formatter, browser regressions and final docs.

The extra UI staging was agreed before writes. Each commit needs bound approval
and normal CI; do not treat plan approval as authorization for an external write.
2A deliberately leaves popup choices raw. Neither it nor stage 1 completes this task.
SG-TODO-004 remains on hold and is not a dependency for public-provider work.

### Source configuration and compatibility

Omitted display.fivetools_sources uses MM, XMM, PHB, XPHB, DMG, XDMG, in order.
Explicit lists replace rather than append; duplicates retain first occurrence.
[] searches no 5e.tools source and does not fetch its index, without disabling
D&D Beyond. IDs are case-sensitive nonempty strings without surrounding whitespace,
maximum 32 input entries. Null/scalar/malformed values or invalid display mappings
fail configuration loading. Existing MM/XMM overrides remain restricted; remove or
expand and restart to opt into all six. No migration, new key or provider-order change.

| Identifier | Exact label |
|---|---|
| MM | Monster Manuals 2014 |
| XMM | Monster Manuals 2024 |
| PHB | Player Handbook 2014 |
| XPHB | Player Handbook 2024 |
| DMG | Dungeon Master Guide 2014 |
| XDMG | Dungeon Master Guide 2024 |

Names are presentation only. Preserve raw IDs in URLs, matching, deduplication and
selected-candidate identity. Unknown/custom IDs remain raw without guessed book or
year metadata. D&D Beyond notification wording remains unchanged.

### Validation and remaining acceptance

Stage-1 preparation: twelve local offline checks using real provider helper,
AST-extracted config/candidate functions, mocked HTTP and JSON/YAML temporary files.
Index metadata contained all six IDs, not proof of usable live stats/token images.
See [handover](../handover/230-fivetools-sources.md) for provenance and limitations.

Stage 2A: seven local source/reader/runner methods and three Node fixture subtests
passed. Updated first-fragment/bundle fingerprints reflect the intentional UI change;
other seven fragments remain identical. Size, syntax, UTF-8, assembly and isolation
checks remain. Full CI, real browser and live-provider validation are pending.

- [x] User confirmed XPHB as the intended identifier.
- [x] Agree separate notification and popup commits for the remaining stage.
- [ ] Deliver notification-label increment after exact bound approval and review CI.
- [ ] Deliver popup labels/browser regressions with raw identity and source links intact.
- [ ] Verify actual live data/stats/images for configured sources, not just index entries.
- [ ] Review complete regression CI and authorized live/browser behavior before closure.

README configuration/UI guidance is refreshed; no backend/provider/API behavior,
schema, credentials or bundled third-party data changes are included in stage 2A.
