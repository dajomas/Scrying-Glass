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
