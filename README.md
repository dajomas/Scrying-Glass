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
deploy it alone or load fragments independently. The accepted pre-009.7 core was
114,814 bytes, SHA-256
`40fca092f989bcd85eaf7f06dc02b962b662a28827864df68c998919cdf87b46`.
That is a historical baseline, not the final 009.7 source identity.
The service account needs a writable temporary directory for the generated bundle.
See [Admin split details](docs/handover/050-admin-script-split.md).

### Accepted 009.7 and overall 009 - 2026-11-12

Whole Deliverable 1, Deliverable 2, SG-TODO-009.7 and overall SG-TODO-009 are
completed and closed for the agreed scope after the user's final acceptance/
close-out request on 2026-11-12 at 22:58 CET. Earlier accepted Stages 1-4,
4A.1-4A.13 and 009.1-009.6 stay closed. Earlier pending whole-deliverable/final-review
notes are superseded by the [final evidence and acceptance record](docs/handover/570-final-0097-close-out.md).

Final integrated application revision 8da0657325818c69fc82dc1234995a5146e88ebc has
successful Branch tests 43310602854 attempt 1, published as
 dbb78d3057a2d38527bd612b948a6566a1a741e3. Direct log review confirms 1,583 Python
tests OK, 43 pytest passes and selected loaded-Admin feedback, accessibility and
Deliverable 2 composition results; all configured validation stages succeeded.
Application/test/tool/workflow tree identities match through documentation close-out
2eb3b4d8a35b8a97761c1479f1ef68275652a01d. No new test run or exhaustive log/screenshot
review, authenticated live-server, human visual or screen-reader verification is
claimed. Final acceptance is bounded to the documented scope and evidence limits,
not certification that every possible accessibility or deployment scenario was tested.

Deploy admin-feedback-controller.js?v=2, admin-feedback-view.js?v=2,
admin-feedback.css?v=2, admin-feedback-admin.js?v=6, initiative-join-gate.js?v=2,
features.js?v=6, monster-initiative-edit.js?v=2, monster-initiative-roll.js?v=3 and
setup-switch.js?v=4 with all eight fragments and templates. Retain non-superseded
Stage 4 assets including admin-dialog-accessibility.js?v=1; deploy the complete tree.
The final core bundle is 131,939 bytes and the Admin script inventory is 44.
Existing endpoints, payloads, permissions, combat/initiative/server gates, drafts
and selections remain. [Deliverable 2 scope and limits](docs/handover/560-connection-field-feedback.md)
include unchanged Client Display reconnect behavior and no guessed server-detail
field mapping. Historical asset lists describe their dated checkpoints only.

