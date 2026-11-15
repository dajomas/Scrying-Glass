# 010 - Scope and current state

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-15. Dated sections below retain their historical scope.

## Repository and branch

- Repository: `dajomas/Scrying-Glass`.
- Default working branch: `features/perplexity`.
- SG-TODO-022 explicitly uses `features/perplexity-statblock`; all work for that task stays there.
- Keep changes scoped to the agreed branch unless explicitly requested otherwise.

## Initial workflow record - 2026-11-01

The Branch tests workflow was added at `.github/workflows/tests.yml` in commit
8465afc86d19340a91433f6d4d7c4112de504a23. At the time of that initial handover
the first run had not been verified. Later feature-specific evidence and limits
are recorded in the corresponding numbered sections; this entry is not a complete
application audit.

## Application context

Scrying Glass is a self-hosted encounter manager with separate FastAPI Admin and
Client applications in one process, SQLite persistence and WebSocket updates.
The root entry point is scrying_glass_server.py. Runtime dependencies are in
requirements.txt; Python, Node and browser fixtures are under tests/.

## Documentation and packaging maintenance - 2026-11-03

The user accepted the Admin and Storage refactors as done. The live size audit at
9703102f1929aedd1887c17f1d7b4a8996dfc04b found no code files above the agreed
25,000-byte existing-file allowance. Temporary CI logs are excluded from refactor
targets and are not deleted by this maintenance. SG-TODO-004's subsequent
cancellation is recorded below.

Technical-Documentation.md is an index to three files under docs/technical/, all
below 20,000 bytes. The draft split reconstructed the exact 31,226-byte source
blob 7f9861b62a11c6efeb82fcb286f5abe300f4db2e and checked 25 compatibility links.
The text and historical validation limits are preserved, except for the required
relative-link rebasing; it is not a fresh technical audit. Preservation/link
regressions accompany the split. README and deployment guidance are refreshed as
current entry points; historical detail remains in Git and numbered feature handovers.

Manifest-dependent verification is retired. deployment/check.py now performs
runtime preflight by default, accepting --runtime as a compatibility alias. It
checks Python/sqlite3/dependencies and server import, not package integrity, live
startup or authenticated workflows. Four mocked contract methods passed locally;
this is not real dependency installation/server validation. The split regression
module parsed successfully; full repository CI was not rerun.

The user approved two commits with [skip ci]: first this documentation/preflight/
test delivery, then a separately confirmed deletion of the unused manifest. The
physical presence of any legacy manifest is not a dependency of the new tooling.
No separate workflow is dispatched, and this skip request is limited to those two
maintenance commits. No application runtime or storage behavior is changed.

## SG-TODO-004 cancelled - 2026-11-03

After a user-requested integration-options review, the user concluded that none
of the investigated approaches were viable for this project and explicitly
requested cancellation. [SG-TODO-004](../todo/040-dndbeyond-account-access.md) is
cancelled, not completed; older hold/deferred references are historical and
superseded by that decision. Its archived requirements and unfulfilled acceptance
criteria are preserved. No account-backed implementation or live account
verification was started, and no credentials were collected or account accessed.
Do not resume this work without a new explicit user request.

The delivered public-provider candidate selection, imports and manual entry remain
unchanged. This is a documentation-only cancellation: no code/test/workflow/data
changes, no automated tests executed and no new CI result claimed. The user
explicitly requested [skip ci] for this cancellation push; no workflow is
separately dispatched. The TODO index now contains seven completed tasks and one
cancelled task, with none active or on hold.

## SG-TODO-022 model foundation - 2026-11-15

[Task and design](../todo/220-admin-statblock-viewer.md) · [022.04 plan](../todo/224-fivetools-statblock-resolution.md).
This indexed current-state subsection is the implementation continuity record for
the first 022 delivery. These dated progress notes supersede the design close-out's
022.02-ready status, not its approved display/model/limit contracts. 022.01 remains
complete. The user agreed to split 022.02 into 022.02a model/validation and 022.02b
persistence/migration. 022.02a code/tests are included in this delivery with full
repository CI validation pending; parent 022.02 remains in progress and 022.02b
remains pending. No statblock UI, provider adapter or persistence is delivered.

New `python/scrying_glass_statblock_model.py` exposes `ModelLimits`,
`StatblockError(code, path)`, `validate_snapshot`, `canonical_bytes` and
`content_digest`. No storage/server import wiring, schema change, network request,
runtime configuration change or new dependency is included. Schema remains 8.

The model enforces positive integer limits with default snapshot/text/node/depth/
definition budgets 2 MiB/64 KiB/16,384/16/256; strict fields/types, selected
provenance, ordered positions, owner isolation, known reference targets, acyclic
content parents, valid UTC metadata and HTTPS links without credentials. Flat
reference cycles are allowed; source/inheritance traversal is future adapter work.
Main facts cannot duplicate SG-owned name/species/AC/HP/initiative values, while
supporting definitions may retain their own values. Imported strings are data,
not HTML rendering: safe rendering still belongs to the viewer unit.

Wire conventions concretized for persistence: provenance embeds ordered `credits`
in the logical model; 022.02b must store credits in separate typed rows. Nodes have
explicit nullable `definition_id` and `parent_local_id`; facts/warnings/provenance
may omit their nullable owner. Optional metadata is permitted before persistence;
supplied revisions are >=1 and timestamps use UTC Z format. A supplied digest
must match. Partial snapshots require a warning. Unavailable supporting references
are represented by readable text/warnings, not dangling resolved-reference nodes.
Original source_label is provenance/import context, never a displayed SG name.
These conventions refine the design's logical shorthand without changing its
separate relational-table or six-field requirements.

Canonical encoding orders records/children and remaps local node/definition IDs
deterministically. The content digest excludes revision/time/digest and cannot
include live SG fields; reference identity/content and warnings remain covered.
Inline paragraph text is measured across formatting nodes to prevent splitting
from bypassing the text-value allowance. Validation returns an independent copy.

Validation actually executed during preparation: AST parsing and unittest discovery
against the two exact staged files in a disposable minimal Python package, 35
tests passed, zero failures/errors (2026-11-15). This was not a full checkout,
application integration, persistence/migration, browser, live-provider or CI run.
`tests/test_statblock_model.py` is discoverable by the existing main unittest CI
step; normal push CI applies, with no skip marker or separate workflow dispatch.
Do not mark 022.02a fully validated until covering repository results are reviewed.
No commit SHA or workflow-run identity is invented before publication.

Next: review covering CI, make any bounded corrective delivery, then 022.02b
typed save/load/replacement, revisions/cascade, backed-up migration and initializer
version guards with new/legacy/reopen/rollback tests. 022.03 retains lifecycle
export/import/copy/recovery integration. Runtime configuration mapping of the
five ModelLimits keys belongs to later server wiring; other agreed limits are
not claimed enforced by this model-only module. README and the HANDOVER root
index remain unchanged: delivered runtime behavior and existing index links
are accurate; this section is already indexed by Scope and current state.

## Documentation entry points

- [README](../../README.md)
- [Deployment](../../DEPLOYMENT.md)
- [Technical documentation index](../Technical-Documentation.md)
- [User guide](../User-Guide.md)
- [Systemd deployment](../Systemd-Deployment.md)
- [Refactor task and acceptance](../todo/080-source-size-refactors.md)

Use live branch files as authoritative; older attachments may describe an earlier
architecture or Python requirement.
