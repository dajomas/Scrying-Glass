# 060 - 5e.tools sources and descriptive names

[Back to TODO index](../../TODO.md)

## SG-TODO-006 - Expand configurable 5e.tools defaults and display book names

- Status: proposed/requested; implementation and validation not started.
- Requested: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Dependency: resolve XPBH/XPHB identifier discrepancy before implementing defaults.

### Requested behavior

Expand the MM/XMM source set to six sources, allow configuration in the config
file, and use all six defaults when the list is omitted. Preserve explicit user
configuration rather than appending default sources unconditionally.

The user's literal requested identifiers are:

    MM, XMM, PHB, XPBH, DMG, XDMG

The same request defines an X prefix as the 2024 version of the corresponding
2014 source. That rule would produce XPHB from PHB, not XPBH. Preserve the literal
request here; verify the intended/provider identifier before changing code. Do not
silently drop the 2024 player-handbook source or implement an unverified alias.

### On-screen labels requested

| Requested identifier | Descriptive label |
|---|---|
| MM | Monster Manuals 2014 |
| XMM | Monster Manuals 2024 |
| PHB | Player Handbook 2014 |
| XPBH (XPHB discrepancy unresolved) | Player Handbook 2024 |
| DMG | Dungeon Master Guide 2014 |
| XDMG | Dungeon Master Guide 2024 |

These labels preserve the user's wording. Keep provider identifiers distinct from
labels in requests, deduplication, source URLs and selected-candidate identity.
Use descriptive names in candidate choices and lookup outcomes; do not replace
provider source codes with display strings internally. Define a sensible fallback
for custom/unmapped configured sources without inventing book metadata.

### Existing implementation to extend

config.example.yaml already exposes display.fivetools_sources: ["MM", "XMM"].
Review configuration normalization plus both candidate and legacy stats/image
provider paths so an omitted setting has one consistent six-source default.
Update the existing key, configuration example and relevant documentation rather
than adding a competing setting. Config/data/source validation must distinguish
unavailable data or provider failure from a successful zero-match search.

### Acceptance and validation

- [ ] Resolve the intended 2024 player-handbook identifier and record the decision.
- [ ] Omitted list uses the agreed six-source default consistently across lookup paths.
- [ ] Explicit lists override defaults; ordering and existing source matching remain predictable.
- [ ] Configuration validation covers malformed lists and explicitly empty lists according to a documented policy.
- [ ] Candidate popup and result notifications show the requested year-specific descriptive names.
- [ ] Unknown custom source labels remain usable without incorrect edition claims.
- [ ] Confirm each configured source is present/usable in the provider's supported data index; report missing data accurately.
- [ ] Offline/config/UI regressions verify omitted/explicit settings, all six labels, provider order and selected identity.

No configuration defaults, lookup implementation or live-provider assumptions are
changed by this documentation-only task entry. Account integration SG-TODO-004
is on hold and is not a dependency for this public-provider source-list work.
