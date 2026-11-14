# 220 - Admin-only active-battle statblock viewer and imports

[Back to TODO index](../../TODO.md)

## Task and status

- Identifier: SG-TODO-022.
- Status: proposed; request recorded 2026-11-14. Implementation and validation have not started.
- Priority: not assigned. No owner or deadline agreed.
- Required development branch: `features/perplexity-statblock` in `dajomas/Scrying-Glass`. All development for this TODO item, including implementation, tests and task-related documentation, must be pushed to this branch. Do not write this work to another branch or merge without explicit approval.
- This addition records planned work only; it does not deliver a working statblock viewer or imports.

## User-requested scope

### Separate admin-only viewer

1. Add an extra viewing screen on default port `3200`, restricted to admins.
2. Display monsters from the currently active battle as tiles. Each tile shows the monster name and species, with a border in that monster's configured colour.
3. Take each monster's statblock from the source used for that monster: D&D Beyond, 5e.tools, Open5e or a `.monster` file. Preserve the exact source identity, including book/edition/document where available, rather than silently substituting another same-name monster.
4. Clicking a tile expands it to display the entire available statblock, not only the AC/HP/initiative fields used by the tracker.
5. Arrow keys navigate/select tiles; Enter expands the selected tile.
6. Another click or Escape collapses the expanded statblock back to its tile.

### Individual import

Add an import-statblock button in the Edit Monster modal. Present all viable statblock source options for that monster, following the existing monster-image selection interaction. Include the supported online providers and `.monster` file import where viable; do not silently choose one candidate when multiple viable variants exist.

### Bulk import

Add a load-statblocks option to the monster bulk-action dropdown for selected monsters. Present all viable source options similarly to the monster-image workflow, with a row and independent choice per selected monster. Show progress and useful per-monster lookup/import results. Cancel or keeping the current choice must leave existing statblocks unchanged.

## Dependencies and implementation preparation

- Follow the live `PERPLEXITY_INSTRUCTIONS.md` and inspect the actual server, authentication, active-battle projection, provider adapters, `.monster` parser, persistence, deployment and tests before implementation.
- Reuse the established image-selector interaction where appropriate: [source-image workflow and accepted follow-ups](../handover/650-monster-source-image.md). This is an interaction reference, not evidence that the current image lookup already supplies complete statblocks.
- Preserve existing source-selection and provider-switch rules: [SG-TODO-016](160-source-based-monster-selection.md), [SG-TODO-017](170-open5e-monster-source.md) and [source workstream history](../handover/590-monster-source-workstream.md).
- Verify which full-statblock fields each viable provider and the current `.monster` format can actually supply. D&D Beyond is requested as a source; full-statblock availability is not yet verified. Do not reopen cancelled account-backed access ([SG-TODO-004](040-dndbeyond-account-access.md)), bypass access restrictions or promise unavailable content. Record any provider limitation and seek a scope decision if it prevents a requested acceptance criterion.
- Determine the necessary persistence/import/export migration so a statblock remains associated with the correct monster and source. Document any backup or migration requirement before delivery.
- Add the third listener's configuration/start-up/deployment support, including collision handling consistent with the existing plain port-in-use error. Update operator/user documentation when the capability is implemented, not as if already delivered.

## Proposed implementation safeguards and details

These clarify a proposed implementation; they are not claims of completed work or separately agreed product decisions.

- Enforce authentication and campaign/active-battle authorization on the viewer, its data endpoints and live-update connections. A separate port or a hidden link is not access control. Deny client-only and unauthenticated access and prevent leakage to Client Display payloads or public media.
- Confirm whether superadmins may view directly or must use the regular-admin workflow; do not infer authorization merely from the role name.
- Keep the tiles synchronized when the active battle, monster membership, name/species or colour changes. Display explicit no-active-battle, empty, missing-statblock, loading and error states rather than stale data.
- Use visible keyboard focus, predictable navigation matching the responsive tile grid, and return focus to the originating tile after collapse. Define the click-to-collapse target so selecting text, scrolling long statblocks and following supported links remain usable.
- Render complete supported statblock content, including abilities, traits, actions and other sections present in the source; safely handle provider-specific formatting and untrusted imported text/HTML. Show source attribution and applicable provider licence metadata. Missing content must be explicit, never invented or assembled from unrelated editions.
- Distinguish automatic original-source retrieval from an admin's explicit alternative-source import. Preserve statblock provenance and do not accidentally change the monster's existing combat values, image or lookup provenance when importing a statblock.
- Deduplicate matching source/species lookups while retaining independent choices for monsters of the same species. Report unavailable providers without presenting a reduced set as exhaustive or importing another source automatically. Define statblock-specific failure and retry behavior rather than inheriting partial image-lookup semantics without review.
- Validate file type, size and content for `.monster` imports; handle older files or formats with no complete statblock explicitly. Do not claim file compatibility before inspecting the parser and fixtures.

