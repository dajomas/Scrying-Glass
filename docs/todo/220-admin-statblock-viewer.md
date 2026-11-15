# 220 - Admin-only active-battle statblock viewer and imports

[Back to TODO index](../../TODO.md)

## Task and status

- Identifier: SG-TODO-022.
- Status: proposed feature; 022.01 design review in progress as of 2026-11-14. Feature implementation and executable validation have not started.
- Priority: not assigned. No owner or deadline agreed.
- Required development branch: `features/perplexity-statblock` in `dajomas/Scrying-Glass`. All development for this TODO item, including implementation, tests and task-related documentation, must be pushed to this branch. Do not write this work to another branch or merge without explicit approval.
- This addition records planned work only; it does not deliver a working statblock viewer or imports.

## User-requested scope

### Separate admin-only viewer

1. Add an extra viewing screen on default port `3200`, restricted to regular admins with access to the active campaign. A superadmin role alone does not grant access.
2. Display tiles for the same monster instances actually displayed on the existing viewer screen, including its alive/dead rendering behavior. Do not use a separate In Battle-only filter. Each tile shows the monster name and species, with a border in that monster's configured colour.
3. Take each monster's statblock from the source used for that monster: D&D Beyond, 5e.tools, Open5e or a `.monster` file. Preserve the exact source identity, including book/edition/document where available, rather than silently substituting another same-name monster.
4. Clicking a tile expands it to display the entire available statblock, not only the AC/HP/initiative fields used by the tracker. At most one statblock is expanded at a time.
5. Arrow keys navigate/select tiles; Enter expands the selected tile.
6. Clicking the expanded tile/header again or pressing Escape collapses it. Selecting text, scrolling and following a supported link must not collapse it.

### Individual import

Add an import-statblock button in the Edit Monster modal. Present all viable statblock source options for that monster, following the existing monster-image selection interaction. Include the supported online providers and `.monster` file import where viable; do not silently choose one candidate when multiple viable variants exist.

### Bulk import

Add a load-statblocks option to the monster bulk-action dropdown for selected monsters. Present all viable source options similarly to the monster-image workflow, with a row and independent choice per selected monster. Show progress and useful per-monster lookup/import results. Cancel or keeping the current choice must leave existing statblocks unchanged.

## Dependencies and implementation preparation

- Follow the live `PERPLEXITY_INSTRUCTIONS.md` and inspect the actual server, authentication, active-battle projection, provider adapters, `.monster` parser, persistence, deployment and tests before implementation.
- Reuse the established image-selector interaction where appropriate: [source-image workflow and accepted follow-ups](../handover/650-monster-source-image.md). This is an interaction reference, not evidence that the current image lookup already supplies complete statblocks.
- Preserve existing source-selection and provider-switch rules: [SG-TODO-016](160-source-based-monster-selection.md), [SG-TODO-017](170-open5e-monster-source.md) and [source workstream history](../handover/590-monster-source-workstream.md).
- Verify which full-statblock fields each viable provider and the current `.monster` format can actually supply. D&D Beyond is limited by user agreement to publicly retrievable content through the existing integration. Do not reopen cancelled account-backed access ([SG-TODO-004](040-dndbeyond-account-access.md)), bypass access restrictions or promise unavailable content. Explicit unavailable/partial states and administrator-selected alternative-source or file import are accepted; silent substitution is not.
- Determine the necessary persistence/import/export migration so a statblock remains associated with the correct monster and source. Document any backup or migration requirement before delivery.
- Add the third listener's configuration/start-up/deployment support, including collision handling consistent with the existing plain port-in-use error. Update operator/user documentation when the capability is implemented, not as if already delivered.

## Proposed implementation safeguards and details

These clarify a proposed implementation; they are not claims of completed work or separately agreed product decisions except where explicitly identified as agreed below.

