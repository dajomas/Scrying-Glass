# 220 - Admin-only active-battle statblock viewer and imports

[Back to TODO index](../../TODO.md) · [022.04 inheritance/reference plan](224-fivetools-statblock-resolution.md)

## Task and status

SG-TODO-022 remains an unimplemented feature. Design unit 022.01 is completed by this consolidated record on 2026-11-15 following the user's seven-item review, sixteen limit/policy decisions and 09:58 CET close-out request. 022.02 is ready to begin, not implemented; 022.03-022.16 remain pending. No owner, priority or deadline is assigned. All development remains on `features/perplexity-statblock` in `dajomas/Scrying-Glass`; no merge, deployment or release is implied.

This record is authoritative over earlier proposals and the dated continuation/status notes in the 022.04 addendum. The addendum's 022.04a-022.04f implementation scope remains required. The full earlier task, original sixteen-unit wording, inspection findings and dated decisions are preserved in the [pre-consolidation record](https://github.com/dajomas/Scrying-Glass/blob/320a0c0e3b1acedd5cdeb1b188264ec8074f1243/docs/todo/220-admin-statblock-viewer.md). Consolidation does not delete unfinished requirements or claim executable validation.

## User-requested scope

### Separate admin-only viewer

Add a separately configurable listener defaulting to port 3200. Require a regular admin with access to the active campaign; superadmin status alone and client viewer grants are insufficient. Protect pages, read APIs, preparation/apply APIs and update transports. Revoke access and clear old content on logout, role/ownership/access changes or campaign changes. Do not alter unrelated Admin or Client Display permissions.

Match the existing viewer's logical monster-card membership for the same state snapshot: `monster.active && (monster.alive || ['down', 'stable'].includes(monster.life_state))`. Preserve monster-array order and distinct instance IDs. Do not use initiative membership, `visible`, or an independent In Battle filter. Existing 750 ms exit animations do not extend logical membership or require cross-browser animation synchronization. Tiles show SG name/species and configured border colour.

At most one monster tile is expanded. Click or Enter expands; another tile replaces it. Tile/header click or Escape collapses with appropriate focus return. Arrow keys navigate the responsive grid with visible focus. Text selection, scrolling, links and supporting-reference controls must not trigger collapse. Show explicit no-campaign/empty/missing/loading/error/partial states.

### Individual import

Edit Monster offers discovery, file upload, candidate selection and preview without saving. Source-selector cancellation discards its unconfirmed choice; cancelling Edit discards all staged edits. Save atomically applies explicit ordinary monster edits and the staged statblock. Imported reference content itself never changes SG name, species, AC, current HP, max HP or initiative bonus. Preserve image and original tracker lookup identity.

### Bulk import

The selected-monster dropdown offers statblock loading, with one row and independent candidate/keep-current choice per monster. Show progress, failures and cancellation clearly; do not present partial discovery as exhaustive. Apply is atomic per request. Unselected/keep-current rows remain unchanged. Explicitly report separate batches for more than 50 targets; completed batches are not rolled back by later failures. Closing a dialog after successful Apply is not undo.

## Final display and normalization contract

SG exclusively supplies monster name, monster species, AC, current HP, max HP and initiative bonus (not rolled initiative). No source fallback or competing displayed values for these six fields; existing SG processes handle absent values. Live changes update the display without re-import or changing the reference-content revision. All other available selected-source statblock information must be presented; source numerical content is not recalculated from these SG overrides.

Resolve Tetra-cube numerical placeholders from source ability scores/proficiency using a restricted parser. Unknown expressions remain readable with a warning. `[MON]` and `[MONS]` resolve to current SG species verbatim, without automatic pluralization and without Tetra-cube regular/short/plural names. At import, replace case-insensitive complete source-creature-label occurrences in the selected creature's descriptive text with explicit species-placeholder nodes. Match full Unicode-aware words/phrases, not substrings; do not infer aliases/plurals. Preserve existing placeholders, possessive suffixes and original surrounding text. Any matching references to another creature of that same species are intentionally normalized too. Source-label fields remain provenance only. Never alter source IDs, URLs, licences or attribution.

Perform inheritance/source calculations first, then selected-creature species normalization. Reference definitions keep their own identities and are not globally rewritten as the owning creature: `Vampire Spawn` must not become `[MON] Spawn`. Root properties/type/subtitle must not duplicate the source creature name as the displayed SG identity. Preserve meaningful source qualifiers without letting source identity override SG species.

