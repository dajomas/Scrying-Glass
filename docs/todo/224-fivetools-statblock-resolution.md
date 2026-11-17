# 224 - SG-TODO-022.04: ordered 5e.tools inheritance and reference resolution

[Back to TODO index](../../TODO.md) · [Controlling parent](220-admin-statblock-viewer.md) · [Handover](../handover/080-monster-lookup-diagnostics.md#02204ab-core-graph-preparation---2026-11-17)

## Current status - 2026-11-17

Partial 04a/b core implementation; neither subunit nor 022.04 is complete or
accepted. All accepted 022.01-022.03/lifecycle and 016/017 scopes stay closed.
The complete original a-f requirements and history remain required and are
[retained here](https://github.com/dajomas/Scrying-Glass/blob/dcd55b68210948e1f142ba6c377cdab25e7f384e/docs/todo/224-fivetools-statblock-resolution.md).
The parent's consolidated contract/limits overrides dated pending-status notes.
This consolidation cancels no unfinished requirement. SG-TODO-023 is separate.

## Implementation and evidence

`python/scrying_glass_fivetools_resolution.py`: typed exact identity, immutable
record index, loader/result/provenance/diagnostic contracts, recursive base and
template copy chains, root overrides, preservation/null rules, template root
precedence/property order, separate active-path/caching, logical cached depth
and operation accounting, deadline/cancellation, compact intermediate preflight,
response-record cap and record-byte/entry LRU with TTL. One immutable configured
dataset generation per resolver. No network, DB, public API or JavaScript.

All 28 runtime modes plus string removal are recognized and ordered; executing
nonempty modifications explicitly fails at 04c. This is not full inheritance
compatibility. Source snapshots/caches/siblings are isolated by immutable bytes.

The reconstructed payload ran 22 native Python graph tests on Python 3.12.8:
OK, no skips/errors/failures. Synthetic exact-source fixtures execute the actual
module, not provider integration. Prior preparation ran seven controlled upstream
getCopy comparisons on Node 20.20.1 matching content and top-level property order.
Those comparisons used the verified unmodified runtime and a captured Parser
slice and were NOT rerun on this reconstructed payload. No full repository suite,
new live-provider check, current-payload oracle run or covering CI is claimed.

## Pins and semantics

Runtime: 5etools-mirror-3/5etools-src at 32ef600fab87a585a61dd1a22e9b02dfc58c728a.
Recovered js/utils.js Git blob 80c10d0439a5179b7d7f6e1220b9efb535a626d2;
329654 bytes; SHA-256 67c28c64fa7cc98139923d7cfdbe4faa6807b6583a54451962a988567de1a172.
Schema comparison: TheGiddyLimit/5etools-utils v0.17.34 commit
64e8ab38231972d8cc1572520978ccea92f17ecb; util-copy template blob
5842394edd2c1b47cebc6af27b06659964af2285; bestiary/template blob
818c978880a75b02b4a8eebf768dd7554e5e056a. Creature schema blob
53bd51112c644f5ccda15777fa41cab636fd41e9 was only partially retrieved.
The package range ^0.17.34 is not a verified lockfile pin. Copy-spec comparison:
TheGiddyLimit/homebrew/_doc/Spec_Copy.md blob 36d759280455b45768210e3c7d644d5c02bc010e.

Runtime adds replaceName; wildcard entry properties include bonus/mythic/headers.
Property groups retain ordinary order, then _, then *. Templates append mods;
template roots cannot overwrite original selected keys. Null removals occur only
while traversing base keys. Dynamic substitution precedes mods; calculateProp
also substitutes its own prof_bonus/dex_mod variables at execution. addSpells
supports a named entry; replace/remove use the first entry. Runtime constant/will/
ritual spell removals omit assignment; a documented compatibility warning is due.
Captured tag defaults: creature/legroup MM; disease/item/variantrule DMG; action/
condition/status/skill/spell/sense PHB. These never default missing copy sources.

## Remaining gates

04a: full operation/option/default matrix, complete relevant schema comparison,
restricted formula/regex/substitution contract and fixture/oracle provenance.
04b: provenance-inclusive cache accounting and complete resource-boundary tests.
Current cache_bytes bounds record bytes only. In-process parsing/compilation does
not enforce a hard worker memory/CPU ceiling. No production preparation endpoint
is enabled; later integration must supply terminable supported-platform memory
isolation and one accepted deadline including queue/network work.
04c/d: general and creature operations, substitutions/versions and compatibility.
04e: semantic exact-reference BFS, normalized model conversion and private provider
integration, including fetch/provider safety outside the DB lock.
04f: adversarial/resource, actual normalized output, persistence and existing
provider regression gates. The parent's complete limits and six-field SG authority
remain controlling. Existing stats/images/tracker/model/lifecycle behavior is unchanged.

Intermediate pushes use [skip ci] until the final 022.04 code push, by explicit
user instruction. No workflow edits or dispatch. Delivery, passing CI and formal
acceptance are distinct. No merge, deployment, release or overall 022 closure.