- Enforce authentication and campaign authorization on the viewer, its data endpoints and live-update connections. A separate port or a hidden link is not access control. Deny client-only and unauthenticated access and prevent leakage to Client Display payloads or public media.
- Agreed 2026-11-14: require a regular admin account with access to the active campaign. Do not inherit the current generic admin dependency's superadmin bypass or treat client viewer grants as sufficient access.
- Keep the tile set identical to the existing viewer's displayed monster set when the battle, viewer membership, name/species or colour changes. Include browser-side alive/dead filtering in parity checks; do not infer membership solely from the server's active flag. Display explicit empty, missing-statblock, loading and error states rather than stale data.
- Use visible keyboard focus, predictable navigation matching the responsive tile grid, and return focus to the originating tile after collapse. At most one block is expanded. The expanded tile/header is the click-to-collapse target; text selection, scrolling and supported links remain usable.
- Render complete supported statblock content, including abilities, traits, actions and other sections present in the source; safely handle provider-specific formatting and untrusted imported text/HTML. Show source attribution and applicable provider licence metadata. Missing content must be explicit, never invented or assembled from unrelated editions.
- Distinguish automatic original-source retrieval from an admin's explicit alternative-source import. Preserve statblock provenance and do not accidentally change the monster's existing combat values, image or lookup provenance when importing a statblock.
- Deduplicate matching source/species lookups while retaining independent choices for monsters of the same species. Report unavailable providers without presenting a reduced set as exhaustive or importing another source automatically. Define statblock-specific failure and retry behavior rather than inheriting partial image-lookup semantics without review.
- Validate file type, size and content for `.monster` imports; handle older files or formats with no complete statblock explicitly. Do not claim file compatibility before inspecting the parser and fixtures.

## Acceptance criteria

- [ ] A separate configurable listener defaults to port 3200; start-up, port-in-use errors and deployment instructions cover it.
- [ ] Only regular admins with access to the active campaign can access the viewer and its data/live-update transports; unauthenticated, client-only and superadmin-only access is rejected. Campaign reassignment, role changes and logout revoke access.
- [ ] Tile monster IDs match the instances actually displayed by the existing viewer, including alive/dead display behavior, and show each monster's name, species and configured border colour. Distinct same-species instances remain separate tiles.
- [ ] Available statblocks are associated with the exact source used for the monster; unavailable or ambiguous sources show an actionable state without silent substitution.
- [ ] Click and Enter expand a tile to the entire available statblock, at most one at a time; clicking the tile/header again and Escape collapse it. Arrow navigation, visible focus and focus restoration work; text selection, scrolling and supported links do not collapse it.
- [ ] Edit Monster includes statblock import with all viable source options and explicit source/candidate selection where needed.
- [ ] The bulk dropdown loads statblocks only for selected monsters and permits independent source choices, with progress, cancellation and per-monster outcomes.
- [ ] D&D Beyond, 5e.tools, Open5e and `.monster` source paths are implemented and verified where viable. D&D Beyond is public-content only; explicit unavailable/partial states with manual alternative-source/file import are accepted. Other nonviable requested paths require documented user resolution before closure.
- [ ] Imported statblocks and provenance survive the agreed persistence/reload and supported export/import workflows without unintended changes to combat values or images.
- [ ] Rendering/imports reject unsafe content and malformed input, preserve source attribution and handle missing/long statblocks and provider failures clearly.
- [ ] Existing Admin, Client Display, image selection, monster lookup, combat and campaign authorization workflows remain functional.
- [ ] Implementation, tests, documentation and evidence are delivered on `features/perplexity-statblock`; required validation and user acceptance are recorded before closure.

## Required validation

Prepare and run relevant server/unit tests for source mapping, exact-source identity, persistence, `.monster` parsing, individual/bulk imports, input validation, permissions and the additional listener/port conflict. Add browser coverage for tile membership parity with the real viewer, click/Enter expansion, arrow navigation, Escape/header-click collapse, one-expanded-block behavior, focus return, source selection, independent bulk choices and active-battle updates. Include Chromium/Firefox end-to-end checks and responsive/accessibility checks where supported by the project tooling, and regression coverage for existing viewer/image workflows.