Integral linked content, such as regional effects, appears in its main section. Supporting spells, conditions, actions, rules, items, skills and related creatures are saved definitions accessible through labelled inline controls and a References section within the one expanded monster. Details start collapsed; multiple reference details may be open. Each shows its own source. Related creatures use their own reference values, not the owner's six SG values. Repeated/circular references navigate to an existing definition, never recursively nest copies. Escape collapses the monster and restores tile focus. External provider links are supplementary, not substitutes for required available saved content.

Distinguish persisted completeness `available`/`partial` from operational `missing`/`loading`/`unavailable`/`error`. An absent optional section or absent source version of an SG-owned field does not cause partial status. Unsupported/unresolved meaningful content must be preserved safely where possible, with a warning; never invent rules, silently discard content, generate assumed legendary boilerplate or substitute editions. Failed replacements leave old content intact. A successfully prepared partial replacement is visibly partial and requires explicit Save/Apply.

## Version 1 model and relational persistence

The logical snapshot is `{model_version:1, source_label, subtitle, completeness, provenance:[], facts:[], definitions:[], nodes:[], warnings:[]}`. Arrays preserve explicit order. Header/runtime metadata additionally carries a monotonically increasing `revision`, UTC `prepared_at`, and SHA-256 `content_digest`. Integers reject booleans; missing optional values are null, not fabricated defaults. IDs inside a snapshot are opaque local strings, remapped on copy/import. Source scores may be retained for derived content, but the six SG-owned values are not duplicated as authoritative display facts.

Concrete record layout, to be implemented in 022.02:

| Relation | Required fields and constraints |
|---|---|
| `monster_statblocks` | `id INTEGER PK`, `monster_id INTEGER NOT NULL UNIQUE FK monsters(id) ON DELETE CASCADE`, `model_version INTEGER CHECK=1`, `revision INTEGER >=1`, `source_label TEXT`, `subtitle TEXT`, `completeness TEXT in available/partial`, `prepared_at TEXT UTC`, `content_digest TEXT SHA-256` |
| `statblock_definitions` | `id INTEGER PK`, `statblock_id FK CASCADE`, `local_id TEXT`, `kind TEXT`, `name TEXT`, `source_code TEXT nullable`, `source_key TEXT`, `position INTEGER >=0`; unique local_id and position per snapshot; exact kind/source_key deduplication |
| `statblock_provenance` | `id INTEGER PK`, `statblock_id FK CASCADE`, nullable same-snapshot `definition_id`, `role TEXT selected/base/template/reference`, `provider TEXT`, `endpoint TEXT nullable`, `api_version TEXT nullable`, `entity_id TEXT`, `source_code TEXT nullable`, `edition TEXT nullable`, `source_url TEXT nullable`, `file_name TEXT nullable`, `file_sha256 TEXT nullable`, `adapter_version TEXT`, `position INTEGER >=0` |
| `statblock_credits` | `id INTEGER PK`, `provenance_id FK CASCADE`, `position INTEGER >=0`, `publisher TEXT nullable`, `attribution TEXT`, `license_name TEXT nullable`, `license_url TEXT nullable`; ordered multiple credits allowed |
| `statblock_facts` | `id INTEGER PK`, `statblock_id FK CASCADE`, nullable same-snapshot `definition_id`, `position INTEGER >=0`, `key TEXT`, `label TEXT`, `display_text TEXT`, `integer_value INTEGER nullable`; ordered positions unique per owner |
| `statblock_nodes` | `id INTEGER PK`, `statblock_id FK CASCADE`, `local_id TEXT`, nullable same-snapshot `definition_id`, nullable same-owner `parent_local_id TEXT`, `position INTEGER >=0`, `kind TEXT`, nullable `text`, `url`, `target_definition_local_id`, `source_path`, `label`, `enabled INTEGER 0/1`, `ordered INTEGER 0/1`; unique local_id and sibling positions |
| `statblock_warnings` | `id INTEGER PK`, `statblock_id FK CASCADE`, nullable same-snapshot `definition_id`, `position INTEGER >=0`, `code TEXT`, `source_path TEXT nullable`, `message TEXT` |

All fields are typed scalar columns, never serialized JSON payload columns. Same-snapshot/owner FKs and uniqueness must be enforced with composite constraints/indexes; root positions need a null-safe unique index. Validate parent existence, acyclicity and allowed parent/child types before any transaction. Definitions are flat roots linked by references, not cyclic content trees.

