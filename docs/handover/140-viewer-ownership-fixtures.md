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
