# 110 - Composed campaign router tests

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Diagnosis and scope

Baseline: `96680deb1d84321043a99bde242b85f4ac18e8e9`. Original test Git blob: `a9683c8821246b7011d551b1a982450726c61986`.

A single `install_campaign_viewers` invocation intentionally includes the viewer initializer and calls `install_campaign_ownership`, which adds a different initializer. On the Admin app the ownership component registers its GET/PUT endpoints and the viewer component registers its own GET/PUT endpoints. The observed four routes have distinct path/method keys; the two routers are different lifecycle components, not duplicate viewer registration. AdminAPI installs this composition once in the inspected setup.

The unit fixture expected one lifecycle router and only two routes. Three tests therefore failed after ownership composition was added. This change fixes the fixture, not production routing. It does not add an idempotency guarantee for repeated installer calls.

## Test changes

- Expect two lifecycle components on Admin and Client apps; Client still has no management routes.
- Assert the exact four Admin path/method keys and their uniqueness, not just a higher count.
- Check both management pairs retain authorization and same-origin write dependencies.
- Make the role fixture distinguish admin-or-superadmin viewer access from superadmin-only ownership access.
- Pin APIRouter, Body and Depends doubles in both modules even when modules are cached; manage patches with ExitStack and unittest cleanup.
- Double both initialization services and add checks that each initializes once, ownership startup failure aborts composed startup, and a regular admin cannot execute ownership handlers.

Production code, ownership migration, campaign permissions and request wrappers are unchanged. README and the TODO index were reviewed; no runtime description or SG-TODO-001 status changes are needed.

## Local verification and limits

Original: seven unit tests, three failures. Candidate: ten tests passed on Python 3.12.8. Runs treating ImportWarning, ResourceWarning and DeprecationWarning as errors passed. A cached-module scenario with a deliberately unusable pre-existing APIRouter binding also passed all ten tests; original cached bindings and module entries were restored afterward. The candidate test file compiled.

The focused local tree used hash-verified viewer/ownership route modules and same-origin code, plus copied production lock and handler-wrapper functions. Persistence services were doubles; permitted transaction/ownership data-access paths were not exercised. These are route-composition and authorization-rejection unit checks, not real FastAPI/Starlette, database or end-to-end integration tests.

CI must validate the complete checkout on Python 3.14. The separate real FastAPI lifespan integration test module and other seven Python errors are not repaired or claimed passing here. No full-suite assertion/error count is predicted. Normal CI should run on the approved push; no skip marker or workflow change is included.
