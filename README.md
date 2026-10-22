# Scrying Glass

## Compact inline HP and initiative fields

Character-table Current HP, Max HP and Initiative inputs, and monster-table
Initiative inputs, now use half their previous width (15ch to 7.5ch). Input height,
keyboard editing and numeric behaviour are unchanged. Setup-form and edit-dialog
fields are unaffected. This is a follow-up overlay compatible with the companion
theme; see [application instructions](Patch/Compact-Inputs-Apply.md).

## Looking Glass companion styling

The preceding presentation-only restyling aligns Scrying Glass with Looking Glass
using shared dark surfaces, gold accents, local font fallbacks and coordinated
controls. It does not merge the applications or change encounter data, permissions,
combatant colours or configured player-display backgrounds. See
`Patch/Restyling-Changes.md`, `Patch/Restyling-Apply.md` and
`Patch/Restyling-Validation.md` from that package for its scope and checks.

[Deployment package](DEPLOYMENT.md) · [User Guide](docs/User-Guide.md) · [Technical Documentation](docs/Technical-Documentation.md) · [Systemd Deployment](docs/Systemd-Deployment.md)

Scrying Glass, formerly Monster Display, is a self-hosted tabletop encounter manager. The GM uses an authenticated Admin interface; players use a separate Client Display. Two FastAPI applications run in one Python process, persist structured data in SQLite and deliver player updates over WebSockets.

## Capabilities

- Campaign-owned character rosters and named monster encounter setups.
- Database accounts, superadmin user management, regular-admin campaign ownership and campaign-specific client viewer grants.
- Fixed/ranged/dice HP, monster quantities, CSV and .monster imports, uploaded images and optional D&D Beyond suggestions.
- Initiative validation and ties, shared monster initiative, rounds and turn progression.
- Damage, capped healing, temporary HP, life states, manual death-save counters, actions and reactions.
- Keep the action modal open across applies; resolved action/reaction rows are locked and skipped on later applies, with an explicit Close button.
- Private/public effects, concentration links and turn-boundary expiry.
- Encounter lairs at initiative 20, bounded persistent undo, checkpoints and portable campaign bundles.
- Activity-log exports, per-setup backgrounds, viewer font sizing and synchronization status.

This is a GM-assisted tracker, not a full rules engine. Resolve dice, saves, mitigation, concentration checks, reaction availability and resurrection exceptions manually.

## Requirements and installation

The launcher scripts accept Python 3.10 or newer with standard-library sqlite3. A modern browser is required. This launcher minimum is not a claim that every Python/dependency combination has passed full application validation. Run exactly one application process per storage directory; multiple workers/replicas are unsupported. Node and browser automation are test tooling, not runtime requirements.

```bash
git clone https://github.com/dajomas/scrying-glass.git
cd scrying-glass
git checkout main
python3.10 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install 'fastapi>=0.115' 'uvicorn[standard]>=0.30' 'PyYAML>=6.0' python-multipart
cp config.example.yaml config.yaml
```

A detached checkout makes this baseline reproducible. Deliberately select a branch when developing newer changes.

## Launcher interpreter selection

`run.sh` reuses `~/dnd` if it is a complete virtual environment and its Python is
3.10 or newer. For creation, it probes `python3`, then versioned commands 3.14
through 3.10, then `python`, choosing the first compatible interpreter on PATH.
`run.ps1` and `run.bat` reuse `%USERPROFILE%\dnd`; for creation they try `py -3`
and then `python` on PATH, accepting 3.10 and newer rather than one exact minor.
All launchers reject an existing environment below 3.10 before pip installation.
They do not automatically replace or downgrade an existing supported environment.
Back up any files before manually recreating an old environment.

SQLite checks, dependencies, config path and server invocation remain unchanged.
Linux retains its dependency marker; Windows retains installation on each launch.
The manual installation example uses `python3.10`; a newer compatible executable
may be substituted. The systemd guide also uses 3.10 in its environment-creation
example and runs that environment directly, without launcher discovery or guards.
Actual Python 3.10 application startup and Windows execution still require testing;
launcher regression tests use simulated versions and mocked external commands.

## Configuration

```yaml
network:
  bind: "0.0.0.0"
  admin_port: 3000
  client_port: 3100
storage_dir: "./scrying-glass-data"
display:
  background: "#080b14"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  default_monster_color: "#842029"
  default_character_color: "#1f4e79"
  dndbeyond_image_lookup: true
```

Accounts live in SQLite, not new configuration files. Legacy security.users is imported once only. Relative storage paths resolve from the working directory; use absolute paths for services. Saved encounter display settings override the configured fallback.

CLI overrides: --config, --bind, --admin-port, --client-port, --storage-dir.

## Validate and run