Node kinds: `section`, `entry`, `paragraph`, `list`, `list_item`, `table`, `row`, `cell`, `text`, `emphasis`, `strong`, `line_break`, `link`, `species_placeholder`, `reference`. Top-level roots are sections/entries/paragraphs/lists/tables. Lists contain list items; tables contain rows, rows cells; paragraphs and inline styles contain only inline content; text/break/placeholders/reference/link targets cannot create structural cycles. Entries/sections/cells/list items may contain ordered blocks. Preserve introductory/concluding paragraphs, names, optional enabled-state and source ordering. Tetra-cube disabled-but-populated sections remain accessible with a disabled label, including sections gated by isLegendary. Render with safe DOM construction; validated HTTPS links only, no imported HTML/JS/styles/handlers, no arbitrary URL fetches. Formatting that cannot be converted remains escaped readable text with warnings.

Digest canonicalization: compact sorted-object-key JSON, UTF-8 with non-ASCII unescaped, finite numbers only, deterministic local IDs/order. Digest covers normalized content/provenance/credits/warnings but excludes revision, prepared_at, own digest and SG live fields. Size validation covers the complete exported logical snapshot including metadata/credits/references. An adapter change invalidates conversion caches even if the resulting content digest is unchanged.

Current schema base is 8; recheck before allocating the migration version in 022.02. Back up storage, configuration and media before upgrade. Migrate transactionally with foreign-key checks and legacy no-statblock compatibility; rollback restores matching pre-upgrade code/data, not a lowered version integer. Each stored `monsters.id` owns an independent snapshot; runtime/setup/recovery/copy/undo/checkpoint/bundle round trips must explicitly preserve it. Encounter reset preserves content; deleting a row cascades. Existing encounter-save paths that rebuild rows must reattach content by validated encounter/combatant identity inside the transaction, not rely on the old database row ID. Copy/import remaps local IDs and does not confer verified online provenance. Bundle manifest limits must accommodate configured snapshots through separately validated reference members or explicitly report an aggregate limit; no silent loss. 022.03 must test the actual chosen bundle representation. Legacy imports discarded full `.monster` content, so recovery requires re-importing original files.

## Exact sources and provider capability contract

Source identity, adapter version and content digest are separate concepts. Use a canonical structured tuple, never display name alone:

| Source | Exact identity |
|---|---|
| 5e.tools | configured data-root/dataset identity, entity kind, source code, exact record name plus disambiguating record discriminator if needed; source edition/version where supplied |
| Open5e | configured HTTPS endpoint, API version, creature key, document key and ruleset/edition where supplied |
| D&D Beyond | exact numeric monster ID/canonical public monster URL, book/edition only where available |
| File | local-file provider marker and SHA-256 of original file bytes; filename is reference metadata, not identity |

Automatic retrieval uses only the retained exact identity. Manual/identity-less rows require explicit selection or file import. Explicit alternative selection updates statblock provenance only, not tracker lookup provenance or six SG fields. Validate candidate authenticity server-side; file claims of online identity are untrusted. No credentials/tokens in provenance. Preserve source attribution/licences. Respect existing provider switches for new fetches; disabling a provider does not delete saved snapshots.

| Content/evidence | 5e.tools | Open5e v2 | Public D&D Beyond | Tetra-cube file |
|---|---|---|---|---|
| Properties, abilities, saves, skills, movement, senses/languages | Source structures inspected in captured Vampire records; tags/nesting require conversion tests | Full serializer inspected; direct captured v2 records verified; preserve explicit bonuses/display strings rather than implicit all-skill defaults | Captured public Vampire pages contain content; markup extraction beyond basic tracker fields remains implementation work | Full JS model/helpers inspected; derive source values only where format defines them |
| Traits/actions/spellcasting/special sections | Traits/action/bonus/legendary/spellcasting and exact legendary groups observed; `_copy` interpreter required | Traits and action_type/order/usage mapping required; absent lair/mythic fields not invented | Old/new Vampire structures observed, not proof all public monsters work | Ordered name/desc arrays and intro/end text mapped; preserve section flags |
| Supporting definitions | Required available datasets collected by exact kind/name/source, transitive references bounded and cycle-safe | Preserve supplied content/attribution; no 5e.tools substitution | No account access/bypass or foreign-source substitution; unavailable/partial accepted | Local provenance; no assumed online authenticity or automatic source substitution |
| Unverified work disposition | Runtime pin/mode/template/default-source compatibility and complete recursive closure: 022.04a-f | All-section conversion/error fixtures: 022.05 | Changed markup, access gates, complete supported extraction: 022.06 | Older/malformed/unsafe/derived/tag fixtures: 022.07 |

