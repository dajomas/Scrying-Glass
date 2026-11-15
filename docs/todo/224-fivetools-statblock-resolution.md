# 224 - SG-TODO-022.04: ordered 5e.tools inheritance and reference resolution

[Back to TODO index](../../TODO.md) · [Parent SG-TODO-022 plan](220-admin-statblock-viewer.md#02204---add-the-5etools-statblock-adapter)

## Status and scope - 2026-11-15

Implementation-plan addition requested by the user at 09:32 CET, following the ordered-interpreter proposal. Status: planned, not implemented. Parent 022.01 remains in progress; 022.02-022.16 remain pending. All development stays on `features/perplexity-statblock` in `dajomas/Scrying-Glass`. No merge, deployment, release or future write is authorized by this record.

This addendum expands 022.04 before the full 5e.tools adapter is completed. It supersedes any reading of the parent's unresolved-copy safeguard as permission to omit inheritance support routinely. Explicit partial/error handling is a failure safeguard, not a substitute for implementing the required resolver. Existing stats/image lookup behavior and the accepted SG-TODO-016/017 scope are not changed by this plan.

## Architecture and processing boundary

Separate three responsibilities:

1. Exact-source loader: locate selected creatures, base creatures and templates by exact identities through the configured source indexes/datasets. Dependency loading is not a new candidate search and must never substitute a same-name creature from another edition.
2. Deterministic Python inheritance interpreter: operate on supplied data, without network calls or database writes. Resolve chains and apply root overrides, preservation/removal directives, templates, placeholders and ordered `_mod` operations according to a pinned, inspected upstream runtime implementation.
3. Reference collector: inspect the resolved creature and collect required available supporting definitions, with source identities, deduplication, cycle protection and bounded work. Feed the result into the shared versioned statblock model.

Resolve source inheritance and source numerical calculations before Scrying Glass species-placeholder normalization and display-field precedence. Keep source intermediate values available where calculations require them; they never overwrite the six live authoritative Scrying Glass fields: monster name, species, AC, current HP, max HP and initiative bonus. Selected-variant provenance remains distinct from base/template/reference dependencies. Imported snapshots remain independent per monster, even when network/cache results are shared.

## Bounded subunits inside 022.04

Execute in order; split further before preparing a large change if the inspected runtime reveals a larger compatibility surface. Each implementation delivery includes focused tests, necessary documentation and reviewed evidence or explicitly pending validation. Each external write needs its own bound approval.

### 022.04a - Pin semantics and freeze the resolver interface

Depends on 022.01; implementation foundation also depends on 022.02. Inspect the actual upstream runtime resolver, templates and schemas, recording repository/ref plus commit/blob identities. Compare runtime behavior with the copy-format specification; documentation alone is not proof of compatibility. Freeze the supported operation/option matrix, defaults, inheritance order, override/null/removal/preservation rules, template handling, substitutions, regex and formula semantics. Define typed input/output/errors and dependency provenance. Finalize separate numeric inheritance-depth, operation-count, dependency-count, expanded-size and execution-work budgets under item 6; do not confuse these with display-tree depth.

Exit gate: a bounded compatibility contract and representative fixture/oracle plan, with unsupported behavior explicit. Do not invent a pinned revision before inspecting it.

### 022.04b - Exact-source inheritance graph and isolation

Implement independent deep copies, exact base/template lookup, recursive chain resolution, root overrides and the verified preservation/removal rules. Use a recursion stack to detect cycles separately from a cache of already resolved entities. Reject missing or ambiguous bases, invalid identity data, cycles and exceeded limits with structured diagnostics. Do not mutate input records, shared caches, sibling variants or already saved snapshots.

Tests: plain records, multiple inheritance levels, cross-bestiary dependencies, repeated dependencies without false cycle reports, real cycles, missing/duplicate bases, null/removal semantics, cache independence and every resource boundary. Gate: correct graph resolution and isolation without pretending all `_mod` modes are implemented.

### 022.04c - Ordered general modification operations

Implement verified selectors, string removal shorthand and ordered operation lists; preserve property and operation processing order as required by the upstream implementation. Cover documented general families: `replaceTxt`, `appendStr`, `prependArr`, `appendArr`, `appendIfNotExistsArr`, `insertArr`, `replaceArr`, `replaceOrAppendArr`, `removeArr`, `renameArr`, `setProp`, `calculateProp`, `scalarAddProp`, `scalarMultProp` and `prefixSuffixStringProp`. Validate actual availability and options against the pinned runtime rather than treating this documented list as exhaustive.

Use a restricted expression evaluator, never Python `eval`, imported JavaScript execution or arbitrary executable expressions. Port supported regex semantics deliberately; bound work and report unsupported syntax rather than silently approximating JavaScript regex behavior. Tests cover each mode/option, no-match behavior, duplicate handling, numeric-string/sign/rounding behavior, malformed payloads and order-sensitive compositions whose result changes when operations are reversed.

Gate: fixture-backed general modification compatibility, with diagnostics identifying selected entity, dependency chain, property, operation index and mode.

### 022.04d - Creature-specific operations and templates

Implement the inspected creature-specific behavior, including `addSenses`, `addSaves`, `addAllSaves`, `addSkills`, `addAllSkills`, `addSpells`, `replaceSpells`, `removeSpells`, `scalarAddHit`, `scalarAddDc`, `maxSize` and `scalarMultXp`, plus required template/dynamic-substitution handling established in 04a. Verify spellcasting-target rules against runtime; do not assume documentation's first-entry behavior is universally sufficient.

Tests: retained greater bonuses/ranges, proficiency/expertise, multiple spellcasting entries, spell usage groups, attack/DC tag changes, intermediate-value calculations, template interactions and numeric boundaries. Unknown modes fail explicitly; never return an unchanged base as a successful variant. Gate: required real variants resolve with their intended identity and content.

### 022.04e - Supporting reference collection and normalized adapter

After inheritance, collect required available content from the configured 5e.tools data root: bestiary index/files and `bestiary/legendarygroups.json`; condition/disease/status, item/base-item, skill, spell, variant-rule and action datasets as required. Relevant locations confirmed during design include `/data/spells/index.json`, source-book spell files such as `/data/spells/spells-xphb.json`, `/data/variantrules.json` and `/data/actions.json`. The user's `spells_` filename prefix denotes the spells subdirectory, not a remote filename. Other dataset paths/default source rules must be verified, not guessed.

Use exact entity kind/name/source identities and documented default-source semantics. Follow required nested dependencies with deduplication and cycle detection. Do not automatically follow every metadata/reprint link or recursively inline other creatures into prose. Collect and expose required related-creature/reference snapshots in a bounded structure. Fetch/cache complete datasets where necessary, but save only the relevant resolved definitions with each statblock snapshot. A provider failure, missing/ambiguous reference, unsupported construct or resource limit must be explicit, never silent truncation or edition substitution. Respect provider switches and trusted configured destinations; network work remains outside the database lock.

Preserve selected-creature modifications to spellcasting/actions; generic referenced definitions supplement, not replace, those modifications. Integral sections such as regional effects belong in the main statblock. Supporting definitions are proposed as expandable reference details inside it. Keep reference-entity identities/prose separate from the owning monster's species normalization, so `Vampire Spawn` is not accidentally changed to `[MON] Spawn`. Final UI detail remains to be reconciled in 022.01; this plan does not imply additional expanded monster tiles.

Tests: MM/XMM Vampire legendary groups, book-specific conditions, Holy Water, skills, XPHB Charm Person/Command, action/rule dependencies, missing editions, repeated/nested/cyclic references, disabled providers and stale fetches. Preserve ordered full content, attribution and the existing stats/image projection. Gate: shared-model output includes required available reference content with explicit capability/warning information.

### 022.04f - Compatibility and integration evidence

Run focused interpreter/collector tests and relevant existing-provider regressions. Compare representative outputs against the pinned upstream resolver where reference execution is available. Keep synthetic fixtures, upstream-oracle comparisons, captured-source analysis and live-provider checks distinct. Record expected/actual results, covered revisions, remaining unsupported constructs and performance/resource checks. Include adversarial regex/formula, expansion-growth, cycle and cache-isolation tests.

Measure actual normalized byte size, text size, node count and depth, including saved references/provenance/warnings. Source JSON bytes/depth are not normalized measurements. Complete 022.04 only when inheritance, reference collection, conversion and required validation gates are satisfied; foundations alone are not complete provider support.

## Continuity: where 022.01 stood at this addition

Seven-item review: items 1-5 agreed in conversation (field precedence/species normalization; model/storage approach; exact-source keys; capability matrix; atomic apply/Edit/conflict semantics). Item 6 resource/retrieval limits remains under review, expanded by reference collection and inheritance budgets. Item 7 consolidated design/evidence/status record is pending. Agreement on high-level approaches is not a claim that every concrete schema/API field or implementation detail is already frozen or persisted. Do not ask the user to reapprove settled items.

The user requires `[MON]` and `[MONS]` to resolve to the current Scrying Glass species verbatim, never the individual name or Tetra-cube regular/short/plural fields. Complete case-insensitive source-creature-label occurrences in selected creature descriptive text become species placeholders on import; do not infer aliases/plurals or alter provenance/URLs/licences. Reference content needs identity-aware treatment as noted above.

The Tetra-cube helper-read blocker was resolved through the complete addition patch for `external_sourcefiles/statblock-script.js`, commit `828a39e56d171d6361aa4812550f316a524daba7`, present in user-supplied merge `5faece210f1bd5b4ce2c9a8557999faea6fff516`; blob `a8520dcbf739ffb4f24ec7a50607bce29886d950`. Earlier truncated-read notes in the parent are historical and superseded on this point.

User-run Vampire captures and uploaded reference datasets were analyzed in conversation; they are not committed evidence by this addition. Eight extracted candidates and 15 captured response hashes were checked. Supporting references increased measured source bundles; normalized limits, complete recursive closure, production interpreter behavior and operational limits remain unvalidated. No complete-support or universal-size claim follows from a Vampire sample. Supporting definitions must be collected when required and available, not merely linked to the provider website.

## Validation and documentation boundaries

This is documentation only, with `[skip ci]`. No interpreter, adapter, migration, network collector, UI or tests are implemented by this commit. No application tests, new live fetch, CI run or upstream-oracle execution was performed for this plan addition. The operation families are based on the reviewed [copy-format specification](https://github.com/TheGiddyLimit/homebrew/blob/master/_doc/Spec_Copy.md); runtime verification remains 04a work.

Live project instructions, README, HANDOVER index, TODO index, parent 022 plan and provider handover 590 were reviewed. README and the accepted 016/017 handover remain unchanged because delivered behavior has not changed. A dedicated indexed 022 handover is still due at the first implementation delivery under the parent plan. The parent task is preserved; this linked addendum is authoritative for the 022.04 expansion and the dated continuation notes above, not a close-out of 022.01.
