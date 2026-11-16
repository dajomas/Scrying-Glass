# 140 - Viewer ownership fixture repairs

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-16. Original 2026-11-01 preparation baseline: `1cfb256cb090ca3834eb2f61d12eca23ce67d4f9`.

## Separate diagnoses

Run 41318275558, attempt 1, tested `f031ccf9185ad0ab0e9ad7b4673adf1f7fb5f7ad` and reported four remaining unittest errors. Each affected path was inspected and reproduced in focused local checks rather than assuming all errors were fixture defects.

- Browser: the `/api/campaigns` mock returned only `active`, omitting the authorized `campaigns` list required by `selectedCampaign`. The production script correctly cleared the panel and disabled saving; it never rendered the two expected users. Supply the campaign list and retain the exact two-user PUT assertion, adding heading, existing-check and save-enabled assertions. No timeout increase or production selection fallback is introduced.
- Two lifespan tests: viewer installation intentionally composes viewer and ownership initializers. The fixtures doubled only viewers, so the real ownership initializer accessed missing `context.STORAGE`. Double both persistence services while retaining real FastAPI lifespan composition in the repository tests. Assert deferred initialization, one call to each initializer, existing lifespan/state preservation, and absence of both management endpoint families on the Client app. Do not remove either production initializer.
- ACL: the fixture initialized grants but omitted ownership, so the regular-admin query failed on `campaign_owners`. Its shared admin/superadmin expectation was also obsolete: regular admins see owned campaigns; superadmins see all. Initialize ownership after users/campaigns exist, and separately test owned, unassigned, other-admin, zero-owned and reassigned cases plus superadmin access to unassigned campaigns. Existing client grant/privacy tests remain unchanged.

Production application code, routes, migrations, authorization and runtime requirements are unchanged. The original broader source split remains unfinished and inactive. README and TODO index were reviewed; neither unrelated feature-task status changes.

## Source identity and local checks

All three reconstructed original test modules matched retrieved Git blobs:

- Browser: `f6b576b70f33877f45a982c5d6533026dbcab6d2`.
- Lifespan: `529faf423f28e43a357cacf042a8c47b6d80cdd4`.
- ACL: `e827c5b50fba63d6022ed8bdcd02f28d06839617`.

On Python 3.12.8, all candidate modules compiled. AST comparison confirmed unrelated browser and ACL code remained unchanged outside the declared methods/import/fixture changes.

The production Admin script matched blob `cb916beacdd9fa2782bfc13982cbc24d07625d44`. A Node VM with DOM doubles reproduced the original missing-list behavior, passed corrected two-user rendering/save checks and preserved deny-by-default behavior with an empty campaign list. This was not a Playwright/Chromium run.

Focused real-SQLite checks using copied inspected ownership initialization/reassignment and viewer choice methods reproduced the missing table and passed the scoped cases. Both exact new ACL test methods passed in that harness. This was not the complete application storage/context or full ACL module.

Viewer and ownership route sources matched blobs `8c4482f71d39f9b99e2ab85b722ece1092c61132` and `5c307b61b0d2799f2b78cb39bb45ab47817d798b`. Copied installers with router/lock doubles reproduced missing STORAGE for both Admin and Client lifecycle paths. Doubling both initializer services passed focused checks for one initialization each, preserved existing state/cleanup and no Client management routes. These were not real FastAPI/Starlette integration runs. No local harness or substitute files are committed.

## Outstanding verification

Current local FastAPI, Starlette and Chromium are unavailable; Playwright is importable but that does not provide a browser binary. Full test modules, real framework/browser behavior, Python 3.14 and full CI remain unverified for this repair. Inspect normal push-triggered CI after approved delivery, including that lifecycle tests run rather than skip. No skip marker or extra workflow dispatch is requested.

The accounts migration repair already passed all 13 account tests in run 41318275558, and both pytest regression modules passed all 43 cases. This does not establish a passing full suite. JavaScript and standalone browser/audit failures remain separate; see [open validation](030-validation-and-next-steps.md).

## Client request forwarding correction - 2026-11-16

This is a production wrapper correction, not a fixture-only change to the
historical repairs above. Working branch: features/perplexity-statblock; inspected
HEAD 355598a1a571095b7f2bde58637a1fe2249bfd05 publishes Branch tests
43846424270 attempt 1 for 812de5ae6717f8a7f34892e0031858a0a3e089c6.
The main suite ran 1,896 tests with three failures and fourteen errors. All six
2C.3b native save-handler methods explicitly passed in workflow reader part 130;
that supersedes their delivery-time unexecuted status, not feature acceptance.