Matrix labels distinguish inspected mapping, conditional mapping, genuinely not supplied, unsupported/unresolved and unverified; no row claims a tested production adapter. Preserve every available meaningful statblock field, including additional sections outside a fixed catalogue. Partial source limitations other than the accepted public-only D&D Beyond boundary remain explicit implementation blockers requiring resolution, not silent scope reduction.

Tetra-cube uses Open5e v1 conversion, not an interchangeable v2 model. Full inspected JS blob `a8520dcbf739ffb4f24ec7a50607bce29886d950`, added by `828a39e56d171d6361aa4812550f316a524daba7`, present in `5faece210f1bd5b4ce2c9a8557999faea6fff516`. `.monster` is JSON.stringify(mon). Source customHP/customSpeed govern overrides; source HP/AC formulas, CR/customProf, save/skill expertise, senses and language shapes are known. Do not reproduce lossy truthiness/bonus inference, generated descriptions, hover-presence or mythic-description conversion defects. SG's six fields override only display, not source intermediate calculations. Full compatibility still requires parser fixtures.

5e.tools pipeline: exact selected record -> inheritance/templates/ordered modifications -> required-reference collection -> safe normalization -> species placeholders -> private snapshot. Required datasets include bestiary index/files/legendarygroups, condition/disease/status, items/base items, skills, spells index/source files, variantrules and actions. `spells_` in uploaded names means `/data/spells/`. Use configured trusted roots and source-specific defaults verified against pinned runtime; never infer another edition. Follow semantic dependencies, not every metadata/reprint link. Every lookup checks the current path before following a dependency; reuse completed definitions. Inheritance/template cycles fail; supporting-reference cycles link to existing definitions. Full interpreter architecture/tests remain in 224; its dated pending-review notes are superseded here. Unknown modes cannot masquerade as resolved inheritance. Safe formula/regex implementation, upstream pin and oracle tests are mandatory 022.04 gates, not claimed done by design closure.

## Selection, read and apply interfaces

IDs are opaque strings, revisions nonnegative integers (0 means no existing statblock). Proposed private routes become the implementation contract; do not change existing image/tracker APIs:

- `GET /api/statblocks/state`: campaign_id, encounter_token, projection_revision and ordered tile summaries `{monster_id,name,species,color,ac,hp,max_hp,initiative_bonus,statblock_revision,status,warnings}`. Same authorization for private update transport; never add these snapshots to Client Display/media payloads.
- `GET /api/statblocks/monsters/{id}`: authorized same-encounter live six-field overlay plus reference snapshot, source identity and revision. No-store private responses; revisions permit avoiding redundant content transfer, not skipping permission checks.
- `POST /api/statblocks/discover`: `{campaign_id,encounter_token,monster_ids}` -> per-monster candidate summaries and per-provider completeness/failure status. Candidate IDs are server-held references, not arbitrary URLs.
- `POST /api/statblocks/prepare`: `{campaign_id,encounter_token,monster_id,expected_statblock_revision,candidate_id}` or multipart equivalent with one `.monster` file -> job_id/status. A job starts its deadline on acceptance. Completion yields selection_id, expires_at, source, completeness/warnings and preview; acceptance is not a saved change. Bind all references to session, campaign, encounter, target/species/original-source identity and revisions. Bound job results share prepared-selection lifecycle; cancellation removes unneeded jobs.
- `POST /api/statblocks/apply`: `{operation_id,campaign_id,encounter_token,items:[{monster_id,expected_statblock_revision,selection_id}]}`. Keep-current rows are omitted. Reject duplicates. Validate all rows before writing; one atomic transaction. Return applied monster IDs/new revisions or structured errors with no changes.

Edit Monster extends its ordinary save with a staged selection_id and operation_id plus expected values/revisions for fields explicitly edited. Save normal edits and statblock together. An intentional species edit in the same save is allowed, with placeholders rendering new SG species. Concurrent saved species/original-source/statblock changes invalidate preparation; unrelated newer HP/AC changes must not be overwritten by stale dialog snapshots. Conflicts on explicitly edited fields reject atomically.

