# 083 - SG-TODO-022 Stage B: Open5e, D&D Beyond and .monster adapters (022.05-022.07)

[Back to handover index](../../HANDOVER.md) · [Stage A](082-fivetools-statblock-stage-a.md) · [TODO 220](../todo/220-admin-statblock-viewer.md)

Date: 2026-11-17. Baseline: `2f2bc4a01612b3f6b8245fcfd4049dc3c935a9b6` on
`features/claude-statblock`. Delivered as a zip archive; commit SHA not yet
known. CI not run (`[skip ci]`, agreed for Stage A-E until the last code delivery).

## User decisions - 2026-11-17

1. Open5e records from every document (including Advanced 5th Edition) are offered
   like the others, labelled with their document and game system.
2. The Open5e adapter may fetch `/documents/<key>/` (cached) for licence and
   publisher attribution.
3. The user supplied seven Tetra-cube files, now in `monsters_examples/tetra-cube/`.

## Delivered

- `scrying_glass_statblock_sources.py`: shared safe Markdown subset (bold, italic,
  bullet lists, pipe tables, paragraphs; HTML removed with `html_removed`),
  `ProviderFetcher` (HTTPS, host allowlist, at most three same-set redirects, size
  enforced while reading, no cookies), species placeholders and validated
  version-one snapshot assembly. `name_key` treats ' and ' (curly) alike.
- 022.05 `scrying_glass_open5e_statblock.py`: `prepare_open5e(key)` and
  `discover_open5e(species)`. Identity: endpoint + v2 creature key; document and
  game system in provenance. Traits and actions in statblock order; actions grouped
  by type; recharge, per-day, legendary cost and form limits added to names; saves
  and skills only as supplied (not the computed `*_all` lists); illustration omitted
  with a warning.
- 022.06 `scrying_glass_dndbeyond_statblock.py`: `prepare_dndbeyond(path)` and
  `discover_dndbeyond(species)`. Identity: numeric monster id; 2014 and 2024 markup;
  attributes, ability blocks/table, tidbits, description blocks, the content below
  the statblock (lair information) and habitat/treasure/source footer. Pages without
  a statblock root are `statblock_unavailable`. Links stay D&D Beyond links.
- 022.07 `scrying_glass_tetracube_statblock.py`: `prepare_monster_file(bytes)`.
  Identity: SHA-256 of the file bytes. Ports ReplaceTags (`[STR ATK]`, `[CHA SAVE]`,
  `[2d6 + 3]`), the `_`/`**` toggles and the property lines. `[MON]`/`[MONS]`
  become species placeholders; hpText, armour, short and plural names are not used.
  Unknown placeholders stay readable with `unresolved_placeholder`.
- `NodeBuilder` gained a pluggable inline parser and an `inlineItems` entry type
  (5e.tools behaviour unchanged).

## Decisions

- The six Scrying Glass fields are never facts (AC/HP/initiative attributes are
  dropped by label on D&D Beyond; Open5e `armor_class`, `hit_points`, `hit_dice`,
  `initiative_bonus` are skipped; Tetra-cube armour/HP fields ignored).
- Tetra-cube `[2d6+3]` without spaces: upstream drops the +3; Stage B keeps it
  ("10 (2d6 + 3)"), per the agreement not to reproduce lossy Tetra-cube parsing.
- Disabled Tetra-cube sections that still hold entries are shown with
  "(disabled)" and `enabled=false`; their generated boilerplate descriptions are
  only shown for enabled sections.
- Open5e and D&D Beyond do not supply lair/regional text (Open5e) or public
  supporting definitions (D&D Beyond); nothing is substituted.

## Validation (Python 3.13.18, this environment)

- Captured evidence (`monsters_examples`, commit 2f2bc4a): all 67 Open5e records,
  35 public D&D Beyond statblocks and 7 `.monster` files convert to valid
  snapshots; the 7 gated D&D Beyond pages report `statblock_unavailable`.
  Largest snapshots: Open5e 25,242 B, D&D Beyond 37,024 B, `.monster` 19,213 B.
- `tests/test_statblock_source_adapters.py`: 14 tests (synthetic fixtures for each
  adapter, fetcher bounds, discovery, plus the captured-evidence tests above, which
  skip when `monsters_examples` is absent). Stage A preparation tests rerun OK.
- Not run: live requests (blocked here), Python 3.14, CI, e2e.

## Open work (Stage C, 022.08)

- Wiring into discovery/preparation APIs, provider switches, job scheduling,
  shared caching and running these adapters in the isolated worker.
- Open5e document licence fields were not captured; the parser accepts
  `licenses[0].name/url` and otherwise warns `license_unavailable`. Verify against a
  live `/documents/` response.