Use fixtures for deterministic provider variants and failures, but distinguish them from live provider verification. Record actual checks, covered commits and limitations; do not claim live-source availability, passing CI or manual acceptance without evidence. Documentation-only task/design updates use `[skip ci]`. No executable tests have been run for these design updates.

## Bounded implementation plan - 2026-11-14

### Delivery rules

This is the proposed implementation sequence, not evidence of implementation or an authorization for future writes. Each numbered unit targets one focused assistant implementation/review cycle and preferably one coherent commit, including its tests and necessary documentation. No duration or single-attempt success is guaranteed. Execute in order unless the dependency notes permit otherwise; never combine provider adapters or both import UIs merely to reduce the number of commits. Current unit status is recorded in the progress section below.

Before each unit, inspect its live code and tests. If it exposes an unresolved contract, unsupported source format, substantial refactor or delivery-size risk, stop at that boundary and propose a smaller named subunit before preparing a large change. Do not silently omit tests or requirements to fit one cycle. Fix a failed unit before building on it; preserve a working branch between units. Foundation units explicitly do not constitute a complete usable feature.

Every implementation unit updates this task's progress/evidence and the relevant indexed handover; add a handover section/index link at the first implementation delivery. Preserve existing task/index links. Update user/technical/deployment documentation as the relevant capability is delivered. Each write needs its own complete bound confirmation. Documentation-only commits use `[skip ci]`; implementation/workflow commits do not unless explicitly requested.

### Starting evidence and planning limits

Planning baseline: branch commit `821db20b5591e219c269f017e6af2a6d9d4119a4`, following task addition `9b475ba5c7961d370e8767dfa3a0b6262cb1b18e`. The branch-test trigger includes this branch; no CI result was reviewed. Automatic evidence publication remains separately blocked by the publisher's branch filter on `main`; do not modify `main` under this plan without explicit approval. Tests can still be reviewed from user-supplied CI evidence. The full Playwright e2e suite remains separate from CI unless explicitly changed.

Code inspected for initial planning: `scrying_glass_server.py` currently composes two FastAPI applications sharing runtime state; `python/scrying_glass_monster_source_snapshot.py` validates/signs online source identities, not full statblocks; `python/scrying_glass_fivetools.py` exposes a limited stats/image projection; `python/scrying_glass_json_import.py` validates JSON text but does not establish `.monster` format support. Existing image-selector behavior is documented in handover 650. Additional 022.01 findings appear below. These reads inform boundaries, not a claim that all affected code or live providers have been audited.

### Units and exit gates

#### 022.01 - Resolve feasibility and freeze the contract

Depends on: none. Deliver a short design record in this task/relevant handover, not feature code. Inspect all three current provider adapters, the actual `.monster` parser and representative files, storage/import/export/copy/reset paths, viewer membership and auth/session composition. Establish a source/section capability matrix from fixtures and permitted live probes where available. Decide the versioned statblock shape, exact-source key, missing/error states, selection/apply contract, payload limits, caching and invalidation rules. Viewer-parity membership, regular-admin campaign access, one-expanded-block interaction and public-only D&D Beyond behavior are agreed below. Finish the remaining contract detail and record migration/backup requirements. Gate: consequential choices are resolved, source/format limitations explicitly dispositioned, and subsequent units have stable interfaces. Do not infer complete D&D Beyond access from name lookup or silently reduce the requested scope.

#### 022.02 - Implement the statblock model and persistence

Depends on: 01. Add bounded, versioned normalized content and provenance storage using the agreed schema. Cover database load/save and any required migration without adding provider/network behavior. Keep absent statblocks compatible with existing rows; never alter combat values or image/source identity accidentally. Tests: valid/invalid model, limits, legacy load, persistence round trip and migration/rollback where applicable. Gate: storage contract is tested; no viewer or importing UI is promised.

#### 022.03 - Preserve statblocks across lifecycle operations

