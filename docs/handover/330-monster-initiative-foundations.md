# 330. Monster initiative and refresh foundations

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-018](../todo/180-monster-initiative-bonus.md).
Status: foundation-only delivery; runtime integration, overall acceptance and
full validation remain outstanding. All 018 writes target features/perplexity-018
until user sign-off; no merge or write-back to features/perplexity is authorized.

## Scope and decisions

Adds two pure Python modules for monster initiative and source-refresh planning,
a standalone JavaScript selection controller, and their regression tests.
These modules are not wired into routes, state normalization, creation/import,
rolling, persistence, templates or browser assets. Existing runtime behaviour and
character initiative remain unchanged. This is not a usable SG-TODO-018 feature.

Initiative retains the existing total plus separate raw roll, signed bonus and
origin scalars. Legacy totals survive bonus edits without an invented raw roll.
The refresh planner captures selected snapshots and prepares replacement candidates
without modifying live state. It validates selections before generating HP and
uses one generated value when HP and Max HP are both selected. The selection
controller implements individual, row and column selection and partial states;
it does not supply DOM rendering, keyboard events or accessibility wiring.

## Executed preparation checks

Exact prepared repository-path copies previously passed these checks in an
isolated temporary checkout during this task:

- Python unittest discovery of test_monster_initiative_refresh.py: 22 tests, OK.
- node --test tests/monster-refresh-selection.test.cjs: 10 tests, zero failures.
- New code/test files were measured below 20,000 bytes.

These are isolated helper tests, with controlled HP factory fixtures and a JSON
round-trip test. They are not real SQLite, provider, HTTP, authenticated server,
DOM, keyboard or end-to-end verification. No full application suite or CI run was
executed for this stage. Tests use normal discovery names for a later normal CI
run; no further workflow change is needed to discover these helper tests.

## Required continuation

Follow the linked task for agreed behaviour and acceptance. Integrate validated
source identity/provider extraction, creation/import, Edit and rolling, persistence
and setup reset/reuse, ordering and review UI. The caller must authenticate or
retain review data server-side, bind campaign/encounter generation and lifetime,
prevent stale/replayed apply, and execute atomic updates with normal health,
statistics and battle-order reconciliation. The planner alone is not a security
boundary or complete transaction implementation. Its scalar validation does not
replace route/storage range checks. Controller offers must be sanitized before
rendering; invalid/missing provider fields must be disabled by the adapter.

## Requested delivery policy

The user explicitly requested this foundation push with [skip ci], followed by
continuing implementation. No workflow is changed or separately dispatched by
this commit and no skipped/passing workflow state is assumed. The existing branch
filter update is 3baf032c1e16a8b05befc2847f4e2dca98ffb049. This one-off skip does
not change the standing normal-CI policy for later code/test integration. A push
does not complete SG-TODO-018. No foundation commit SHA is invented in advance.
README was verified unchanged and needs no edit for inactive helpers.