Recheck authorization, campaign, encounter token, target existence, candidate/source binding, expiry and revisions in the protected apply transaction. Network/normalization happens outside the DB lock. Operation IDs bind to session and canonical request digest. A duplicate identical successful request returns its recorded outcome; changed content under the same ID conflicts. Reserve bounded outcome capacity before mutation. Outcome records share the global 1,000-reference accounting and retain through the consumed selection's original expiry (including failed retries of the same request); do not evict unexpired outcomes to admit more work. Restarts invalidate sessions/selections. Each write requires current authorization even for result replay.

Error envelope: `{code,message,items:[{monster_id,code,message,source_path?}],retry_at?}`. Use 401 unauthenticated, 403 unauthorized, 404 unavailable target, 409 stale/conflict/provider-disabled, 410 expired, 413 size/count overflow, 422 malformed/unresolvable, 429 capacity/cooldown, 504 deadline; no remote content or tokens leaked to unauthorized callers. Discovery failures distinguish unavailable/partial/error from complete zero-match results. A bounded transient retry may occur only within the same remaining end-to-end deadline and provider retry instruction; it never restarts the clock. No separate 20/45-second network budgets exist.

## Approved limits and configuration

Runtime namespace `statblocks.limits` below is the concrete naming contract. All integers are positive unless noted; MiB/KiB use 1,048,576/1,024 bytes. Values are server/operator controlled, not import-request overrides; reject invalid configuration clearly. Validate all budgets on cached/shared results too. Lowered limits apply to new preparation/import validation, not silent deletion of existing saved snapshots. All sixteen points were approved; defaults are engineering allowances, not proven universal bounds.

| Key | Default | Counting and boundary |
|---|---:|---|
| inheritance_steps | 16 | selected depth 0, each `_copy` edge +1; reject beyond cap; cycles fail immediately; cached chain logical depth still counts |
| modification_operations | 1024 | whole selected inheritance/template resolution; each instruction/removal counts, even no-match; operation lists count individually; reject beyond cap |
| reference_steps | 16 | selected depth 0; breadth-first shortest-path entity references; depth-cap definitions included, new definitions beyond cap readable/unresolved + partial |
| supporting_definitions | 256 | unique kind/name/source; includes legendary groups/related creatures, excludes selected creature and inheritance-only intermediates; deterministic BFS, overflow references explicitly partial |
| intermediate_creature_bytes | 8388608 | compact UTF-8 JSON per intermediate creature; check input/root/template/each operation, anticipate expansion before allocation; overflow fails |
| preparation_seconds | 10 | one monotonic end-to-end deadline from acceptance, including queue/network/retries/inheritance/references/normalization/validation; expiry fails without saving |
| supporting_reference_bytes | 16777216 | unique collected reference records + retained identities, before normalization; exclude datasets/main intermediate; oversized additions not added/expanded, warn partial and continue eligible smaller definitions |
| snapshot_bytes | 2097152 | complete normalized logical snapshot including metadata/provenance/credits/references/warnings; overflow fails, no silent dropping |
| content_nodes | 16384 | structural + inline nodes across snapshot; each saved definition once, each reference-link occurrence separately; facts/provenance/warnings byte-bounded, not counted as nodes; overflow fails |
| content_depth | 16 | top-level node depth 1, inline/structural child +1; each definition independent roots; no cyclic trees; overflow fails |
| text_value_bytes | 65536 | UTF-8 per logical text value before inline splitting; includes facts/credits/warnings; no artificial splitting to evade cap; overflow fails |
| response_bytes | 10485760 | each response body after decompression, enforced during reading; reject truncated/oversized result, never success-cache; core/inheritance dependency failure fails, support-only failure may yield explicit partial |
| active_jobs | 2 | global preparation jobs, bulk uses same scheduler |
| queued_jobs | 16 | global accepted waiting jobs; queued time consumes deadline; full queue rejects explicitly; fair scheduling prevents bulk monopolization |
| outbound_requests | 4 | application-wide including shared fetches |
| provider_requests | 2 | per provider, also bounded by global cap |
| worker_memory_bytes | 268435456 | total memory per isolated terminable worker; supported-platform hard enforcement must be verified; unsupported enforcement explicitly disables preparation rather than claiming a hard ceiling |
| cache_entries | 64 | shared provider/conversion LRU, bounded by bytes too |
| cache_bytes | 67108864 | retained response/conversion content separately accounted; not total process memory; successful TTL only |
| cache_seconds | 3600 | successful entries; invalidate on provider config/adapter changes |
| failure_cooldown_seconds | 30 | automatic fetch cooldown by exact identity; return reason/retry time, not false zero-match |
| selection_seconds | 600 | from completion, viewing does not extend; distinct from 10-second preparation deadline |
| prepared_snapshots | 200 | unique immutable prepared snapshots, byte limit also applies |
| prepared_bytes | 134217728 | prepared content storage; no guarantee all count slots fit at max snapshot size |
| session_selection_references | 200 | private bindings per session |
| selection_references | 1000 | global bindings including retained operation outcomes |