Depends on: 02. Wire the agreed model into setup/campaign export/import, copy/move, checkpoints/undo and reset paths identified in 01. Preserve or invalidate provenance according to the frozen contract; prevent leakage into client projections or unauthenticated media. Tests: round trips, distinct same-species instances, reset/copy behavior, malformed imported content and client-data exclusion. Gate: one persisted statblock survives the supported lifecycle, independently of provider lookups.

#### 022.04 - Add the 5e.tools statblock adapter

Depends on: 01-02. Implement exact-source full-content conversion in a focused module without changing the existing stats/image projection. Preserve section order, nested entries, source/book identity and supported special sections. Explicitly reject or mark unresolved copy/unsupported constructs rather than borrowing another edition. Tests: representative complete/nested records, same-name editions, missing fields, unsupported copy entries and malformed data. Gate: deterministic normalized output and actionable limitations; no UI work.

#### 022.05 - Add the Open5e statblock adapter

Depends on: 01-02. Implement the agreed exact-creature/document fetch and conversion, with provider switches, attribution/licence metadata and bounded requests. Tests: representative API records, actions and optional sections, missing sections, identity mismatch, timeout and malformed payload. Gate: no source substitution and no regression of existing Open5e stats/image lookup.

#### 022.06 - Add the viable D&D Beyond statblock adapter

Depends on: 01-02 and the feasibility decision. Convert only publicly retrievable content tied to the exact monster identity; distinguish blocked/unavailable content from an empty statblock and label partial content explicitly. No account/entitlement bypass or authenticated-access project. Tests: permitted representative HTML/data fixtures, formatting, identity mismatch, blocked response, changed markup and missing sections. Gate: requested sections are supported where retrievable, with the accepted explicit unavailable/partial behavior and manual alternative-source/file import otherwise; do not write a guessed parser.

#### 022.07 - Add `.monster` statblock ingestion

Depends on: 01-03. Extend the actual file parser/import path to preserve complete supported statblock content and local provenance. Supply an explicit file-selection path for existing monsters according to the agreed format. Handle older files without content without fabricating fields. Tests: representative supported versions, malformed/oversized files, UTF-8/unsafe input and import/export preservation. Gate: importing content changes only intended statblock fields and a valid file can feed the shared model.

#### 022.08 - Implement source resolution and authenticated apply APIs

Depends on: 03-07, allowing only explicitly resolved nonviable paths. Add a shared exact-source resolver and candidate discovery for explicit replacement. Deduplicate by the agreed exact-source key, respect provider switches, bound work/cache size and reject arbitrary fetch URLs. Validate signed selections or equivalent server-held candidate references against monster, campaign, species, source and expiry. Add individual and per-monster bulk apply with explicit transaction/failure policy and stale-state checks. Tests: regular-admin campaign access, tampering/expiry, disabled providers, mixed failures, unknown IDs, concurrent/stale responses, atomicity and unchanged combat/image fields. Gate: reusable backend works without either import UI; original-source retrieval never silently substitutes candidates.

#### 022.09 - Add the protected third listener and read API

Depends on: 02-03 and agreed auth contract from 01. Add the statblock FastAPI application, configuration/CLI default 3200, safe static wiring, port validation/collision reporting and shared lifecycle/shutdown behavior. Implement the regular-admin-only campaign-authorized viewer-parity projection/read endpoint; no public statblock media mount and no generic superadmin bypass. Include deployment/preflight adjustments and session-expiry behavior. Tests: listener/config construction, all pairwise duplicate ports, occupied port, regular-admin/client/unauthenticated/superadmin-only and cross-campaign access, logout/restart/reassignment and private-data exclusion. Gate: protected shell and read data work; no complete viewer interaction is claimed yet.

#### 022.10 - Render tiles and complete safe statblocks

