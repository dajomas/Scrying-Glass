# 010 - Architecture, runtime and security

[Back to technical documentation](../Technical-Documentation.md)

<!-- BEGIN preserved technical content -->
## Scoped compact inline editors

`static/compact-combatant-inputs.css` sets width, min-width and max-width to 7.5ch
(previously 15ch) for character `[data-chp]`, `[data-cmaxhp]`, `[data-ci]` inputs
and monster `[data-mi]` inputs within `#characters` / `#monsters`, retaining
`.hp-edit` / `.initiative-edit` class qualification. This overrides the generic
number-input minimum without altering setup-form or edit-modal fields.
The stylesheet is linked from `templates/admin/190_document_end.html`, after
feature styles. No JavaScript, validation, handlers, fonts or heights change.
The ch unit scales with the active font: 7.5ch is exactly half 15ch with the same
font. See `Patch/Compact-Inputs-Validation.md` for browser measurements and scope.

## Looking Glass companion styling

The preceding presentation-only restyling aligns Scrying Glass with Looking Glass
using shared dark surfaces, gold accents, local font fallbacks and coordinated
controls. It does not merge the applications or change encounter data, permissions,
combatant colours or configured player-display backgrounds. See
`Patch/Restyling-Changes.md`, `Patch/Restyling-Apply.md` and
`Patch/Restyling-Validation.md` from that package for its scope and checks.

## Python version and launcher policy

The launcher minimum is Python 3.10, not an exact minor-version selection. This
policy allows a compatible interpreter to be chosen; it does not establish full
application/dependency compatibility on every accepted Python version. Full
application execution on Python 3.10 remains unverified in this patch series.

- Linux: reuse a complete `~/dnd` environment after checking
  `sys.version_info >= (3, 10)`. For creation, probe `python3`, `python3.14`,
  `python3.13`, `python3.12`, `python3.11`, `python3.10`, then `python` in that order.
  Select the first command that exists and passes the minimum check.
- Windows: reuse `%USERPROFILE%\dnd` after the same minimum check. For creation,
  try `py -3`, then `python` on PATH. Validate the reported version rather than
  requiring an exact `-3.10` interpreter.
- Every launcher rejects an existing environment below 3.10 before pip, checks
  sqlite3 before package installation, and retains its existing config and entry
  point. Linux retains its dependency marker; Windows installs on each launch.
- A compatible existing environment is not silently replaced or downgraded.
  Back up files before manually recreating an unsupported environment. Changing
  the system Python installation does not upgrade an existing virtualenv.

The systemd unit does not use launcher discovery or its version checks. Its
`ExecStart` uses `/opt/scrying-glass/.venv/bin/python` directly; validate that
interpreter separately and recreate the service environment deliberately if
changing its Python version. Launch the root server script, not an external
`uvicorn module:app` command that would skip main-guard initialization.

Launcher regression checks:

```bash
bash -n run.sh
python3 -m unittest discover -s tests -p 'test_launcher*.py' -v
```

These tests use mocked Linux executable commands and simulated version reports.
Windows checks are static contracts, not PowerShell/cmd execution. Their passing
results do not prove full Python 3.10 server operation or dependency installation.
After installing dependencies in the chosen environment, check its version and
sqlite3, import the server, and validate real startup, persistence and encounter
workflows on copied data. Preserve this distinction in future compatibility claims.

## Runtime and composition

The root scrying_glass_server.py owns CONFIG, STATE, LOCK, SESSIONS, SOCKETS, STORAGE, paths and two FastAPI applications. Services bind methods to that live module before route construction and call each other through self.context. State replacement must update context.STATE. Services must not import the root server.

Root imports use python.* and web_html.*; siblings use relative imports. Retain __init__.py and avoid loading modules under two identities. web_html avoids standard-library html collision.

AdminAPI composes domain mixins plus feature/lair/account/ownership/viewer installers. Annotation resolution uses live-context names; request models/FastAPI types must exist before handler registration. Historical route counts are obsolete after extensions.

## Module map

| Module/group | Responsibility |
|---|---|
| scrying_glass_services | Service binding |
| service_auth | Database accounts, initialization, authorization |
| service_state | Normalize and project Admin/player state |
| service_campaigns | Campaign/setup lifecycle |
| service_migrations | One-time legacy JSON import |
| service_persistence | Runtime/roster/setup writes |
| service_activity | Action and HP logs |
| service_images | Media/remote lookup/monster construction |
| service_battle | Activation/order/rounds/turns |
| service_notifications | Persistence helpers and broadcasts |
| service_features | Recovery, effects and revision integration |
| scrying_glass_storage | Normalized SQLite and schema upgrades |
| database_transactions | Serialization, rollback, deferred broadcast |
| campaign_ownership and routes | Admin ownership/reassignment |
| campaign_viewers and routes | Viewer grants and campaign scoping |
| feature_rules, turn_rules, health_limits | Health and eligibility invariants |
| initiative_gate | Integer initiative requirement |
| feature_storage, api_features | Recovery/effect storage and APIs |
| service_lairs, lair_rules/storage, api_lairs | Lair model and actions |
| campaign_bundle | ZIP validation, media remapping/cleanup |
| request_security, logout, asset_cache | Origin checks, revocation, cache busting |