Two transport tests reached the serialized client handler without its required
request argument. The wrapper exposed both the handler's Request parameter and
an injected _operation_request; FastAPI supplies one Request dependency per route.
The same pattern is used by production ClientAPI.register_routes, so the failure
must not be dismissed as merely a privacy-fixture problem.

serialized_handler now detects an existing resolved Request annotation (including
subclasses), retains the original signature and passes the handler's actual bound
request to post-lock authentication and ownership checks. Requestless handlers
retain the existing injected parameter, removed before invocation. Keyword and
positional calls, sync/async results and response deepcopy remain supported. No
permission rule, route, schema or transactional-handler body is changed.

Seven new test_serialized_request.py methods cover single-request signatures,
sync/async and keyword/positional forwarding, requestless injection, post-lock
revocation, denied sessions and actual ClientAPI.register_routes ASGI requests
for live/saved campaign selection and revoked grants. Existing transport privacy
assertions are unchanged. Standard unittest discovery and the connection audit
include this filename without a workflow edit.

Preparation: original production source matched blob
738bc574abe40b97f50c0b6beb7a964d2c1a16f5. Production/test AST parsing passed;
transactional_handler remained AST-identical. Eight isolated exact-wrapper checks
passed with Request/ownership doubles, including old duplicate-injection failure
reproduction. The first notebook runner attempt failed because a loop was already
running; executing the unchanged checks in an isolated thread passed. This is a
harness correction, not an application fix. FastAPI is absent locally: the seven
native/ASGI methods, original privacy regressions and full CI remain unexecuted
for this correction. No new production transport or CI pass is claimed.