Retained existing preparation/apply bounds: `.monster` uploads 5 MiB; at most 50 unique targets and 1 MiB body per apply request. These are named server constants initially; changed values require documented validation. Redirects at most 3, HTTPS and configured approved provider destinations only; no credentials, arbitrary browser URLs or local/private destination traversal. Captured-file evidence is not permission to bypass access controls. In-flight cancellation/redirect/size/deadline validation must run before accepting results. Operator-trusted custom roots must still satisfy fetch safety rules.

Workers cover parsing/inheritance/modifications/references/normalization under deadline and memory isolation. Two default workers allow up to 512 MiB worker memory, excluding server/shared caches; do not call this a total process cap. Check deadline in loops and terminate blocked regex/formula workers; no eval/imported JS. A stage's working data cannot grow unbounded merely because its final serialized output would fit. Inheritance-only base/template processing is sequential and subject to the same operation/time/memory/intermediate limits; do not retain an unbounded graph. Worker-start/platform enforcement failures are explicit preparation errors, not application permission changes.

Bulk jobs are submitted successively as capacity allows; distinguish not-yet-submitted rows from accepted jobs with running deadlines. Shared exact fetches have per-consumer deadlines and logical accounting. One expired consumer does not cancel another valid consumer, but can never resume/save. Cancel queued unneeded work; stop in-flight work when no consumers remain where practical, otherwise discard it.

Cache and prepared stores are separate. Enforce both counts and bytes; failed/truncated content never becomes a successful entry. Prepared content can be shared immutably, but bindings remain private and target-specific. At capacity reject new work, never silently evict another user's unexpired selection. Release snapshots after all references expire/cancel/consume; invalidate on logout/revocation/restart and recheck permission on every use. Cache eviction does not invalidate prepared content. Provider/cache changes never automatically replace saved content. Explicit successful Apply consumes bindings; bounded outcome replay survives through original expiry as above.

## Evidence, limits and 022.01 exit audit

Inspection evidence from the original task covers server composition, auth/ownership bypasses, active storage scalar extras/schema 8, provider projections, import loss and lifecycle paths. New schema inspection confirms `monsters.id` is the database PK, scoped by encounter/combatant identity. Existing schema-module staged docstrings are not evidence the mixins are inactive. `static/client.js` blob `a528632fae747bf2016838d8afe72eb866ce47d3` establishes the membership predicate above. Open5e complete serializer blob `8e03cb97136154f68905098d9f4c111ab779ee06` was inspected upstream, not proof of deployed API revision. Tetra-cube full addition was inspected, not executed.

User-run Vampire capture at 2026-11-15T07:50:06Z: four Open5e variants, two 5e.tools books and two public D&D Beyond blocks. Python analysis decoded concatenated base64/gzip output, verified all 15 raw-response manifest hashes and independently remeasured eight extracted records. All captured HTTP statuses were 200 without truncation. Largest full dataset 1,573,620 B; largest extracted candidate 12,903 B; largest source string 924 B. MM/XMM + exact legendary groups were 7,987/7,418 B. Adding available conditions/item/skills/direct related creatures produced 20,973/14,380 B, not recursive closure. New XPHB spell and variant-rule definitions added 7,153 B before wrapper overhead; actions upload 45,532 B was inspected. These are source measurements, not normalized-node/depth/size or broad provider guarantees. Uploaded data/analysis artifacts were conversation evidence and are not bundled into this documentation commit. No third-party dataset redistribution is added.

| Original 022.01 gate | Disposition |
|---|---|
| Membership/auth/interaction/source limitations | agreed and concrete above; no unresolved product decision |
| Provider/parser feasibility and capabilities | inspected with explicit conditional/unverified matrix and assigned adapter verification gates; public-only D&D Beyond disposition accepted |
| Model/storage/migration/lifecycle contract | version 1 typed records/ownership/invariants, schema-upgrade backup and preservation rules specified; DDL implementation and round-trip tests assigned 022.02/03 |
| Exact-source/select/apply/stale/transaction policy | canonical identities, route payloads, private bindings, atomic save/conflicts/outcomes specified |
| Limits/caching/invalidation/reference presentation | seven review items and sixteen detailed policy points approved; numeric defaults/config keys and boundary behavior consolidated |
| Evidence and remaining work | captured-source analysis distinguished from application, live, upstream-oracle and normalized validation; all implementation gates remain required |