## Startup and paths

Direct-script startup loads config/overrides, resolves storage, checks static/, creates uploads/, opens SQLite, initializes users, transactionally imports legacy data and loads/normalizes/saves runtime. It mounts static/media and runs both Uvicorn listeners concurrently. Shutdown closes storage.

Composed router/application lifespans initialize additive campaign viewer/ownership storage. Preserve lifespan composition; server import checks do not execute it. External uvicorn imports skip main-guard storage initialization.

Relative storage resolves from working directory; templates/static resolve from source. An absent new default directory may fall back to the legacy monster-display-data directory. Explicit storage_dir remains authoritative.

Configuration merges defaults. CLI: --config, --bind, --admin-port, --client-port, --storage-dir. Accounts are not current YAML settings; security.users imports once only.

## SQLite model and migration

Canonical structured storage is storage_dir/scrying-glass.sqlite3; uploads remain files. Base schema reaches v8: normalized records, accounts, effects/recovery/revisions, lairs, setup lair flags and attack statistic reductions. Ownership/viewer tables initialize additively; PRAGMA user_version alone does not identify every extension.

Campaign/setup IDs are stable integers. API campaign IDs are decimal strings. Campaign renames retain relationships; setup names normalize lowercase and are unique per campaign. Combatant logical IDs differ from storage record IDs; order uses position, not primary-key order.

Relational groups include campaigns, battle_setups, character_rosters, characters, encounters, monsters, ordered_combatants, activity_log_entries, users, account_migration, application_state, migration maps, effects, recovery snapshots, revision records, lairs and owner/viewer links.

Supported scalar extras and absent/null markers use typed records, not JSON payload columns. Unsupported nested extras and duplicate supplied IDs can cause rollback rather than silent loss. Historical log IDs are text references so history survives deletion. Ownership relationships use foreign keys.

Characters remain campaign-owned. Saved setups own their monsters; unsaved working monsters use runtime encounter records. Active/last-used setup references use stable database relationships. Service state exposes active_setup such as {"campaign_id":"12","name":"fight"}.

Older supported SQLite schemas are backed up then upgraded. Original JSON imports leave source files unchanged; old JSON becomes archival, not live storage. Database migration backups omit config/media. Restore matching pre-upgrade code/data for rollback; never fake a downgrade by editing user_version.

## Transactions and concurrency

Protected supported mutations serialize under an operation lock and outer SQLite transaction. Failure restores SQL and in-memory STATE. Broadcast waits until commit. Nested transactions use savepoints. Most protected reads return detached snapshots under the operation lock; remote D&D lookup runs outside it in a worker thread. Account mutations use serialized transactions.

One connection belongs to the event-loop thread. General uploads are outside SQL rollback and can leave orphans; bundle import has dedicated cleanup. One process per storage directory is mandatory. Serialization is not optimistic edit-conflict detection.

## Authentication and campaign scope

Users store salted scrypt hashes. Legacy users import atomically; first legacy admin is promoted if no superadmin exists. Otherwise bootstrap credentials are randomly generated and printed once. Account import completion prevents configuration from resetting/resurrecting users.

Session tokens are in memory. Cookies: scrying_glass_admin_session and scrying_glass_client_session. Authorization re-reads database users/roles. Account edits revoke both-interface sessions/sockets. POST /logout revokes only its interface; Client logout closes matching sockets.

Client users require explicit campaign grants; admin viewer rights follow ownership; superadmins can view all. Admin domain operations enforce owned target/source/destination campaigns and active encounter scope. Another owner's active runtime yields blank admin state, not access. Global display connection metadata is not returned to regular admins.

Ownership reassignment preserves client grants; changing away from admin clears ownership. Bundle ownership is not imported. One shared live campaign remains; inactive viewer selections load saved state without reviving historical turns.

Cookies use HttpOnly, SameSite=lax, secure=False. Protected browser mutations check supplied Origin and reject cross-site fetch metadata; missing headers alone are not sufficient for rejection. WebSockets check supplied Origin. Login POSTs do not use the protected-mutation dependency. Static/media mounts have no session dependency. Review TLS, proxy headers, rate limiting and exposure separately.

<!-- END preserved technical content -->
