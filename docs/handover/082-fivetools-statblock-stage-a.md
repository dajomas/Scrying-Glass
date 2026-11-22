# 082 - SG-TODO-022 Stage A: complete 5e.tools adapter (022.04)

[Back to handover index](../../HANDOVER.md) · [TODO 224](../history/224-fivetools-statblock-resolution.md) · [TODO 220](../history/220-admin-statblock-viewer.md)

Date: 2026-11-17. Baseline: `1e78d7531c95c80ab571f464e640bd1d121cee41` on
`features/perplexity-statblock`; prepared on `features/claude-statblock` (local
branch) by Claude and delivered as a zip archive (the user applies and commits;
no GitHub push). Commit SHA: not yet known. CI: not run (`[skip ci]`, agreed for
all Stage A-E deliveries except the last code delivery).

## Staged plan agreed 2026-11-17

The user agreed to deliver the rest of SG-TODO-022 in five larger stages, each
reviewed with CI/e2e results before the next: A = all of 022.04; B = 022.05-07;
C = 022.08-09; D = 022.10-12; E = 022.13-14; then 022.15/16. Recorded in
`CLAUDE_INSTRUCTIONS.md`.

## Delivered

All remaining 022.04 subunits are implemented:

- 04a contract: pinned runtime `5etools-src` `32ef600fab87a585a61dd1a22e9b02dfc58c728a`,
  `js/utils.js` blob `80c10d0439a5179b7d7f6e1220b9efb535a626d2`. Every copy mode of
  the runtime (`MODES` in the resolver) now executes. Typed diagnostics are unchanged.
- 04c.3c/d: `replaceArr`, `replaceOrAppendArr` (name/regex/index selectors, global
  `lastIndex` semantics), `removeArr` (names/force/items), `renameArr`.
- 04c.4: `scalarAddProp`, `scalarMultProp`, `calculateProp` with a restricted
  evaluator (`scrying_glass_fivetools_expressions.py`), never `eval`.
- 04c.5: `replaceTxt`, `replaceName`, `scalarAddHit`, `scalarAddDc` with a
  deliberate JavaScript RegExp port (`scrying_glass_fivetools_jsregex.py`) and
  the runtime's tag-skipping text walker.
- 04d: `addSenses`, `addSaves`, `addAllSaves`, `addSkills`, `addAllSkills`,
  `addSpells`, `replaceSpells`, `removeSpells`, `maxSize`, `scalarMultXp`;
  templates; dynamic `<$mode__detail$>` substitutions resolved before any _mod
  runs, as upstream does.
- 04e: allowlisted dataset fetching (`scrying_glass_fivetools_fetch.py`), exact
  case-insensitive dataset index and breadth-first reference collection
  (`..._collector.py`), tag port (`..._tags.py`), entry-to-node conversion
  (`..._nodes.py`), monster/definition facts (`..._statblock.py`,
  `..._definitions.py`), species placeholders and validated version-one
  snapshots (`..._preparation.py`).
- 04f: isolated preparation worker (`..._preparation_worker.py`): the whole
  preparation runs in a prlimit-bounded child; the parent fetches only allowlisted
  paths on its request. Oracle tooling in `tools/fivetools_oracle/`.
- `OrderedResolver.ADAPTER_VERSION` is `04f-1`; snapshot adapter version
  `5etools-04f-1`.

## Decisions and behavior changes

- Entity matching follows the runtime's URL hash: name and source compare
  case-insensitively; record `edition`/`discriminator` metadata only constrain a
  match when the request specifies them. Needed for e.g. `Kuo-Toa` vs `Kuo-toa`
  and edition-tagged base items.
- Dynamic substitutions no longer fail with `dynamic_substitution_pending_04d`;
  unknown modes stay verbatim. Missing scores or other NaN/undefined outcomes,
  which upstream prints as text or JSON `null`, fail explicitly
  (`nonfinite_numeric_result`, `unsupported_substitution_value`).
- The foundation `Resolver` keeps `modification_execution_pending_04c` for
  compatibility; unknown modes in the ordered executor report
  `unknown_modification_mode`.
- Regex subset: non-unicode flags `g i m s`; no backreferences, lookarounds,
  nested unbounded quantifiers, non-ASCII case folding or astral-subject splits;
  each refusal is `unsupported_regex`. Hard CPU bounds remain the worker's.
- Facts for the selected creature never include name, AC, HP or initiative
  bonus; related creatures keep their own values. Section labels (trait names)
  keep source text; species placeholders apply to text nodes, protecting names of
  collected related creatures (e.g. `Vampire Spawn`).
- Legendary action counts are shown only when present in the data; no
  boilerplate intro is generated. Images in entries are omitted with a
  `media_omitted` warning.
- New engineering limit `dataset_files` (64 dataset files per preparation) is
  a proposed safeguard, not one of the agreed sixteen limits; agreed by the user
  2026-11-20 as a fixed safeguard (TODO 220). Reaching it yields an explicit partial warning.

## Validation (executed in this environment, Python 3.13.18, Node 22.23.4)

- Upstream oracle, all real inheritance data: 1,161 of 1,161 entities
  (1,142 monsters, 3 templates, 16 legendary groups) resolve identically to the
  pinned runtime, including root key order.
- Synthetic oracle, 351 cases across every mode/option: 271 identical, 66 fail in
  both, 14 where upstream emits NaN/undefined and the port fails explicitly; no
  mismatches.
- Regex port: 2,573 pattern/subject/replacement cases identical to Node. Restricted
  evaluator: 3,023 expressions, no value mismatches (128 legacy-octal/comment
  forms refused). Tag stripping: 19,197 real tagged strings identical.
- Preparation of all 4,683 real monsters from a local checkout of the pinned data:
  no errors; 4,627 `available`, 56 `partial`. Maxima: snapshot 612,484 B, 2,779
  nodes, depth 9, 1,255 B text value, 135 definitions, 190,066 B reference
  bytes, 2.2 s (p95 0.78 s). All within the agreed limits.
- Unit tests: new `test_fivetools_jsregex` (12), `_general_modes` (9),
  `_creature_modes` (7), `_preparation` (7), `_fetch` (4), `_preparation_worker`
  (5); updated existing resolver tests for the completed-mode contract. All
  fivetools/statblock modules give the same results as the baseline; modules that
  need FastAPI/aiohttp/httpx cannot import here (same failures at the baseline).
- Not run: the full suite (several tests need network/FastAPI), Python 3.14,
  CI, browser/e2e, live 5e.tools fetches (the container cannot reach 5e.tools;
  the pinned GitHub data was used instead).

## Known limitations and open work

- Generated magic-item variants (e.g. `+1 shortsword`, barding, `Flame Tongue`)
  from `magicvariants.json` and the runtime's item enhancement are not
  implemented; such references are `reference_unavailable` (partial). This is the
  cause of 55 of the 56 partial monsters and is open work 04e.2 in TODO 224.
- Apply/API binding, job scheduling, provider switches and shared caching across
  preparations belong to 022.08; `CachingFetcher`/`HttpsFetcher` are building blocks.
- `_versions` of a creature are not separate candidates yet (022.08 selection).