## Acceptance criteria

- [ ] A separate configurable listener defaults to port 3200; start-up, port-in-use errors and deployment instructions cover it.
- [ ] Only authorized admins can access the viewer and its data/live-update transports; unauthenticated and client-only access is rejected, with the superadmin rule explicitly documented and tested.
- [ ] Tiles represent the currently active battle's monsters and display each monster's name, species and configured border colour, including distinct instances of the same species.
- [ ] Available statblocks are associated with the exact source used for the monster; unavailable or ambiguous sources show an actionable state without silent substitution.
- [ ] Click and Enter expand a tile to the entire available statblock; another click and Escape collapse it. Arrow-key navigation, visible focus and focus restoration work.
- [ ] Edit Monster includes statblock import with all viable source options and explicit source/candidate selection where needed.
- [ ] The bulk dropdown loads statblocks only for selected monsters and permits independent source choices, with progress, cancellation and per-monster outcomes.
- [ ] D&D Beyond, 5e.tools, Open5e and `.monster` source paths are implemented and verified where viable; any nonviable requested path is documented and explicitly resolved with the user before closing the task.
- [ ] Imported statblocks and provenance survive the agreed persistence/reload and supported export/import workflows without unintended changes to combat values or images.
- [ ] Rendering/imports reject unsafe content and malformed input, preserve source attribution and handle missing/long statblocks and provider failures clearly.
- [ ] Existing Admin, Client Display, image selection, monster lookup, combat and campaign authorization workflows remain functional.
- [ ] Implementation, tests, documentation and evidence are delivered on `features/perplexity-statblock`; required validation and user acceptance are recorded before closure.

## Required validation

Prepare and run relevant server/unit tests for source mapping, exact-source identity, persistence, `.monster` parsing, individual/bulk imports, input validation, permissions and the additional listener/port conflict. Add browser coverage for the tile grid, click/Enter expansion, arrow navigation, Escape/click collapse, focus return, source selection, independent bulk choices and active-battle updates. Include Chromium/Firefox end-to-end checks and responsive/accessibility checks where supported by the project tooling, and regression coverage for existing viewer/image workflows.

Use fixtures for deterministic provider variants and failures, but distinguish them from live provider verification. Record actual checks, covered commits and limitations; do not claim live-source availability, passing CI or manual acceptance without evidence. CI and local test execution are not required for this documentation-only task addition; use `[skip ci]` in its commit message. No tests have been run for this addition.

## Bounded implementation plan - 2026-11-14

### Delivery rules

This is the proposed implementation sequence, not evidence of implementation or an authorization for future writes. Each numbered unit targets one focused assistant implementation/review cycle and preferably one coherent commit, including its tests and necessary documentation. No duration or single-attempt success is guaranteed. All units are pending. Execute in order unless the dependency column permits otherwise; never combine provider adapters or both import UIs merely to reduce the number of commits.

Before each unit, inspect its live code and tests. If it exposes an unresolved contract, unsupported source format, substantial refactor or delivery-size risk, stop at that boundary and propose a smaller named subunit before preparing a large change. Do not silently omit tests or requirements to fit one cycle. Fix a failed unit before building on it; preserve a working branch between units. Foundation units explicitly do not constitute a complete usable feature.

Every implementation unit updates this task's progress/evidence and the relevant indexed handover; add a handover section/index link at the first implementation delivery. Preserve existing task/index links. Update user/technical/deployment documentation as the relevant capability is delivered. Each write needs its own complete bound confirmation. Documentation-only commits use `[skip ci]`; implementation/workflow commits do not unless explicitly requested.

### Starting evidence and planning limits

Planning baseline: branch commit `821db20b5591e219c269f017e6af2a6d9d4119a4`, following task addition `9b475ba5c7961d370e8767dfa3a0b6262cb1b18e`. The branch-test trigger includes this branch; no CI result was reviewed. Automatic evidence publication remains separately blocked by the publisher's branch filter on `main`; do not modify `main` under this plan without explicit approval. Tests can still be reviewed from user-supplied CI evidence. The full Playwright e2e suite remains separate from CI unless explicitly changed.

