# 140 - Viewer ownership fixture repairs

[Back to handover index](../../HANDOVER.md)

## Current state - 2026-11-16

022.02 and bounded 2B/2C/2D remain accepted and closed. Increment 3A is delivered
but its first covering CI failed. The narrow Store ZIP-harness correction below
passes locally; corrected covering CI and acceptance remain pending. Increment 3B,
final lifecycle acceptance, SG-TODO-022 Stage 1/2, 022.03 and overall 022 remain
open/unaccepted. No merge, deployment or release is authorized.

## Preserved evidence and historical sections

[Complete preceding handover](https://github.com/dajomas/Scrying-Glass/blob/e8546fb1ec14e4163faa89c326592948d6d81c46/docs/handover/140-viewer-ownership-fixtures.md)
retains every prior heading, diagnosis, correction, criterion map, CI count,
immutable archive and evidence limitation. These historical records remain part
of the handover; 3A preparation does not replace their proof or reopen accepted work.

## 2B bounded close-out - 2026-11-16

Accepted at bcb55bb4f6542ac99d95684a247ffadeb05f3a32; reviewed covering run
43899670266 attempt 1. Full criteria and limits remain in the preceding record.

## 2C bounded close-out - 2026-11-16

Accepted for the agreed clone/copy/move/Save-As scope. Tested
7c703c4d66f63bd765a780f8e5ed6a2cd465521c; successful covering run 43933600072
attempt 1; publication dae492f2e95bc378d73425f22dd5e85d9c681215. Thirteen 2C.3c
methods passed, main unittest 1,956 OK, selected pytest 43 passed, audit 218 modules
with zero failures. Counts are not unique aggregates. Full map/limits stay archived.

## 2D bounded close-out - 2026-11-16

Accepted close-out e8546fb1ec14e4163faa89c326592948d6d81c46. Tested
 ecd56957f9f147ac36d5196c23aec96d8889129c; successful covering run 43941792616
attempt 1; publication 0742d36fa6186b3764d9b3c6e4153c20f6071b08. Seventeen import
methods passed within 1,962 main tests OK; selected pytest 43 passed; audit 219
modules, zero failed. Full six-group criterion map and evidence limits remain in
the preceding handover and lifecycle record, not discarded or widened by 3A.

## 3A private bundle roundtrip - 2026-11-16

The actual campaign bundle path now exports version 2 when setup/runtime private
snapshots exist. A separate statblocks envelope has exact setup-name maps and an
encounter map keyed by normalized monster identity. Tracker-only exports stay at
version 1; imports accept versions 1 and 2. Version 1 cannot smuggle private content.
Ordinary _statblocks fields reject. No separate reference members are introduced.

Incoming maps, target identities, digests, graph shape and safe provenance URLs
validate before allocation under operator ModelLimits. Trusted stored reads/export
remain permissive when incoming limits are lowered. Imported revision/prepared_at
are removed; canonical local IDs and fresh destination metadata are assigned through
existing private storage. Source provenance/credits remain content, not verified
online authority. No provider requests, credentials, fetch authority or permissions
are added. New setups use save_new_setup; the imported recovery image is an internal
PrivateEncounterState captured by FeatureStorage. The active campaign is not switched.

The complete manifest, including private content, must fit 10 MiB or export rejects
explicitly with 413. Existing 25 MiB compressed, 100 MiB expanded and 1,000 member
limits remain. Import requires the protected outer transaction. Media paths are
registered for cleanup before write_bytes, including partial-write failure.

Eight new tests cover rich graph/credits roundtrip, checkpoint restore and reload,
independent ownership/source isolation/privacy, distinct unsaved runtime content,
legacy import/empty export, malformed maps/digest/URL/version/private-field rejection,
lowered incoming limits, explicit aggregate overflow, late private DB failure and
partial media failure cleanup. They use native SQLite/service fixtures, not actual
HTTP sessions, full-server startup or real network WebSockets.

Executed here: compile() on the complete production and test source, both successful;
AST inventory found eight new test methods. Native tests executed here: zero. No
server import, full suite, browser/E2E or fresh CI result is claimed. The existing
Branch tests workflow discovers test_*.py on features/perplexity-statblock; this code/
test delivery omits [skip ci]. Await actual covering results before acceptance.

README and HANDOVER index were reviewed and remain applicable; no new section path,
listener, UI or installation-backup claim. The TODO index retains the pending parent
scope; detailed current 3A status below supersedes its older unimplemented-bundle
wording, not its open gates. Schema remains 9; retain matching whole code/storage/
config/media backups and never roll older code alone over ledger-bearing data.
[Current task and remaining 3B gates](../todo/223-statblock-lifecycle.md).

## 3A Store ZIP-harness correction - 2026-11-16

First covering Branch tests 43955177051 attempt 1 tested exactly
 ea8b4c7342ba2b86e8c2ca7b07892fdf4ce7f7b9 and concluded failure; publication
6ca1fefebe459f797e3014331019f2f72d7cd1c4. Main Python and standalone/audit stages
failed; setup, Chromium, syntax/server import, pytest, JavaScript and artifact upload
passed. This supersedes the earlier pending-execution wording, not the scope limits.
The complete failure inventory and other possible failures have not been reconciled.

Inspected tracebacks identify Store.connection AttributeError in the ZIP-only AST
harness tests/test_bughunt_130f875.py. That harness intentionally replaces relative-
import collaborators and is not native storage proof. Repair the harness, not the
production transaction guard: provide its explicit in_transaction fixture, recursively
replace relative imports including the new function-local save_new_setup collaborator,
and supply tracker-only adapters/PRIVATE_KEY/participant-validation fixture. The
private carrier adapter rejects nonempty graphs. Version 2 is supported now, so the
unknown-version case uses 3; a separate case retains version-2 missing-envelope rejection.
No existing ZIP/media/corruption assertion is dropped; no production file is changed.

Executed locally in the Python tool: reconstructed complete production source was
verified against Git blob d2d85fc473520c43a58b6c3627bb9d77d8dad61c, then the corrected
harness ran all 20 cases: 0 failures, 0 errors, 0 skips. Real ZIP/compression/corruption/
media I/O ran with isolated collaborators. A separate mutation run removed the guard;
the single guard regression failed as expected (1 expected failure), showing that
this assertion detects guard removal. Corrected test source compilation also passed.
These are not native SQLite, full repository, HTTP, browser, private persistence or
rollback results. Full/native suites and corrected covering CI remain pending.

This test/documentation correction runs normal push CI without [skip ci]; no workflow
change, manual dispatch or SG-TODO-023 cleanup is included. 3A remains unaccepted.
