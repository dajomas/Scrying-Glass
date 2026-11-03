# 030 - Attack statistics and persistence

[Back to technical documentation](../Technical-Documentation.md)

<!-- BEGIN preserved technical content -->
## Attack statistics: schema 8

This implementation starts from the original uploaded e0c321a archive. It does not
require or include the prior assistant's Encounter tools reduction panel or API.

### Model and attack resolution

`BattleActionRow.action` adds `reduce-stat`; these rows have `target_id`, a `stat`
(`max_hp`, `strength`, `dexterity`, `constitution`, `intelligence`, `wisdom`,
`charisma`) and positive `amount` (1–99999). `stat` is rejected on unrelated action
kinds. Reduction rows cannot be reactions or critical hits. Actor/target eligibility
uses the established battle validation. The GM resolves attack/save outcomes and
chooses the amount; no derived ability modifiers, AC or initiative are automated.

The existing `/api/battle/actions` transaction validates rows, then resolves all
pending rows in order. Damage and reduction are independent rows: max-HP reduction
clamps only above the effective maximum, does not reapply damage, consume temp HP
or invoke massive-damage/death-save mechanics. Compound persistence and audit,
one undo snapshot and deferred broadcast remain within the existing serialized
transaction. A later validation/storage failure restores live state and SQLite;
uncommitted state is not broadcast.

For batches containing reductions, `BattleActions.statistics_token` is required.
The admin state returns this token, binding the active campaign, persistent feature
revision and normalized encounter fingerprint. It is captured when Battle actions
opens, not replaced by background polling; successful applies refresh it. Stale
batches return 409. Old ordinary-action payloads need no token. Changing scope
closes the attack window; turn/source eligibility is still checked server-side.
This is concurrency protection, not a substitute for admin/origin/ownership guards.

### Bases, reductions and normalized persistence

On first use, current `max_hp` becomes `base_max_hp`. Abilities use explicit nullable
`base_strength`, `base_dexterity`, `base_constitution`, `base_intelligence`,
`base_wisdom`, `base_charisma` fields. Effective values are their unprefixed
counterparts. Bases are typed scalar entity attributes in the existing normalized
attribute tables, not JSON. Ability bases must be known integers 0–30 before a
reduction; no missing value is guessed. HP bases retain signed-64-bit storage
bounds. Legacy entities without bases/mechanics preserve their original health
normalization compatibility, including historical above-maximum current HP.

Each applied reduction creates a private manual effect with a strictly validated
payload such as `{"version":1,"stat":"dexterity","amount":3}` in `mechanical`.
Full amounts are retained and effective values floored at zero. Invalid schemas,
versions, stats, bounds or automatic-expiry/concentration payloads are rejected,
including on campaign import. The attack source is audit metadata, not recovery
ownership: deletion of the source does not remove reductions. Ordinary descriptive
conditions retain their existing behavior. Player serialization stays allowlisted
and excludes bases, scores, mechanics and admin concurrency tokens.

Schema v7→v8 adds nullable `mechanical_version`, `reduction_stat` and
`reduction_amount` columns to `characters_effects`, `monsters_effects` and
`snapshot_characters_effects` inside a migration transaction, with the normal
pre-upgrade database backup. A backup already made earlier in startup is reused.
New installs reach v8. Existing effects need no rewriting; bases opt in at use.
Snapshots/rosters/setups/runtime and bundles use the same storage paths. Bundle
format remains 1, but mechanics-bearing bundles require a compatible validator;
old applications cannot interpret them. No accounts/media are bundled into this
source overlay.

### Restoration/base API and UI

`POST /api/combatants/{ident}/statistics` runs on the admin app only via the existing
feature router, serialized transaction, same-origin/admin/campaign-ownership guards.
It requires current `token` and accepts one of:

- `{"operation":"restore","stat":"strength","token":"..."}`; `stat` can also be
  `all`. Remove all mechanical reductions matching that stat; keep bases, current
  HP, unrelated effects and ordinary encounter state. No healing/resurrection.
- `{"operation":"bases","bases":{"strength":14,"max_hp":20},"token":"..."}`;
  bases may contain supported stats, with null only for abilities without active
  reductions. Recompute effective values, clamping current HP only when needed.

The Restore statistics dialog appears beside Reset in character and monster rows.
It inspects effective values, total reductions and originals, and provides
confirmation/cancellation. Polling does not overwrite drafts. Campaign/setup
changes invalidate the dialog; stale API operations return 409. Browser base
editing is limited to JavaScript safe integers; API HP storage supports signed
64-bit values. Apply rows lock before refresh to avoid duplicate reductions when
refresh fails. No reduction controls or mechanical-effect removal are added to
Encounter tools. Ordinary Reset retains bases/reductions and respects its existing
HP result capped at the effective maximum (Original HP remains a monster reset
HP template, not a replacement for an explicitly edited base).

### Deployment and rollback

Deploy Python, static files and templates together. Back up complete storage,
media and configuration with the server stopped before upgrade; automatic database
backups omit media/configuration. Do not decrement user_version. To roll back,
restore matching baseline code and the pre-upgrade full backup; later edits are
lost in that restored copy. Older code rejects schema 8. This archive is not a
migration from the previously delivered assistant patch; apply against the original
baseline and matching data, not by overlaying both archives.
<!-- END preserved technical content -->