Code inspected for planning: `scrying_glass_server.py` currently composes two FastAPI applications sharing runtime state; `python/scrying_glass_monster_source_snapshot.py` validates/signs online source identities, not full statblocks; `python/scrying_glass_fivetools.py` exposes a limited stats/image projection; `python/scrying_glass_json_import.py` validates JSON text but does not establish `.monster` format support. Existing image-selector behavior is documented in handover 650. These reads inform boundaries, not a claim that all affected code or live providers have been audited.

### Units and exit gates

#### 022.01 - Resolve feasibility and freeze the contract

Depends on: none. Deliver a short design record in this task/relevant handover, not feature code. Inspect all three current provider adapters, the actual `.monster` parser and representative files, storage/import/export/copy/reset paths, active-battle membership and auth/session composition. Establish a source/section capability matrix from fixtures and permitted live probes where available. Decide the versioned statblock shape, exact-source key, missing/error states, selection/apply contract, payload limits, caching and invalidation rules. Define whether dead/unjoined monsters count as active-battle members, the superadmin rule, click-collapse target and legacy identity-less behavior. Record whether a migration is needed and its backup requirements. Gate: open consequential choices are resolved with the user, unsupported provider/format paths explicitly dispositioned, and subsequent units have stable interfaces. Do not infer complete D&D Beyond access from name lookup or silently reduce the requested scope.

#### 022.02 - Implement the statblock model and persistence

Depends on: 01. Add bounded, versioned normalized content and provenance storage using the agreed schema. Cover database load/save and any required migration without adding provider/network behavior. Keep absent statblocks compatible with existing rows; never alter combat values or image/source identity accidentally. Tests: valid/invalid model, limits, legacy load, persistence round trip and migration/rollback where applicable. Gate: storage contract is tested; no viewer or importing UI is promised.

#### 022.03 - Preserve statblocks across lifecycle operations

Depends on: 02. Wire the agreed model into setup/campaign export/import, copy/move, checkpoints/undo and reset paths identified in 01. Preserve or invalidate provenance according to the frozen contract; prevent leakage into client projections or unauthenticated media. Tests: round trips, distinct same-species instances, reset/copy behavior, malformed imported content and client-data exclusion. Gate: one persisted statblock survives the supported lifecycle, independently of provider lookups.

#### 022.04 - Add the 5e.tools statblock adapter

Depends on: 01-02. Implement exact-source full-content conversion in a focused module without changing the existing stats/image projection. Preserve section order, nested entries, source/book identity and supported special sections. Explicitly reject or mark unresolved copy/unsupported constructs rather than borrowing another edition. Tests: representative complete/nested records, same-name editions, missing fields, unsupported copy entries and malformed data. Gate: deterministic normalized output and actionable limitations; no UI work.

#### 022.05 - Add the Open5e statblock adapter

Depends on: 01-02. Implement the agreed exact-creature/document fetch and conversion, with provider switches, attribution/licence metadata and bounded requests. Tests: representative API records, actions and optional sections, missing sections, identity mismatch, timeout and malformed payload. Gate: no source substitution and no regression of existing Open5e stats/image lookup.

#### 022.06 - Add the viable D&D Beyond statblock adapter

Depends on: 01-02 and the feasibility decision. Convert only legitimately retrievable content tied to the exact monster identity; distinguish blocked/unavailable content from an empty statblock. No account/entitlement bypass or authenticated-access project. Tests: permitted representative HTML/data fixtures, formatting, identity mismatch, blocked response, changed markup and missing sections. Gate: every requested section is supported or its limitation is explicitly accepted; if nonviable, record the user-approved disposition instead of writing a guessed parser.

#### 022.07 - Add `.monster` statblock ingestion

Depends on: 01-03. Extend the actual file parser/import path to preserve complete supported statblock content and local provenance. Supply an explicit file-selection path for existing monsters according to the agreed format. Handle older files without content without fabricating fields. Tests: representative supported versions, malformed/oversized files, UTF-8/unsafe input and import/export preservation. Gate: importing content changes only intended statblock fields and a valid file can feed the shared model.

#### 022.08 - Implement source resolution and authenticated apply APIs

