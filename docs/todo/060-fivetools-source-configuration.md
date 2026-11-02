# 060 - 5e.tools sources and descriptive names

[Back to TODO index](../../TODO.md)

## SG-TODO-006 - Expand configurable 5e.tools defaults and display book names

- Status: in progress; stage 1 prepared, CI/live validation pending; stage 2 UI names not implemented.
- Requested: 2026-11-02. Two-commit delivery approved: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Preparation base: a8461e93ac6281f618aa3b436a68e2787578e909 on features/perplexity.
- Identifier decision: user corrected XPBH to XPHB on 2026-11-02.

### Approved staged delivery

1. Source configuration/providers, tests and documentation: six defaults, explicit ordered overrides and empty-list handling. Raw source codes remain visible in this stage.
2. Descriptive UI book/year names, preserving raw identifiers internally, with UI tests and documentation.

Stage 1 is a usable expanded-search increment, not completion of the full task.
Do not close before stage 2 and required validation. SG-TODO-004 remains on hold
and is not a dependency for this public-provider work.

### Source configuration and compatibility

Omitting display.fivetools_sources uses, in order:

    MM, XMM, PHB, XPHB, DMG, XDMG

JSON/YAML explicit lists replace the defaults, never append to them. An explicit
empty list searches no 5e.tools sources and does not fetch its index/data, without
disabling independent D&D Beyond lookup. Duplicate identifiers are searched once
in first-occurrence order. Identifiers are case-sensitive, nonempty strings without
surrounding whitespace; maximum 32 input entries. Null, scalar, malformed lists and
invalid display mappings fail configuration loading rather than acting as omission.

Existing config files explicitly listing only MM/XMM remain two-source overrides.
Remove that key or expand it to opt into all six; restart after configuration edits.
The configuration example is updated. Shared provider validation/default handling
is used by candidate enumeration and legacy first-result stats/image lookup. The
normal merge still isolates defaults from mutations. No new configuration key,
schema, credentials, bundled third-party data or provider-order change is added.

### Descriptive labels (stage 2 remaining)

| Identifier | Requested label |
|---|---|
| MM | Monster Manuals 2014 |
| XMM | Monster Manuals 2024 |
| PHB | Player Handbook 2014 |
| XPHB | Player Handbook 2024 |
| DMG | Dungeon Master Guide 2014 |
| XDMG | Dungeon Master Guide 2024 |

Preserve raw IDs in URLs, matching, deduplication and selected-candidate identity.
Show names in popup choices and lookup notifications; unknown custom source codes
must remain usable without fabricated names/edition metadata. UI behavior is not
changed by stage 1.

### Acceptance and validation

- [x] User confirmed XPHB as the intended identifier.
- [ ] Review CI for omitted defaults, explicit/empty settings, ordering, deduplication and validation across configuration and provider paths.
- [ ] Verify all six sources can supply usable stats/images through supported live data; distinguish index entries from successful live retrieval.
- [ ] Deliver and validate descriptive names in popup choices and result notifications, including unknown/custom IDs.
- [ ] Review complete regression CI and authorized live/browser behavior before completion.

Twelve new offline tests passed locally. They use the real 5e.tools helper module
and AST-extracted actual config/candidate functions, with JSON/YAML temporary files
and mocked data HTTP. They do not initialize the complete FastAPI server. Sources
compile; full application/CI tests and live data/image access remain pending.
Existing provider/diagnostics/UI tests remain unchanged and must run normally.

All six IDs were present in data/bestiary/index.json of 5etools-mirror-3/5etools-src
at 8790755429c346d20020eed7826d312d484c393f (blob 6c1dc9533c847cd5e4d081b68b7ad705db0278ef).
This verifies index metadata only. The direct live 5e.tools fetch failed in the
assistant environment; runtime reachability, returned stats and images are not
claimed verified. Existing missing-source/HTTP error policies are otherwise unchanged.

See [stage handover](../handover/230-fivetools-sources.md). README's explicit
MM/XMM snippet remains a valid restrictive override, not the new omitted-list
default; the fuller README/UI documentation refresh is planned with stage 2.
