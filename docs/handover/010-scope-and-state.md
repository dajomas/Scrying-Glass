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

Historical model/preparation details, original test scopes and limitations are
preserved in the [pre-rebuild current-state record](https://github.com/dajomas/Scrying-Glass/blob/1eb80fc389519542daf6f7a2ebfead214347848b/docs/handover/010-scope-and-state.md).
The model-only delivery supplied validation, canonical IDs/content digests and
limits, not a usable viewer. Its schema-8/pending-persistence wording is historical.
022.02 model/storage/startup is now accepted and closed, with reviewed activation
CI 43713643326 attempt 1 for 28d75d08febf5b595afe8145b4097410eb987986 and the
user's 13:48 CET sign-off. [Accepted record](../todo/222-statblock-persistence.md).
The approved display, model, ownership, limit and backup contracts remain binding.

## Activation preparation B - 2026-11-15

Historical preparation B: a44727ef76f810ab593305033947c84eb9af26ae, lair-v5 and
feature-v4 fixtures, backup/account/FK checks, no claimed local production pass.
Full details remain in the linked pre-rebuild record. Later activation evidence
and acceptance supersede its pending status, not its recorded evidence limits.

## Activation preparation C - 2026-11-15

Historical preparation C: 1ccd5c36afb88a99b812b79bacd5a63c7c194654, attack-v7
backup and cleanup fixtures; three isolated resource-lifetime tests passed, not
full startup or hosted CI. Full details remain in the linked pre-rebuild record.
Later accepted activation supersedes its pending status. Existing anchors remain.

## 022.03 counter-only row rebuilds - 2026-11-15

Baseline: 1eb80fc389519542daf6f7a2ebfead214347848b. [Current lifecycle details,
acceptance gates and remaining work](../todo/223-statblock-lifecycle.md).
This current-state entry supersedes earlier dated 2B.4 claims in 030 only for
counter encoding/coordination, not accepted 022.02 or unrelated task history.

Inspection found that 2B.4's custom value_kind violates the actual attribute-table
CHECK; its eight earlier isolated passes used an incomplete fixture. Do not treat
that result as production ledger validation. The corrected row uses supported
integer kind, integer_value for the counter and text_value for the exact private
version marker, with null real_value. No DDL/schema-version change or weakening
of schema assertions. Ordinary input cannot supply the reserved field; malformed
markers fail closed. The facade filters the row from ordinary dictionaries.

Setup/runtime preservation now detects counters as well as snapshots. The adapter
captures encounter-local combatant bindings and max(header,counter) before the
plain save, requires unchanged heads on stable rows and unowned rebuilt rows,
and seeds counters for retained identities even without content. Snapshot ownership
checks remain. Unchanged reattachment keeps historical content metadata; changed
content advances once; the final counter is recorded under the same transaction.
Counter-only monsters stay without snapshots. Removed IDs never seed other IDs.
Partial read/record protocols fail; legacy header-only protocols do not gain clear.

Executed: eleven exact isolated ledger/rebinding methods against real SQLite with
the production value-kind CHECK, all passed. New coverage rejects the old kind,
checks stable/foreign counter guards and partial protocols, and rolls back rebound
counters with deleted owners. This is not a full production adapter-save pass.
Eleven production writer/rebuild methods are prepared, not executed, including
setup/reopen, runtime isolation, reattachment metadata, late rollback, tampering
and deletion/new-owner separation. Header deletion is only controlled fixture
absence, not service clearing. Four changed Python modules AST-parse. Full import,
constructor/model/service, HTTP/WS/browser and covering CI remain pending.

Configured unittest discovery covers these tests; tests.yml was read, not changed
or dispatched. The intermediate commit uses [skip ci]; covering CI is deferred
until final Stage 3 code. Clearing still fails closed, and arbitrary private-only
transaction saves remain pending. 2C/2D, bundles, Stage 1/2 validation and 022.03
acceptance remain open. No viewer/provider/listener or feature completion.

README whole-tree/backup guidance, root index links and storage history were
reviewed; no cosmetic root/index edits. Deploy matching code/data only after
validation/acceptance. Schema remains 9 but older code lacks private-marker/filter
handling, so do not roll code back alone over ledger-bearing data. Keep matching
storage/config/media/code backups. No merge/deployment/release is authorized.

## Documentation entry points

- [README](../../README.md)
- [Deployment](../../DEPLOYMENT.md)
- [Technical documentation index](../Technical-Documentation.md)
- [User guide](../User-Guide.md)
- [Systemd deployment](../Systemd-Deployment.md)
- [Refactor task and acceptance](../todo/080-source-size-refactors.md)

Use live branch files as authoritative; older attachments may describe an earlier
architecture or Python requirement.