Depends on: 03-07, allowing only explicitly resolved nonviable paths. Add a shared exact-source resolver and candidate discovery for explicit replacement. Deduplicate by the agreed exact-source key, respect provider switches, bound work/cache size and reject arbitrary fetch URLs. Validate signed selections or equivalent server-held candidate references against monster, campaign, species, source and expiry. Add individual and per-monster bulk apply with explicit transaction/failure policy and stale-state checks. Tests: auth/ownership, tampering/expiry, disabled providers, mixed failures, unknown IDs, concurrent/stale responses, atomicity and unchanged combat/image fields. Gate: reusable backend works without either import UI; original-source retrieval never silently substitutes candidates.

#### 022.09 - Add the protected third listener and read API

Depends on: 02-03 and agreed auth contract from 01. Add the statblock FastAPI application, configuration/CLI default 3200, safe static wiring, port validation/collision reporting and shared lifecycle/shutdown behavior. Implement the admin-only active-battle projection/read endpoint; no public statblock media mount. Include deployment/preflight adjustments and session-expiry behavior. Tests: listener/config construction, all pairwise duplicate ports, occupied port, admin/client/unauthenticated and cross-campaign access, logout/restart and private-data exclusion. Gate: protected shell and read data work; no complete viewer interaction is claimed yet.

#### 022.10 - Render tiles and complete safe statblocks

Depends on: 08-09. Add focused viewer assets and safe rendering for the normalized format. Show one tile per agreed battle member with name/species/configured border colour. Clicking expands full supported content and clicking the agreed target collapses it. Display attribution, long-content scrolling and explicit empty/loading/error/missing states. Tests: real rendered fixtures covering every agreed section, malicious content/URLs, duplicate species, colours, long names and mouse expand/collapse. Gate: useful mouse-driven viewer with fixture-backed complete rendering; no keyboard or live-sync completion claim.

#### 022.11 - Add keyboard and accessibility behavior

Depends on: 10. Implement grid-aware arrow navigation, Enter expansion, Escape collapse, visible focus, accessible names/expanded state and focus return. Prevent expansion/collapse handlers from disrupting text selection, links or scrolling. Tests: first/last rows, resized/incomplete grids, removed focused tile, narrow widths, focus containment as applicable and axe checks in both supported browsers. Gate: keyboard and mouse paths meet the same behavior contract.

#### 022.12 - Add live synchronization and original-source loading

Depends on: 08, 10-11. Connect authorized state updates/recovery to tile membership, names/species/colours and selected statblocks. Retrieve missing original-source statblocks automatically at the agreed lifecycle point, not on every broadcast/render. Recheck auth after campaign/session changes; discard stale in-flight results. Tests: start/end/switch battle, join/remove/update, same-species distinct sources, reconnect/logout/restart, slow provider after campaign switch and failed lookup retry/deduplication. Gate: viewer stays current without exposing a prior campaign or losing safe keyboard focus.

#### 022.13 - Add Edit Monster statblock import

Depends on: 07-08 and 10. Add the button and shared source-selection dialog, showing all viable provider/file options with attribution and progress. Use staged selection saved with the agreed Edit action; Cancel keeps existing content. Protect against species changes, stale lookup results and replacement of unrelated fields. Tests: each viable source, variant selection, file input, save/cancel, errors and coexistence with image selection. Gate: one monster can import/replace its statblock end to end; bulk UI remains pending.

#### 022.14 - Add selected-monster bulk statblock import

Depends on: 08 and 13. Add the bulk dropdown option and one row per selected monster with independent choice/keep-current, shared in-flight lookups, progress and explicit apply outcomes. Preserve unselected monsters and enforce the frozen failure/transaction policy. Tests: empty selection, mixed species/sources, same-species independent choices, cancel/retry, malformed/unknown items and double submission. Gate: bulk workflow works without regressing existing image/bulk actions.

#### 022.15 - Integrated verification and bounded corrections

Depends on: 03-14. Run/review the configured full CI suite for the actual implementation commit and the real-server Chromium/Firefox e2e checks, including third-listener fixtures, permissions, provider/file imports, keyboard, accessibility, persistence and deployment startup. Add any missing integration tests rather than treating unit fixtures as end-to-end coverage. Keep live-provider observations separate from intercepted fixtures. Record actual results/limits. If findings appear, create one narrowly scoped corrective unit per coherent cause with its own tests and approval; do not turn this unit into an unbounded redesign. Gate: every acceptance criterion has reviewed evidence or an explicit unresolved blocker.