No agreed 009.7/009 implementation or acceptance action remains. Deferred test-suite
cleanup remains separate work. The source-selection/Open5e workstream (016/017) has
an accepted plan with Stage 1 recorded in
[590](docs/handover/590-monster-source-workstream.md); Stage 2 (Open5e provider and
provider switches) is delivered with CI pending and Stage 3 is not started. SG-TODO-019 is also completed and closed for
its agreed Activity log Details scope after final user acceptance on 2026-11-13 at
09:04 CET. Tested implementation 4a1feb47654ea6665862ec44b3f52dc6a27458b8 on
features/perplexity has successful Branch tests 43386246710 attempt 1, evidence
publication 5b1a0a6270adea9e67ca9ffd1def534b875f1317. [580 close-out and evidence limits](docs/handover/580-activity-log-result-details.md#sg-todo-019-accepted-close-out---2026-11-13)
supersedes its earlier CI/acceptance-pending notes; old entries are not rewritten,
and no new authenticated live-server, human visual or screen-reader review is
claimed. Closure does not authorize merge, deployment or a release operation.
The [009.7 task plan](docs/todo/097-feedback-delivery-plan.md) and [parent checklist](docs/todo/090-admin-usability-redesign.md)
retain their accepted scope/history. Earlier README checkpoint detail is preserved
in the [pre-final-009-close-out README](https://github.com/dajomas/Scrying-Glass/blob/2eb3b4d8a35b8a97761c1479f1ef68275652a01d/README.md).

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

Launchers accept Python 3.10 or newer and require working standard-library sqlite3. This
minimum is not a full dependency/Python compatibility matrix. Run exactly one
application process per storage directory; workers/replicas are unsupported.
A modern browser is required. Node and Playwright are test tooling, not runtime
requirements. Choose a reviewed code revision before deployment.

```bash
python3.10 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
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

Add monster and source-candidate lookup for Refresh search all enabled public
providers, retaining D&D Beyond and configured 5e.tools versions together even
when D&D Beyond returns usable matches. Distinct provider/book/edition candidates
keep their own statistics and signed source identities; statistics are not merged.
Any enabled-provider failure or incomplete configured-book search blocks the
combined lookup and returns no candidates. Retry or enter stats manually; partial
results are not offered as exhaustive. D&D Beyond book metadata that is unavailable
remains explicitly unavailable rather than guessed. No account authentication or
entitlement filtering is added.

In Add monster, one candidate is automatic and multiple candidates open a selection
dialog. There is no separate initiative-bonus confirmation. Available source
bonuses fill blank fields; the overwrite checkbox covers AC, HP range and initiative
bonus. With overwrite enabled, an explicitly missing source bonus clears the input
to blank, using the existing default-zero path without source-bonus attribution.
With overwrite disabled, an existing bonus is preserved. Invalid/ambiguous source
bonuses and failed/empty/cancelled lookups do not erase the current bonus. Values
edited during lookup or candidate selection remain unchanged, including edit then
revert. An explicit source zero remains distinct from a defaulted zero. Signed
offers stay bound to the selected candidate and assigned value; a later manual
edit, reset or changed selection clears attribution. Unsigned values remain manual.
Initiative bonus is in Combat statistics between HP Range end and Quantity; its
long help paragraph is removed. Leaving Monster species fills a blank Monster name
from trimmed species without replacing existing names.
Cancel permits manual entry. Refresh retains exact source identities without silently
selecting another provider, book or edition. For identity-less rows, exactly one
usable signed candidate resolves automatically; multiple candidates require explicit
selection and zero remain unresolved with a status. Invalid retained identities or
failed exact-source fetches never trigger substitution. Resolving another row keeps
other rows' candidates, proposals and individual field choices. Reload review starts
a fresh lookup; continuation does not refetch unaffected rows. Auto-resolution selects
no fields, changes no live statistics and generates no HP. The selected image snapshot
is retained; a missing image does not select another monster's image. Explicit Apply
remains required in Refresh. See [A.3 delivery and validation](docs/handover/340-combined-monster-lookup.md#a3-sole-candidate-refresh---2026-11-08).

Notifications and popup choices share descriptive book/year labels. Raw IDs, URLs
and selection tokens remain unchanged. Default 5e.tools sources are MM, XMM, PHB,
XPHB, DMG, XDMG, in that order. An explicit `fivetools_sources` list replaces them;
`[]` skips 5e.tools data requests without disabling D&D Beyond. Existing explicit
MM/XMM settings remain two-source overrides. Remove or expand the key, then restart,
to use more. Sources are case-sensitive; invalid lists fail validation; at most 32
input entries. A configured book absent from the provider index is an incomplete
search, not a successful zero-match result. Entries from unconfigured books are
not offered.

For compatibility, `dndbeyond_image_lookup` and `fivetools_fallback` retain their
names/defaults. In candidate lookup, `fivetools_fallback` independently enables
5e.tools rather than restricting it to D&D Beyond zero matches. Legacy stats/image
fallback interfaces are otherwise unchanged. Admin source help and config-example
comments describe combined search and fail-closed behavior. See
[combined lookup delivery](docs/handover/340-combined-monster-lookup.md)
and [source configuration and labels](docs/handover/230-fivetools-sources.md).

AC accepts numbers/AC objects; HP prefers supported dice then numeric average.
Names match after case/punctuation normalization. JSON fetches are bounded to
16 MB, use a five-second socket timeout and an in-process one-hour/32-entry cache.
Unresolved copy entries and special-only stats are not guessed; missing values
are not combined across providers/editions. Token URLs are remote, not downloaded
or cached locally, and availability is not probed. Disable both lookup providers
to prevent optional provider requests; no credentials are sent to 5e.tools.
Live-provider data/image availability is separate from intercepted-HTTP fixtures.

Open5e (SG-TODO-017 Stage 2, delivered 2026-11-13 with CI pending) is a third
provider after D&D Beyond and 5e.tools. It searches every Open5e v2 document by
exact name, validates each returned creature (the API silently ignores unsupported
filters) and fails closed like the others. Popup choices read, for example,
"5e 2014 Rules, 5th Edition 2014 (Open5e)" and show document, publisher and
licence attribution. AC, HP (dice only when the formula reproduces the listed
average) and the explicit `initiative_bonus` map through the existing offer rules;
missing values stay empty. Most creatures have no illustration; available ones are
remote Open5e images (CC BY-NC 4.0). `display.open5e_lookup` (default `true`) and
`display.open5e_base_url` (HTTPS, default `https://api.open5e.com/v2`) configure it.
A superadmin can switch D&D Beyond, 5e.tools and Open5e search on or off on the
User management page; saved switches override the three configuration keys for
candidate lookup, image lookup and Refresh. Open5e does not take part in Refresh.
See [590 Stage 2](docs/handover/590-monster-source-workstream.md#stage-2-delivery---2026-11-13).

The 10 remaining visible monster-row buttons stay on one line with table-local
horizontal scrolling and focus exposure. Name/species remain individually
unwrapped. Manual Turn buttons are excluded from both roster UIs, keyboard
navigation and accessibility navigation by scoped CSS; the legacy DOM and turn
APIs remain unchanged. Start/Next/End, turn highlighting and progression remain.
Row Damage/Heal buttons and HP change columns are removed from both combatant
tables by the loaded row-layout enhancement; other damage/healing workflows remain.
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
combatant colours or configured player-display backgrounds. Historical delivery details
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