```bash
.venv/bin/python -c "import sqlite3; print(sqlite3.sqlite_version)"
.venv/bin/python -m compileall -q scrying_glass_server.py python web_html
.venv/bin/python -c "from web_html.admin_html import ADMIN_HTML; print(len(ADMIN_HTML))"
.venv/bin/python -c "import scrying_glass_server"
.venv/bin/python scrying_glass_server.py --config config.yaml
```

Import checks do not initialize deployment storage, run application lifespans or test listeners. Launch the root script directly; external uvicorn module:app commands skip main-guard initialization.

| Interface | Default URL | Account |
|---|---|---|
| Battle Admin | http://SERVER:3000/ | admin |
| User Management | http://SERVER:3000/users | superadmin |
| Client Display | http://SERVER:3100/display | client/admin/superadmin, scoped by permissions |

Fresh installs print a random superadmin password once. Change it immediately, then create admin/client accounts. Superadmins land on /users rather than battle HTML. Use a regular admin for interactive battles. Assign campaign ownership and client viewer grants separately.

## Layout and deployment

Deploy scrying_glass_server.py, python/, web_html/, templates/ and static/ together. Keep package __init__.py files. web_html avoids collision with Python's html module. Admin markup is assembled from ordered templates/admin fragments; user management uses templates/users.html. Restart after imported HTML changes and reload browsers for assets.

The repository documentation directory is docs/. This set contains four self-contained documents; supplemental feature pages are not required. Package-specific instructions are in DEPLOYMENT.md; exact source identity and checksums are recorded in package-manifest.json.

## Persistence and backup

storage_dir contains scrying-glass.sqlite3, uploads/ and optional migration backups/archived legacy data. The database includes accounts/password hashes, campaigns, rosters, setups, runtime, logs and recovery state. Legacy JSON remains archival after import.

Stop the application and back up the entire directory, configuration and service unit. Automatic database migration backups omit media/configuration. Campaign bundles omit accounts, other campaigns and accumulated undo/checkpoint collections; they are not full installation backups.

## Security and limitations

Use a trusted LAN or restricted VPN/HTTPS proxy, not public default HTTP listeners. Sessions are in memory and clear on restart. Account changes invalidate sessions. Player state is filtered, but names, images, public effects, life state and relative ordering are intentionally visible. /media is a static mount without session protection.

There is one shared live active campaign, not an independent runtime per admin. Serialized transactions do not provide optimistic conflict detection for simultaneous edits. Coordinate administrators. See the other three documents for workflows, internals and operations.

## 5e.tools monster fallback

Optional monster suggestions now try D&D Beyond first, then 5e.tools JSON data.
AC accepts numeric entries and AC objects; HP prefers a supported dice formula
and falls back to the numeric average. Names match exactly after case and
punctuation normalization. The UI labels the provider and source. Existing
AC/HP overwrite and in-flight edit protection are unchanged.

Image lookup follows the same provider order when creating a monster without an
uploaded image. 5etools supplies a token URL (explicit `tokenUrl` or a generated
WebP token path when `hasToken` is set), not necessarily a full illustration.
Existing monsters' images are not retroactively updated. Image URLs are remote;
they are not downloaded or cached locally, and availability is not probed.

Configuration under `display`:
```yaml
fivetools_fallback: true
fivetools_sources: ["MM", "XMM"]
fivetools_data_base_url: "https://5e.tools/data/bestiary"
fivetools_image_base_url: "https://5e.tools/img"
```

MM is tried before XMM to retain the older-edition preference. Only configured
sources are searched: add source identifiers from the bestiary index to extend
coverage. D&D Beyond and 5etools are independently controlled: disable both
`dndbeyond_image_lookup` and `fivetools_fallback` to prevent optional provider
lookups. No credentials are sent to 5etools. Remote JSON is bounded to 16 MB per
file, fetched with a five-second socket timeout, and cached in-process for one
hour with at most 32 entries. Restart clears the cache. Source files are loaded
sequentially; configured source count affects cold-lookup latency.

Unresolved `_copy` entries without their own usable values are skipped for stats;
this is not a complete implementation of 5etools inheritance. Special-only AC/HP
is not guessed. Fallback uses a single usable source entry and does not combine
missing fields across providers/editions. Browser access to remote token hosts
and server HTTPS access to data endpoints are required. Use third-party data
and images only where permitted; none are bundled with this patch.

Run offline tests from the repository root:
```bash
python -m unittest discover -s tests -p 'test_fivetools_fallback.py' -v
```

Live validation: enter Crawling Claw and check that the notification identifies
5e.tools after D&D Beyond fails. Add a monster without uploading an image and
check its token in the player view. If no result appears, inspect WARNING logs
and verify index/source URL reachability from the service account. Token paths
and live endpoints could not be verified from the patch-build environment.