Depends on: 08-09. Add focused viewer assets and safe rendering for the normalized format. Show one tile per monster actually displayed by the existing viewer, with name/species/configured border colour. Clicking expands full supported content, replacing any currently expanded block, and clicking the expanded tile/header collapses it. Display attribution, long-content scrolling and explicit empty/loading/error/missing/partial states. Tests: real rendered fixtures covering every agreed section, malicious content/URLs, viewer membership parity, duplicate species, colours, long names and mouse expansion/collapse. Gate: useful mouse-driven viewer with fixture-backed complete rendering; no keyboard or live-sync completion claim.

#### 022.11 - Add keyboard and accessibility behavior

Depends on: 10. Implement grid-aware arrow navigation, Enter expansion, Escape collapse, visible focus, accessible names/expanded state and focus return. Prevent expansion/collapse handlers from disrupting text selection, links or scrolling. Tests: first/last rows, resized/incomplete grids, removed focused tile, narrow widths, one-expanded-block rule, focus containment as applicable and axe checks in both supported browsers. Gate: keyboard and mouse paths meet the same behavior contract.

#### 022.12 - Add live synchronization and original-source loading

Depends on: 08, 10-11. Connect authorized state updates/recovery to viewer-parity membership, names/species/colours and selected statblocks. Retrieve missing original-source statblocks automatically at the agreed lifecycle point, not on every broadcast/render. Recheck regular-admin campaign access after campaign/session/role/ownership changes; discard stale in-flight results. Tests: start/end/switch battle, viewer alive/dead membership changes, join/remove/update, same-species distinct sources, reconnect/logout/restart, slow provider after campaign switch and failed lookup retry/deduplication. Gate: viewer stays current without exposing a prior campaign or losing safe keyboard focus.

#### 022.13 - Add Edit Monster statblock import

Depends on: 07-08 and 10. Add the button and shared source-selection dialog, showing all viable provider/file options with attribution and progress. Use staged selection saved with the agreed Edit action; Cancel keeps existing content. Protect against species changes, stale lookup results and replacement of unrelated fields. Tests: each viable source, variant selection, file input, save/cancel, errors and coexistence with image selection. Gate: one monster can import/replace its statblock end to end; bulk UI remains pending.

#### 022.14 - Add selected-monster bulk statblock import

Depends on: 08 and 13. Add the bulk dropdown option and one row per selected monster with independent choice/keep-current, shared in-flight lookups, progress and explicit apply outcomes. Preserve unselected monsters and enforce the frozen failure/transaction policy. Tests: empty selection, mixed species/sources, same-species independent choices, cancel/retry, malformed/unknown items and double submission. Gate: bulk workflow works without regressing existing image/bulk actions.

#### 022.15 - Integrated verification and bounded corrections

Depends on: 03-14. Run/review the configured full CI suite for the actual implementation commit and the real-server Chromium/Firefox e2e checks, including third-listener fixtures, regular-admin campaign authorization, superadmin-only rejection, viewer membership parity, provider/file imports, keyboard, accessibility, persistence and deployment startup. Add any missing integration tests rather than treating unit fixtures as end-to-end coverage. Keep live-provider observations separate from intercepted fixtures. Record actual results/limits. If findings appear, create one narrowly scoped corrective unit per coherent cause with its own tests and approval; do not turn this unit into an unbounded redesign. Gate: every acceptance criterion has reviewed evidence or an explicit unresolved blocker.

#### 022.16 - User acceptance and documentation close-out

Depends on: 15. Reconcile the acceptance checklist, delivered behavior, source capability matrix, backup/migration/port/auth guidance and known limitations. Obtain explicit user acceptance of the usable viewer and both import workflows, including any agreed unavailable-source disposition. Update the TODO index/task and indexed handover with tested commit/run identities. Documentation-only close-out uses `[skip ci]`. Gate: close SG-TODO-022 only after required validation and user acceptance; no merge, deployment or release is implied.

### Progress and continuation checklist