#### 022.16 - User acceptance and documentation close-out

Depends on: 15. Reconcile the acceptance checklist, delivered behavior, source capability matrix, backup/migration/port/auth guidance and known limitations. Obtain explicit user acceptance of the usable viewer and both import workflows, including any agreed unavailable-source disposition. Update the TODO index/task and indexed handover with tested commit/run identities. Documentation-only close-out uses `[skip ci]`. Gate: close SG-TODO-022 only after required validation and user acceptance; no merge, deployment or release is implied.

### Progress and continuation checklist

All 022.01-022.16 are pending. For each unit record: scope delivered; exact implementation commit; tests actually run; CI/e2e evidence and covered revision; outstanding checks; limitations/user decisions; and the next unit. A pushed unit with unreviewed CI is delivered with validation pending, not verified complete. Approval of this plan commit records the proposed sequence only; it does not authorize subsequent code writes or guarantee every unit finishes without a corrective cycle.

Planning-only validation: existing task requirements and inspected code were reviewed for scope/dependency coverage. No application tests, live-provider probes, CI runs or browser checks were executed for this plan. README, HANDOVER and TODO index remain unchanged because this adds detail inside the already indexed task and does not change delivered capabilities or acceptance status.

### Tetra-cube `.monster` format reference - 2026-11-14

User-supplied format reference for 022.01 and 022.07: [Tetra-cube statblock-script.js](https://github.com/dajomas/Tetra-cube/blob/master/dnd/js/statblock-script.js), repository `dajomas/Tetra-cube`, ref `master`, path `dnd/js/statblock-script.js`. Inspected Git blob SHA: `a8520dcbf739ffb4f24ec7a50607bce29886d950` (a blob identity, not a commit SHA). The GitHub connector returned a truncated file; the initial `mon`, save/load, rendering and `ReplaceTags` sections were available, but the complete helper implementation was not audited.

Confirmed in the retrieved code: `SavedData.SaveToFile` writes `JSON.stringify(mon)` into a text Blob named `<lowercase monster name>.monster`; `RetrieveFromFile` reads the file as text and assigns `JSON.parse(reader.result)` to `mon`. The file therefore contains the monster object directly, not JavaScript source or a `mon` wrapper. Treat imported content as untrusted JSON, never execute it.

Apply to 022.01: use the `mon` declaration together with save/load, `UpdateStatblock`, `AddToTraitList`, `ReplaceTags` and their helpers to establish the field/section mapping and fixtures. Cover identity/size/type/tag/alignment; armor fields and shield/natural armor; hit dice and custom HP; normal/custom movement; six ability scores; senses, saves, skills, damage/condition modifiers, languages, challenge/proficiency; custom properties; and optional action sections. Distinguish defaults and derived values from values explicitly supplied in a file. Follow helper/data-table dependencies for actual nested array shapes, armor/HP/speed calculations, formatting and proficiency; empty arrays in the declaration do not define their element schema.

Apply to 022.07: ingest and preserve supported `abilities`, `actions`, `bonusActions`, `reactions`, `legendaries`, `mythics`, `lairs` and `regionals`, including `isLegendary`, `isMythic`, `isLair`, `isRegional` and the corresponding introductory/ending descriptions. Retrieved trait rendering accesses entries as `name`/`desc`. Verify the original conditional section-display semantics and avoid silently discarding supplied content. Retain useful raw source/provenance under the agreed bounded model where necessary; `doubleColumns` and `separationPoint` are presentation hints, not combat statistics.

Account for `ReplaceTags` semantics, including `[mon]`, `[mons]`, ability modifiers, attack/save expressions and dice expressions. Name substitutions use `shortName`/`pluralName` when provided. Inspect the complete helper dependencies before implementing safe substitution; do not use JavaScript evaluation or substitute current battle-modified scores for source scores accidentally. Test custom HP/speed overrides, derived values, optional/empty sections, older/missing fields, malformed nested arrays, unknown tokens, unsafe text and representative tag expressions. Do not claim compatibility with every historical `.monster` variant solely from the default object.

This reference narrows the format-discovery work but does not complete 022.01 or 022.07. No parser, renderer, migration or tests are delivered by this documentation update; all implementation units remain pending. Other plan steps, acceptance criteria and branch restrictions are unchanged.
