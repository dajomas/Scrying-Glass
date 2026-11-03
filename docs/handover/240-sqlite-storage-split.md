# 240 - SQLite storage source split

[Back to handover index](../../HANDOVER.md)

Updated 2026-11-03. Task: [SG-TODO-008](../todo/080-source-size-refactors.md).
Activation preparation base: 0c8f1c9a95763bf8729d775f4596de68835cabf6, features/perplexity.

## Delivery history and scope

The agreed five stages are fields, schema/migration, records/encounters, operations,
and native facade activation. Stages 1-4 were deliberately unused preparations:

- 1: a9da32439b01529ab6deba8242b48593d95be594; fields and five local checks.
- 2: 2a651004a7870de461cce32f5dcffd56b91a2aa6; schema and seven local checks.
- 3: 8ed072c3cd3be53474a77cc9267bd7708f0d7638; records and eight local checks.
- 4: 0c8f1c9a95763bf8729d775f4596de68835cabf6; operations and eight local checks.

Each delivery was verified after pushing. No Storage CI result has been reviewed.
Earlier tests were limited original-base-schema fixtures; stage 4's effect rewrite
used mocked snapshot boundaries and did not validate effects persistence. Earlier
schema tests used empty v1/v2-to-v3 upgrades, not constructor/backups/full upgrades.

## Stage 5 activation draft

The 4,710-byte python/scrying_glass_storage.py facade imports the existing shared
fields and three native mixins. Five lifecycle methods remain on SQLiteStorage;
three schema, ten record and twenty operation methods dispatch through inheritance.
All 38 original method ASTs, signatures/decorators/SQL and seven field expressions
match the 39,486-byte original blob ea80b59cca80c6885f6ba1ba4d32b759beb187b5.
No schema/version/configuration change: SCHEMA_VERSION remains 8. Existing callers,
FeatureStorage underscore entry points, lazy migrations, transaction/savepoints,
backup ordering and compatibility exports remain. Shared STATE_FIELDS now aliases
the facade export, as the single runtime definition. Stage-module staging comments
are historical provenance; their methods are now activated by the facade.

Test-only storage_split_reference.py checks pinned original AST fingerprints and
builds an independent reference class for fixture comparisons. It is not production
source assembly. Old monolith-blob assertions are deliberately replaced, not waived:
complete method/field pins, native-dispatch and per-file <=20,000-byte guards remain.
The four preparation suites consolidate assertions into eleven methods. Ops rename
uses a limited snapshot-table fixture; effect rewrite still mocks load/save only.

Local results: eleven preparation methods, one native-dispatch/size test and one
constructor-failure/connection-close test passed (13 total). Proposed sources compile.
The new file-backed v8 persistence/effects/lair/reopen/rollback test was compiled but
not executed locally. Full v1/v2 populated migrations, backups, full service/server,
feature/snapshot suites and that new test remain CI validation, not claimed passes.
Existing unittest discovery includes all tests without workflow edits. GitHub search
is default-branch indexed, not an exhaustive working-branch source-reader audit;
existing inspected SQLite regression tests exercise runtime APIs and stay unchanged.

## Deployment and acceptance

Deploy the entire matching python/ tree, including all four storage support modules,
with the facade and package __init__.py; restart the single process. Do not deploy
the facade alone or mix pre-split and split files. Existing README deployment/backup
instructions already require the whole tree and remain applicable. Back up data as
usual. This source-only change adds no migration or special database conversion.

README, HANDOVER index, maintenance conventions and existing CI were reviewed/reused
unchanged; no path/index or command changes. No archive, manifest refresh, CI skip or
workflow dispatch. The five Storage source files are each below 20,000 bytes; other
oversized sources and Admin acceptance are separate SG-TODO-008 work. Keep task open
until exact activation CI evidence and deployment/user acceptance are reviewed.
