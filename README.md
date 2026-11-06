# Scrying Glass

Scrying Glass, formerly Monster Display, is a self-hosted tabletop encounter
manager. An authenticated GM Admin interface and a separate Client Display run
as two FastAPI applications in one Python process, with SQLite persistence and
WebSocket updates.

[Deployment](DEPLOYMENT.md) · [User Guide](docs/User-Guide.md) ·
[Technical Documentation](docs/Technical-Documentation.md) ·
[Systemd Deployment](docs/Systemd-Deployment.md) · [TODO](TODO.md) · [Handover](HANDOVER.md)

## Source layout and deployment

Deploy `scrying_glass_server.py`, `python/`, `web_html/`, `templates/` and the
complete `static/` tree together. Preserve package `__init__.py` files. Admin HTML
is assembled from ordered `templates/admin/` fragments, not Jinja templates.
Restart after imported HTML/Python changes and reload browsers for changed assets.

Admin source lives in eight ordered UTF-8 files under `static/admin/`, each at
most 20,000 bytes. The static adapter assembles them without separators and serves
one classic deferred script at `/static/admin.js` on both interfaces. The tracked
`static/admin.js` is a failure marker, not application source: do not overwrite it,
deploy it alone or load fragments independently. The current assembled core is
114,814 bytes, SHA-256
`40fca092f989bcd85eaf7f06dc02b962b662a28827864df68c998919cdf87b46`.
The service account needs a writable temporary directory for the generated bundle.
See [Admin split details](docs/handover/050-admin-script-split.md).

Legacy source-reading tests use a disposable assembled checkout:

```bash
python tools/run_split_tests.py -- python -m unittest discover -s tests -p 'test_*.py' -v
python tools/run_split_tests.py -- node --test tests/battle-action-apply.test.cjs
python tools/run_split_tests.py -- python tests/browser_smoke_272cc73.py
```

The real checkout and marker remain untouched. Normal CI uses this runner for
Python, pytest, Node and standalone browser/audit fixtures. Fixture results and
workflow metadata are not authenticated/live-server verification.

Technical Documentation is now an index with three topic files under
`docs/technical/`; retain that directory with the documentation. Existing technical
section anchors remain as links to the moved sections. The historical package
manifest is retired from active verification. `deployment/check.py` performs
runtime preflight only, with or without `--runtime`; it does not verify hashes,
package completeness or provenance and does not require a manifest. A legacy
manifest, if still present during staged cleanup, is unused. Use Git commit
identity or independently generated release checksums for release integrity.

## Capabilities

- Campaign-owned character rosters and named monster encounter setups.
- Database accounts, superadmin user management, admin campaign ownership and
  campaign-specific client viewer grants.
- Fixed/ranged/dice HP, monster quantities, CSV and .monster imports, images and
  optional public-provider monster suggestions.
- Initiative validation/ties, shared monster initiative, rounds and turn progression.
- Damage, capped healing, temporary HP, life states, manual death saves, actions
  and reactions; resolved action rows remain locked while the modal stays open.
- Attack statistic reductions, restoration and explicit original/base score entry.
- Private/public effects, concentration links and turn-boundary expiry.
- Lairs at initiative 20, bounded undo, checkpoints and portable campaign bundles.
- Activity exports, per-setup backgrounds, viewer font size and synchronization status.

This is a GM-assisted tracker, not a full rules engine. Resolve dice, saves,
mitigation, concentration checks, reaction availability and resurrection manually.
See the User Guide for workflows and the numbered handover for delivery history.

## Requirements and installation

Launchers accept Python 3.10 or newer with working standard-library sqlite3. This
minimum is not a full dependency/Python compatibility matrix. Run exactly one
application process per storage directory; workers/replicas are unsupported.
A modern browser is required. Node and Playwright are test tooling, not runtime
requirements. Choose a reviewed code revision before deployment.

```bash
python3.10 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python deployment/check.py --runtime
cp config.example.yaml config.yaml
.venv/bin/python scrying_glass_server.py --config config.yaml
```

Use a newer compatible Python executable if appropriate. Copy the configuration
only for fresh installations; preserve an existing config and storage on upgrade.
Preflight checks dependencies and server import/route construction, not lifespans,
storage initialization, listeners, authentication or browser workflows.

`run.sh` reuses a complete `~/dnd` environment at Python 3.10 or newer; otherwise
it probes `python3`, then 3.14 through 3.10, then `python`. Windows launchers reuse
`%USERPROFILE%\dnd`, otherwise trying `py -3` then `python`. They reject an existing
environment below 3.10 rather than replacing/downgrading it. Linux retains its
dependency marker; Windows installs on each launch. Back up files before manually
recreating an environment. Systemd runs its explicit interpreter directly, not
launcher discovery. Actual Windows execution and full Python 3.10 application
validation remain distinct from mocked launcher contracts.