Audit result: 022.01 design complete; 022.02 ready. Detailed upstream runtime pin/operation compatibility belongs to 022.04a, not an assertion that an interpreter exists. Numeric allowances are configurable and must be measured during implementation. No remaining design uncertainty is silently converted into a passing test. Any newly discovered consequential incompatibility requires an explicit corrective design record, not guessed behavior or reopened settled decisions.

## Acceptance criteria

- [ ] Configurable protected third listener defaults to 3200, with pairwise port/occupied-port handling and deployment guidance.
- [ ] Regular-admin campaign authorization on every page/API/transport, superadmin-only/client-only/unauthenticated rejection and revocation/stale-content coverage.
- [ ] Logical tile-ID parity with existing viewer, correct SG name/species/colour and six live values; same-species instances remain separate.
- [ ] One expanded monster, mouse/Enter/arrows/Escape/focus behavior, no collapse from text/scroll/links/reference controls, responsive/accessibility coverage.
- [ ] Full safe source content and required available reference snapshots with exact-source identity, species placeholders, attribution, explicit partial/failure states and no silent substitution.
- [ ] Individual staged import and independent selected-monster bulk workflows, progress/cancel/keep-current, atomic batches, conflicts and retry-safe apply.
- [ ] All provider/file paths verified where viable; accepted D&D Beyond public-only limits; unsupported requested paths explicitly resolved before whole-feature closure.
- [ ] Backed-up migration and persistence/setup/copy/reset/recovery/undo/checkpoint/bundle preservation without changing SG combat/image/original-source data.
- [ ] Configured size/depth/work/memory/deadline/cache boundaries enforced, safe inheritance/formulas/regex and bounded cycle-safe references tested.
- [ ] Existing Admin/Client Display/image/provider/combat/campaign workflows regressions pass; actual CI/e2e/manual evidence and user acceptance recorded before closing SG-TODO-022.

## Required validation

This close-out changes documentation only and uses `[skip ci]`; no application tests, migration, browser/CI/upstream-oracle run or new live fetch was performed for it. Earlier probe syntax/synthetic helper checks and captured-data calculations are not production tests. Reuse reviewed reads by verified blob identity. README and HANDOVER describe delivered behavior and stay unchanged; add a dedicated indexed 022 implementation handover at the first code delivery. The existing 224 addendum and its shipped plan at `320a0c0e3b1acedd5cdeb1b188264ec8074f1243` remain linked.

Run relevant unit/integration/provider/security/limit tests as each unit is delivered, configured Branch tests for implementation commits, and real-server Chromium/Firefox e2e for 022.15. The workflow includes this branch but the full e2e suite is separate; automatic CI-results publication's separate branch restriction is unchanged. Do not infer CI run state merely from the marker or claim undocumented tests ran. Keep fixture/live/captured/upstream results separate and tie evidence to covered commits. Review the CI-results directory only when requested/supplied as implementation evidence; its mere presence is not statblock verification.

## Bounded implementation plan - 2026-11-14

The original sixteen-unit sequence remains; 022.04 expands into the shipped 224 subunits. Prefer one coherent bounded commit per implementation cycle including tests/docs; split at a newly discovered substantial boundary, never omit requirements to fit. Every external write needs fresh bound approval. Documentation-only messages include `[skip ci]`; implementation normally runs CI. No owner/deadline or release authority is added. Full original unit descriptions remain in the immutable pre-consolidation record above; the following exit gates retain all pending work.

### Units and exit gates

#### 022.01 - Resolve feasibility and freeze the contract

Completed design-only by this record and audit; all seven items and limits agreed. No feature implementation implied.

#### 022.02 - Implement the statblock model and persistence

Ready; depends 01. Implement typed version 1 records, validation/digests, backed-up migration and storage round trips, with legacy absent content and independent ownership. Gate: model/limits/migration/rollback tests; no provider/UI claim.

#### 022.03 - Preserve statblocks across lifecycle operations

Pending; depends 02. Setup/campaign export/import, copy/move, checkpoints/undo, recovery and reset, remapped snapshots and client-data exclusion. Gate: lifecycle/malformed/bundle-boundary tests, no silent loss.

#### 022.04 - Add the 5e.tools statblock adapter

