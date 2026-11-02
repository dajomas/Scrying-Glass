# 180 - Attack statistics archive implementation

[Back to handover index](../../HANDOVER.md)

Recorded: 2026-11-02. Task: [SG-TODO-002](../todo/020-monster-damage-effects.md).

## Baseline and revised request

This archive starts from the original user attachment
`scrying-glass-source-e0c321a-base64.txt`, not the earlier assistant patch. No live
GitHub commit/branch identity was checked; no commit was made, branch modified or
workflow dispatched. The current archive request supersedes historical
GitHub-first delivery language in the restart prompt/handover.

The implemented user interface now puts Add statistics reduction in the bottom
Battle actions bar. Each row contains target, statistic and amount; seven stats
are supported. Reductions resolve in attack row order in the same serialized
transaction, not through a new Encounter tools panel. Applied rows are locked and
skipped on subsequent applies. Closing discards pending rows. Reaction mechanics
retain their existing damage/healing-only scope.

Restore statistics is next to character Reset and also available beside monster
Reset. It restores one chosen stat or all, keeping original/base values and
removing the relevant reductions without healing current HP or resurrection. The
dialog also enters unknown original ability scores; these are not guessed. It
shows originals, effective values and reduction totals. Polling preserves open
base drafts, scope changes discard them, and stale operations are rejected.

See [workflow](../User-Guide.md#attack-statistics-reductions) and
[technical model/API/migration](../Technical-Documentation.md#attack-statistics-schema-8).

## Integration and decisions

The baseline lacks six original ability scores, so the dialog requires known
values before an ability reduction can apply. Effective values floor at zero but
full reduction amounts persist. All ability modifiers/derived AC/initiative,
monster presets, save outcomes and special death rules stay GM-resolved. Ordinary
Reset retains reductions and bases; monster Original HP remains a separate reset
HP template. Restore is not damage healing.

Mechanical effects have manual recovery and private generated names. They use
normalized schema-8 effect columns, while base/effective fields use existing typed
scalar entity attributes. Existing setup/roster/runtime persistence, source
cleanup, snapshots, undo and campaign bundles are reused. Public serialization
remains allowlisted. Token checks bind reductions/restoration to campaign, revision
and encounter state. Audit, persistence and deferred broadcast share the existing
transaction wrapper. No new player route or CI change is introduced.

The schema version constant matches 8. Existing v5/v6 migration fixtures now remove
v8 columns before setting their simulated old version; simply lowering a pragma
would not make a valid old schema. The monster-edit AST fixture supplies package
context for newly required relative imports.

## Validation executed

- `python -m pytest tests/test_attack_statistics.py -q --color=no`: 21 passed.
- `python -m unittest discover -s tests -p 'test_*.py' -v`: 910 run, OK,
  2 skipped. This includes the 21 new tests (not a separate count to add).
- Configured pytest-only death-save and slug-truncation modules: 43 passed.
- `node --test` individually on all 36 top-level JavaScript/CJS test scripts:
  every script exited 0. Two new scripts exercise attack-row integration and
  restoration UI with mocked DOM/fetch.
- Python compileall across application/tests: exit 0.
- Attempted server import: failed at missing uvicorn; FastAPI is also unavailable.

New Python tests use real temporary SQLite, fixture services and the actual
serialized transaction wrapper. They cover all seven stats, ordered compound
resolution, stacking/zero/clamping, unknown bases, selected/all restoration,
nonhealing/nonrevival, stale checks, storage rollback/no broadcast, reset/source
cleanup, restart/undo/checkpoints, bundles/privacy, schema rejection and migration
backups. Existing tests may mock runtime dependencies. Two existing FastAPI
lifespan integration tests skipped because FastAPI is not installed. These results
are not evidence of actual application startup or authenticated HTTP/browser
integration. Standalone Python audits/browser scripts outside discovery were not
run. Logs are in the archive-only Patch/ directory.

## Remaining validation and operational cautions

Install runtime dependencies and validate startup/listeners, admin/origin/ownership
HTTP enforcement, real-browser attack-only reduction batches, mixed row ordering,
failed/stale applies, row replay protection, cancel/close, restoration and drafts
across scope changes. Confirm player privacy and HP-visibility behavior. Validate
migration/backup/rollback on a copy of deployment data and review CI if run.
Broader SG-TODO-002 and live validation are still open.

Do not overlay this on the earlier assistant patch without reviewing differences.
Deploy this replacement set against the original baseline. Stop/back up storage,
media/configuration first. Schema 8 is not safely downgraded by changing
user_version; restore matching old code/data from the backup instead. No file
renames/deletions/manual SQL are required.

README, deployment, user/technical documentation and indexed TODO/handover were
updated. Runtime requirements, CI and systemd service contract remain unchanged.
The historical root package-manifest.json is not this overlay's manifest;
Patch/FILE_MANIFEST.json records the baseline/replacement hashes. Patch/ is
supporting archive material and must not be staged as project source.