## Configuration and interfaces

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

Relative storage paths resolve from the working directory; use absolute paths for
services. Saved encounter display settings override configured fallbacks. Accounts
live in SQLite; legacy `security.users` imports only once. CLI overrides are
`--config`, `--bind`, `--admin-port`, `--client-port`, `--storage-dir`.

| Interface | Default URL | Role |
|---|---|---|
| Battle Admin | http://SERVER:3000/ | admin |
| User Management | http://SERVER:3000/users | superadmin |
| Client Display | http://SERVER:3100/display | permitted client/admin/superadmin |

Fresh installs print a random superadmin password once; change it immediately.
Create regular admin/client accounts and assign ownership and viewer grants
separately. Superadmins land on /users; use a regular admin for interactive battles.

## Monster lookup and row controls

Add monster searches D&D Beyond first, falling back to 5e.tools only after zero
usable matches. Provider errors stop lookup. One candidate is automatic; multiple
candidates open a selection dialog. Cancel permits manual entry. The selected
image snapshot is retained; a missing image does not select another monster's
image. No account authentication or entitlement filtering is added.

Notifications and popup choices share descriptive book/year labels. Raw IDs, URLs
and selection tokens remain unchanged. Default 5e.tools sources are MM, XMM, PHB,
XPHB, DMG, XDMG, in that order. An explicit `fivetools_sources` list replaces them;
`[]` skips 5e.tools without disabling D&D Beyond. Existing explicit MM/XMM settings
remain two-source overrides. Remove or expand the key, then restart, to use more.
Sources are case-sensitive; invalid lists fail validation; at most 32 input entries.
See [source configuration and labels](docs/handover/230-fivetools-sources.md).

AC accepts numbers/AC objects; HP prefers supported dice then numeric average.
Names match after case/punctuation normalization. JSON fetches are bounded to
16 MB, use a five-second socket timeout and an in-process one-hour/32-entry cache.
Unresolved copy entries and special-only stats are not guessed; missing values
are not combined across providers/editions. Token URLs are remote, not downloaded
or cached locally, and availability is not probed. Disable both lookup providers
to prevent optional provider requests; no credentials are sent to 5e.tools.
Live-provider data/image availability is separate from intercepted-HTTP fixtures.

The 11 remaining monster-row buttons stay on one line with table-local horizontal
scrolling and focus exposure. Name/species remain individually unwrapped. Row
Damage/Heal buttons and HP change columns are removed from both combatant tables
by the loaded row-layout enhancement; other damage/healing workflows remain.
Characters and Monsters show read-only current/max HP in their rosters. Use the
existing row Edit dialog to change character Current HP and Max HP, then Save
character. Character and monster initiative editors retain compact 7.5ch widths.
See [row-layout handover](docs/handover/250-monster-button-layout.md) and
[roster/HP delivery and validation limits](docs/handover/310-admin-rosters.md).

## Attack statistics and presentation

Battle Actions includes ordered statistics-reduction rows for Max HP and the six
abilities. Restore statistics appears beside Reset for both combatant kinds; its
readable view/selector shows only affected statistics. A separate original/base
editor sets missing ability scores. Schema 8 requires a pre-upgrade storage backup;
the restoration-layout follow-up adds no migration. See the
[workflow](docs/User-Guide.md#attack-statistics-reductions) and
[technical contract](docs/Technical-Documentation.md#attack-statistics-schema-8).

The companion theme coordinates dark surfaces, gold accents and local fonts with
Looking Glass; it does not merge applications or alter encounter data, permissions,
combatant colours or configured display backgrounds. Historical delivery details
and validation limits remain in the indexed handover.

## Persistence, backup and security

Storage contains `scrying-glass.sqlite3`, uploads and optional migration backups/
archived legacy data. It includes accounts, campaigns, rosters, setups, runtime,
logs and recovery state. Stop the process and back up the whole storage directory,
configuration and service unit. Migration backups omit media/configuration;
campaign bundles omit accounts, other campaigns and accumulated recovery history
and are not full installation backups.

Use a trusted LAN or restricted VPN/HTTPS proxy, not public default HTTP listeners.
Sessions are in memory and clear on restart; account changes revoke sessions.
Player projections omit private state, but visible names/images/effects/life state
and relative order are intentional. `/media` is a static mount without sessions.
One shared live active campaign remains, not independent runtime per admin. Most
serialized transactions do not detect simultaneous stale edits; reduction and
restoration/base operations additionally use a scope/revision token. Coordinate
administrators and consult the technical/security and deployment documentation.