Pending; depends 01-02. Execute [022.04a-f](224-fivetools-statblock-resolution.md): upstream pin/interfaces, exact inheritance graph, ordered general modes, creature modes/templates, supporting-reference collector/full conversion, compatibility/integration evidence. Preserve nested sections/order/identity/credits; no tracker/image regression. Gate: full required support and tested diagnostics, not routine unresolved-copy omission.

#### 022.05 - Add the Open5e statblock adapter

Pending; depends 01-02. Exact v2 creature/document full conversion, ordering/usage/attribution, provider switches, identity/timeout/malformed/missing-section tests. Gate: complete available content, no source substitution or lookup regression.

#### 022.06 - Add the viable D&D Beyond statblock adapter

Pending; depends 01-02. Exact public record only; complete supported extraction, blocked/changed-markup/identity/formatting fixtures, explicit partial/unavailable. Gate: accepted public-only boundary, no account bypass or guessed parser.

#### 022.07 - Add `.monster` statblock ingestion

Pending; depends 01-03. Full supported Tetra-cube mapping, file selection for existing monsters, local provenance, older files/custom/derived/tag/unsafe/malformed/size fixtures and export preservation. Gate: correct shared-model content without imported overrides of the six SG fields.

#### 022.08 - Implement source resolution and authenticated apply APIs

Pending; depends 03-07 except explicitly resolved nonviable paths. Exact discovery/preparation/private bindings, dedup/cache/deadline/worker policies, atomic individual/bulk apply and Edit conflicts. Gate: tamper/expiry/stale/cross-campaign/provider/capacity/idempotency/concurrency tests; no silent substitution.

#### 022.09 - Add the protected third listener and read API

Pending; depends 02-03 and auth contract. CLI/config/default3200, private static/read/transport wiring, shared startup/shutdown and preflight/deployment, all duplicate/occupied-port combinations. Gate: regular-admin-only ownership/revocation/logout/restart/campaign tests, no private-data leakage.

#### 022.10 - Render tiles and complete safe statblocks

Pending; depends 08-09. Logical membership, six-field overlay, all supported sections/definitions, source credits/status/warnings, one mouse-expanded block. Gate: malicious content/URLs, same-species instances, colours/long text/membership and reference interactions tested.

#### 022.11 - Add keyboard and accessibility behavior

Pending; depends 10. Grid-aware arrows/Enter/Escape/focus, resized/incomplete grids, removed focused tiles, labels/expanded states and non-disruptive text/scroll/links/reference details. Gate: keyboard/mouse parity, responsive and axe checks in both browsers.

#### 022.12 - Add live synchronization and original-source loading

Pending; depends 08,10-11. Authorized state/recovery, membership/six-field/colour updates, missing original-source loading on stable lifecycle events, no repeated render fetch. Gate: battle/campaign/role/reconnect/stale-fetch/removal/focus/dedup/retry tests; never expose old campaign.

#### 022.13 - Add Edit Monster statblock import

Pending; depends 07-08,10. Button/dialog/all viable source-file choices, staged atomic save, progress/errors/variants/species edits, image coexistence. Gate: every viable source save/cancel/stale flow end-to-end for one monster.

#### 022.14 - Add selected-monster bulk statblock import

Pending; depends 08,13. Independent choices/keep-current, shared lookups, bounded jobs/batches, progress/cancel/retry/outcomes. Gate: mixed/same-species/empty/unknown/double-submit tests and existing bulk/image regressions.

#### 022.15 - Integrated verification and bounded corrections

Pending; depends 03-14. Actual implementation-commit full configured CI plus real-server Chromium/Firefox e2e, access, ports, persistence, providers/files, keyboard/accessibility/refs, limits and deployment. Record live-vs-fixture limits and covered revisions; findings become narrow corrective units with tests/approval. Gate: every criterion has evidence or explicit blocker.

#### 022.16 - User acceptance and documentation close-out

Pending; depends 15. Reconcile capability/acceptance/backup/limits/port/auth/operator docs and indexed handover/TODO with tested identities. Explicit user acceptance required for usable viewer and individual/bulk flows. Gate: whole SG-TODO-022 closes only after evidence/acceptance; no merge/release/deployment inferred.

### Progress and continuation checklist

022.01 complete, 022.02 ready, remainder pending. Next implementation unit is 022.02. For every delivery record actual scope/commit/tests/CI-e2e coverage/limitations/user decisions/next step. A push with unreviewed tests is delivered with validation pending, not verified complete. Planning closure never authorizes later writes.