The user requested one issue per commit, [skip ci] on intermediate corrections
and normal push-triggered CI only on the final corrective commit. This first
correction uses [skip ci]; no workflow edit or manual dispatch. Each push still
needs complete bound approval. Remaining corrections, final-run review and wider
022.03/2C.3c/2D/Stage 3 gates remain in the [lifecycle task](../todo/223-statblock-lifecycle.md#ci-correction-series---2026-11-16).
README, HANDOVER/TODO indexes, scope handover and CI configuration were reviewed;
no unrelated application guidance or index links change. No merge or deployment.

## Service AST harness correction - 2026-11-16

Correction 2 baseline is 4935fddbcdf14fe241ed052f4f81ff63275b4370, the delivered
request-wrapper correction. Only tests/test_bughunt_4eb87b6.py and this handover/
lifecycle tracking change. The extraction namespace now supplies __name__ and
__package__ so reconcile can import the real private pruning helper. No shipped
pruning stub, production service change or assertion removal is introduced.

The original nineteen tests, including all seven effect-reconciliation assertions,
are retained unchanged. Two new methods check module/package identity and pruning
of removed private bindings while preserving survivors, source-map independence
and repeated-reconciliation stability. The latter uses a trusted carrier with
synthetic metadata to test pruning only, not model/graph validity or persistence.

Preparation matched original test blob aa97ebec4059d140648a3b2f2e4983a52b8ae78f;
inspected service blob is 58bbec24fb02534e8c80246c03fc3910f9b8e653. Syntax/AST
checks passed, with original method bodies unchanged. An isolated reconstruction
used eight selected inspected service method bodies, extracted PrivateEncounterState
and prune_private bodies, real SQLite checkpoint names and the existing collaborator
doubles. Original: nineteen tests, exactly seven missing-__name__ errors. Corrected:
twenty-one tests passed. Disabling pruning made the new pruning test fail as intended.
This did not execute full native package imports, full production storage, ASGI,
server startup or CI. Native-module and covering-suite validation remain pending.
No temporary reconstruction files or module doubles are included in the commit.

This intermediate correction uses [skip ci], without workflow changes or dispatch.
Correction 3's snapshot harness and corrections 4-9 remain separate. README and
index guidance are unchanged; [current status and remaining gates](../todo/223-statblock-lifecycle.md#ci-correction-series---2026-11-16).

## Snapshot AST harness correction - 2026-11-16

Correction 3 baseline is 293376ea594eadb8077f97c1b076f7b36b3d1cd1, the delivered
service-harness correction. The snapshot extraction in test_bughunt_711881a.py
now supplies module/package globals. The fixture also supplies a real SQLite
connection context manager as its transaction factory, committing seed data first
so a rejected load cannot roll back fixture initialization. No production code,
WebSocket test body, original assertion or generated boundary case is changed.

Three added methods cover extraction identity, fixture rollback retaining the
seeded row and invalid loads preserving SQL rows without calling read_capture.
The decoder is mocked only for the explicit invalid-ID non-call assertion; no
read_capture replacement is added to the shared fixture or production code.
This remains a minimal snapshot-ID fixture, not native storage transaction coverage.

Preparation matched original test blob de024a946ec4afbe4dedebc6b4e08a2fa88dfde9;
inspected feature-storage blob is 981c10c866218b14dc332edda737800a2162e668.
Initial reconstruction hash mismatches were corrected before validation. Syntax/
AST checks passed; original test method bodies and the WebSocket class are unchanged.
Using four inspected FeatureStorage method bodies and an unused decoder double,
the original sixteen snapshot tests reproduced two missing-module-context errors;
package context alone exposed two missing-transaction errors. The corrected nineteen
snapshot checks passed with zero decoder calls. Removing the row guard made the
new invalid-load check error, demonstrating the retained boundary assertions.
These are isolated reconstructions, not full native imports, recovery decoding,
production graph/transaction integration, WebSocket execution, server startup or CI.
Native module and final covering-suite validation remain pending.

Only the snapshot harness and existing handover/TODO tracking change here. This
intermediate push uses [skip ci], without workflow edits or separate dispatch.
Corrections 4-9 remain separate; README and root index links remain applicable.
[Current status and wider gates](../todo/223-statblock-lifecycle.md#ci-correction-series---2026-11-16).

## Revision-test digest mutation correction - 2026-11-16

Correction 4 baseline is d68cccc128c8444d7fd6b917d7970820e857a17f, the delivered
snapshot-harness correction. The revision rebuild test now removes the old
content_digest before changing source_label. All four original no-op/revision/
counter assertions remain, with added checks for the saved label and changed digest.
A new native regression submits changed content with its stale digest plus a
tracker HP edit, expecting digest_mismatch and unchanged SQL dump, counter/header
revision, persisted HP and transaction state. No production validator or save path
is changed; malformed supplied digests still must fail closed.

Inspected test blob: 577f15bf1278701adec5b27cd723d9020526da52; model:
4b51b2acf162f30b48de107905a78ba395554d2b; adapter:
8a5bc1c2389f22aa50ecdf8ac7795136c4526be4. Both changed test methods AST-parse
and compile; all four original assertions remain in their ASTs. Four isolated
checks of the inspected canonicalization body and SHA-256 calculation passed:
old mutation retains a mismatching digest, removing it permits a fresh different
digest, revision/time-only changes preserve content digest, and canonicalization
leaves its input unchanged. These checks did not execute production validation,
SQLite writes, rebuilds, atomic rejection or the complete native module. The
changed native method, added rejection regression and covering CI remain pending.

Only the revision test and existing handover/TODO tracking change. This intermediate
push uses [skip ci], with no workflow edit or separate dispatch. Corrections 5-9
remain separate, and wider 022.03/Stage 3 acceptance gates remain open.
README, root indexes and runtime/backup guidance remain unchanged and applicable.
[Current status](../todo/223-statblock-lifecycle.md#ci-correction-series---2026-11-16).

## Mocked copy boundary correction - 2026-11-16

Correction 5 baseline is c69db3b112cf675ac9ba0c6c08afcc2fa2b7e904. The effect-
cleanup unit intentionally mocks saving, so it now explicitly calls the production
StorageOperationsMixin.transfer_setup body rather than claiming to complete the
private facade's persisted-destination contract. Both original cleanup assertions
remain, supplemented by exact load/save calls, returned name, input independence
and explicit absence of persistence. No private clone stub is used in that test.

A separate facade regression keeps the mocked save and requires the existing
missing-destination ValueError, zero clone calls, unchanged SQL dump, no destination
and a closed transaction. It preserves the production fail-closed guard rather
than fabricating a destination or suppressing private cloning. Existing native
copy/graph tests remain separate and unchanged. This is not successful native-copy
integration coverage; correction 6's schema fixture is deliberately untouched.

Inspected facade-test blob: fbed4e58412193022b11f9fd75d1b428c0fa4c91; plain
operations: 9f16de18019464def7e5bea811b711f0dfd7ceda; private wrapper:
a6d7b16fa0bebfd550ebc7a02d4aa305f7413f21. Both proposed methods compile/AST-parse,
and both original effect assertions are retained. Two isolated checks passed using
the inspected transfer/identity bodies, real constrained SQLite and simplified
callbacks. The old boundary reproduced the missing-binding error; bypassing the
facade guard made the new regression fail as intended. Native facade/graph/schema
execution, the full module and covering CI remain pending. No production changes,
shared schema-fixture edit, dispatch-pin change, workflow edit or manual dispatch.
This intermediate commit uses [skip ci]; corrections 6-9 remain separate.
README and root index links remain applicable; [current task status](../todo/223-statblock-lifecycle.md#ci-correction-series---2026-11-16).