022.01 is in progress: first code-review findings and user decisions are recorded below; detailed contract and mapping work remains. 022.02-022.16 are pending. For each unit record: scope delivered; exact implementation commit; tests actually run; CI/e2e evidence and covered revision; outstanding checks; limitations/user decisions; and the next unit. A pushed unit with unreviewed CI is delivered with validation pending, not verified complete. Approval of a documentation commit does not authorize subsequent code writes or guarantee every unit finishes without a corrective cycle.

Planning-only validation: task requirements and inspected code were reviewed for scope/dependency coverage. No application tests, successful live-provider probes, CI runs or browser checks were executed for this design. README, HANDOVER and TODO index remain unchanged because this adds detail inside the already indexed proposed task and does not change delivered capabilities or close an implementation unit.

### Tetra-cube `.monster` format reference - 2026-11-14

User-supplied format reference for 022.01 and 022.07: [Tetra-cube statblock-script.js](https://github.com/dajomas/Tetra-cube/blob/master/dnd/js/statblock-script.js), repository `dajomas/Tetra-cube`, ref `master`, path `dnd/js/statblock-script.js`. Inspected Git blob SHA: `a8520dcbf739ffb4f24ec7a50607bce29886d950` (a blob identity, not a commit SHA). The GitHub connector returned a truncated file; the initial `mon`, save/load, rendering and `ReplaceTags` sections were available, but the complete helper implementation was not audited.

Confirmed in the retrieved code: `SavedData.SaveToFile` writes `JSON.stringify(mon)` into a text Blob named `<lowercase monster name>.monster`; `RetrieveFromFile` reads the file as text and assigns `JSON.parse(reader.result)` to `mon`. The file therefore contains the monster object directly, not JavaScript source or a `mon` wrapper. Treat imported content as untrusted JSON, never execute it.

Apply to 022.01: use the `mon` declaration together with save/load, `UpdateStatblock`, `AddToTraitList`, `ReplaceTags` and their helpers to establish the field/section mapping and fixtures. Cover identity/size/type/tag/alignment; armor fields and shield/natural armor; hit dice and custom HP; normal/custom movement; six ability scores; senses, saves, skills, damage/condition modifiers, languages, challenge/proficiency; custom properties; and optional action sections. Distinguish defaults and derived values from values explicitly supplied in a file. Follow helper/data-table dependencies for actual nested array shapes, armor/HP/speed calculations, formatting and proficiency; empty arrays in the declaration do not define their element schema.

Apply to 022.07: ingest and preserve supported `abilities`, `actions`, `bonusActions`, `reactions`, `legendaries`, `mythics`, `lairs` and `regionals`, including `isLegendary`, `isMythic`, `isLair`, `isRegional` and the corresponding introductory/ending descriptions. Retrieved trait rendering accesses entries as `name`/`desc`. Verify the original conditional section-display semantics and avoid silently discarding supplied content. Retain useful raw source/provenance under the agreed bounded model where necessary; `doubleColumns` and `separationPoint` are presentation hints, not combat statistics.

Account for `ReplaceTags` semantics, including `[mon]`, `[mons]`, ability modifiers, attack/save expressions and dice expressions. Name substitutions use `shortName`/`pluralName` when provided. Inspect the complete helper dependencies before implementing safe substitution; do not use JavaScript evaluation or substitute current battle-modified scores for source scores accidentally. Test custom HP/speed overrides, derived values, optional/empty sections, older/missing fields, malformed nested arrays, unknown tokens, unsafe text and representative tag expressions. Do not claim compatibility with every historical `.monster` variant solely from the default object.

This reference narrows the format-discovery work but does not complete 022.01 or 022.07. No parser, renderer, migration or tests are delivered by this documentation update. Subsequent user decisions below supersede earlier proposed defaults; the development branch remains unchanged.

## 022.01 - Design review and agreed decisions - 2026-11-14

### Agreed behavior - user confirmation at 23:18 CET

1. Membership: the same monster instances actually displayed on the existing viewer screen must appear as tiles on the statblock screen. The earlier proposal to include every In Battle monster, including dead monsters regardless of viewer rendering, is superseded. Inspect the real browser renderer and share or equivalently test its membership predicate; server `active` flags and initiative order alone are not sufficient. Do not alter the existing viewer to obtain parity.
2. Access: only regular admins that have access to the active campaign may access the statblock screen. Superadmin status alone grants no access. Reuse campaign access relationships, not the current generic superadmin bypass. Client-only viewer grants are insufficient. Protect pages, summaries, expanded content and update transports; clear stale content and revoke access after logout, role/ownership changes or campaign changes. Do not change unrelated Admin/Client Display permissions.
3. Interaction: at most one statblock expanded at a time. Click or Enter expands; selecting another tile replaces the expanded block. Clicking its tile/header again or Escape collapses it and restores appropriate focus. Selecting text, scrolling and following supported links do not collapse it. Arrow navigation and visible focus remain required.
4. Source limitations: D&D Beyond support is limited to publicly retrievable content through the existing integration. Explicit unavailable/partial states with manual alternative-source or `.monster` import are accepted. No account-backed access, access-control bypass, fabricated content or silent source substitution.

These decisions replace conflicting earlier proposals, including the suggestion to inherit superadmin access. They do not assert implementation or executable verification.

### Observed code findings

- `.monster`: `python/scrying_glass_monster_csv.py::parse_monster` retains only name, type-as-species, AC, HP and optional initiative bonus. Other Tetra-cube content is discarded. It reads a number from `hpText` without consulting `customHP`, and may use `natArmorBonus` as a direct AC fallback rather than computing displayed AC. `python/scrying_glass_admin_monsters.py::import_monster` accepts files up to 5 MiB and passes the reduced fields to construction. `python/scrying_glass_service_images.py::make_monster` preserves supplied fields, so the parser is an important information-loss boundary. Existing imported rows cannot reconstruct discarded content; the original file must be imported again. Full-statblock normalization must not silently change existing combat-import behavior.
- Persistence: `python/scrying_glass_storage.py` actively composes the records/schema/operations mixins at schema version 8. Despite historical staged/not-wired module docstrings, `StorageRecordsMixin` is active. Its scalar-extra encoder rejects dict/list extras. The technical architecture specifies normalized typed records rather than JSON payload columns. A nested statblock cannot simply be appended to a monster and persisted unchanged.
- Lifecycle: `python/scrying_glass_combatant.py` uses deep copies for setup snapshots and imported monsters; reset changes battle/health flags rather than reconstructing the entire row. `python/scrying_glass_feature_storage.py` stores recovery monsters through encounter persistence. `python/scrying_glass_campaign_bundle.py` normalizes and saves imported setup/encounter content and has a 10 MiB manifest limit. Dedicated statblock persistence/validation must be included in these paths; no automatic nested-data compatibility is claimed.
- 5e.tools: `python/scrying_glass_monster_selection.py` reads source records and projects them through `fivetools_candidate`; the current output contains limited tracker statistics/image/source identity, not full content. Add complete conversion without changing the existing candidate contract or borrowing unresolved copy data from another edition.
- Open5e: `python/scrying_glass_open5e.py::FIELDS` explicitly restricts requests to identity/document, AC/HP/dice, initiative and illustration. A separate full-detail projection is needed. `tests/test_open5e_provider.py` fixtures exercise that limited shape, not complete statblocks. Publisher/licence attribution is already mapped for candidates.
- D&D Beyond: `python/scrying_glass_dndbeyond.py` has bounded public-detail retrieval and access-gate/redirect checks, but the stats extractor only reads AC/HP. `monster_selection.py` adds image, source and initiative information. Complete public-content parsing remains future work; successful name lookup does not establish full-content availability.
- Membership: `python/scrying_glass_service_state.py::display_state` includes active monster cards and leaves alive/dead card behavior to the browser. `service_battle.py::clean_order` filters turn eligibility, so initiative membership is not equivalent to displayed card membership. Browser-side membership inspection remains required.
- Authorization: `python/scrying_glass_service_auth.py::require('admin', ...)` currently permits admin and superadmin; `python/scrying_glass_campaign_ownership.py` also allows superadmins. The new statblock gate must explicitly enforce the narrower agreed rule instead of inheriting either bypass.

### Proposed shared model and persistence direction

Use one provider-independent, versioned statblock model with source identity, ordered facts, ordered safe content blocks and explicit warnings. Source identity includes provider and stable monster/source identifiers (book/document/edition where available); file imports retain local provenance. Keep statblock provenance separate from the monster's original lookup identity and current name/species. Explicit replacement imports never change combat values, image or original lookup provenance accidentally.

Persist this model in dedicated relational records: a statblock header for version/provenance/attribution/content digest/import-or-fetch time; ordered facts for displayed properties; ordered section/content-block records for paragraphs/lists and supported nested content; and warnings for missing/unresolved sections. Use typed scalar columns/rows, not a nested extra or a serialized JSON payload column. Link records to the correct stored monster instance and cascade cleanup. Runtime, setups and recovery snapshots must have independent content snapshots when copied. The exact DDL and model field/type definitions remain to be frozen before 022.02.

A backed-up schema migration is proposed; the current base is version 8. Recheck the live schema before allocating the next version. Legacy monsters have no statblock until fetched/imported; never synthesize a full block from AC/HP alone. Back up the whole storage/config/media before upgrade; migration backup alone is not a full installation backup. Rollback restores matching pre-upgrade code and data rather than editing the schema version down.

Preserve complete available source text and ordering through validated content blocks; never execute imported JS or render unsanitized provider HTML. Tetra-cube derived display values and placeholders use source values, not battle-modified values. Unsupported constructs require explicit warnings/partial status, not invented replacements or silent loss.

### Proposed retrieval, status and apply boundaries

- Separate lightweight tile summaries from expanded content to avoid retransmitting every complete statblock during routine state updates. Use a private statblock projection/transport, never the Client Display payload or public media mounts.
- Distinguish `missing`, `loading`, `available`, `partial`, `unavailable` and `error`. Mark partial content and explain missing sections. An empty optional section is not by itself a provider error.
- Resolve an existing monster only against its retained exact source. Identity-less legacy/manual rows require explicit import/source selection, not an inferred original provider. Explicit alternative imports update only statblock content/provenance.
- Perform provider discovery/detail work outside the database operation lock. Recheck regular-admin campaign access, encounter identity, monster/species/source and stale selection state inside the protected apply transaction. Discard results from a changed encounter or revoked authorization.
- Use signed selections or server-held candidate references bound to campaign, monster, species, source and expiry; do not trust arbitrary browser URLs or imported claims of provider authenticity.
- Deduplicate matching exact-source work without merging editions/documents or coupling independent per-monster choices. Respect provider switches for new fetches. Define bounded cache, invalidation and retry behavior before backend implementation rather than inheriting image-only partial-result semantics.

### Remaining 022.01 work and validation limits

Finish the concrete versioned field/block schema, exact-source key details, selection/apply payloads and transaction policy, numeric payload/cache/depth limits, invalidation rules and provider/section capability matrix. Inspect the complete Tetra-cube helper/data dependencies and representative full `.monster` records, plus the real viewer's browser membership rule. These are remaining design/verification work, not reasons to ask the user to repeat the agreed behavior decisions.

URL-tool attempts to retrieve Tetra-cube raw JS, the Open5e API and the 5e.tools index returned no content. This establishes an environment retrieval limitation, not provider downtime or a live compatibility result. The Tetra-cube connector read was truncated as noted above. No application tests, live-provider availability verification, CI or browser checks were run. Relevant existing parser/provider fixtures were inspected, not executed.

Status: 022.01 in progress, with the above user-facing decisions settled and findings recorded; not yet a fully frozen implementation contract. 022.02-022.16 remain pending. This documentation commit uses `[skip ci]` at the user's request and does not implement a migration, listener, parser, API or UI. No other branch, merge, release or deployment is authorized.
