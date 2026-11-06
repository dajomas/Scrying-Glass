# 330. Monster initiative and refresh foundations

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-018](../todo/180-monster-initiative-bonus.md).
Status: foundation delivered; reset/setup-import integration increment prepared
for delivery with full validation pending. Other runtime integration remains
outstanding. All 018 writes target features/perplexity-018 until user sign-off;
no merge or write-back to features/perplexity is authorized.

## Foundation scope and decisions

Foundation commit: 539697fabdde7e564b198104739870760032d638.
It added two pure Python modules for monster initiative/source-refresh planning,
a standalone JavaScript selection controller and regression tests. At that commit
the modules were not wired into runtime paths. That historical foundation-only
status is superseded only for reset/setup import by the increment below; there
is still no usable complete SG-TODO-018 feature or changed character initiative.

Initiative retains the existing total plus separate raw roll, signed bonus and
origin scalars. Legacy totals survive bonus edits without an invented raw roll.
The refresh planner captures selected snapshots and prepares replacement candidates
without modifying live state. It validates selections before generating HP and
uses one value when HP and Max HP are both selected. The selection controller
implements individual/row/column selection and partial states; DOM, keyboard and
accessibility wiring remain outstanding.

## Historical foundation preparation evidence

Exact prepared repository-path copies passed 22 Python and 10 Node helper tests
in an isolated temporary checkout before the foundation push. Code/test files
were below 20,000 bytes. Those checks were controlled helper/JSON fixtures, not
SQLite, provider, HTTP, browser or end-to-end verification. They were not rerun
for this reset increment. The foundation used the user's one-off [skip ci] request;
no full suite or observed CI result is claimed for that push.

## Reset/setup-import integration - 2026-11-06

The existing reset functions restored original_initiative but retained the current
initiative_roll. Later normalization could reconstruct the pre-reset initiative
from that stale roll. reset_initiative_patch now restores the original total,
clears the current raw roll and retains the assigned bonus/origin. Original totals
remain legacy, not invented historical raw rolls. Records without the new fields
retain their legacy representation. Invalid monster original totals are rejected
before reset_entity changes live flags. Character reset semantics are unchanged.

reset_entity and reset_imported_monster call the helper. Imported monsters still
receive new IDs, retain source HP/Max HP and deep-copy their source. setup_snapshot
remains unchanged and preserves the current initiative relationship; importing
from a snapshot retains the existing reset-on-import semantics. No new original
raw-roll field, provider capability or schema migration is added.

## Executed reset/persistence preparation checks

Prepared tests: tests/test_monster_initiative_reset_storage.py, 16 methods:
10 reset/setup/character cases and six native SQLite entity-record cases.
They passed twice in an isolated temporary checkout. Against the original reset
implementation, the same suite reported eight failures, including three invalid-
input subtest failures; restoring the prepared reset code yielded 16 passes.

The SQLite fixture uses a real temporary file and a minimal entity/attribute
schema. Locally it exercised copies of the repository's entity-record methods;
the committed test imports StorageRecordsMixin normally. No storage implementation
changes are proposed. Round-trip/reopen/reset tests cover signed bonuses, explicit
and default zero, null roll, legacy totals and illustrative source identity
scalars. This is not verification of the complete SQLiteStorage facade, production
schema/constraints, migrations, effects storage or application transactions.
The scalar tests support the existing extra-attribute mechanism, not a claim that
all persistence acceptance criteria are complete. Source identity samples are
fixture values, not an implemented provider contract.

No full application suite, authenticated routes, state normalization, provider,
ordering or browser checks were run for this increment. Normal CI should discover
the new test module. The proposed runtime files are 2,697 and 3,524 bytes; the new
test is 8,672 bytes, below the file limit and existing-file growth allowance.

## Required continuation

Integrate validated source identity/provider extraction, creation/.monster import,
Edit and rolling, state normalization and full storage/setup routes, active-battle
ordering and the review UI. The refresh caller must authenticate or retain review
data server-side, bind campaign/encounter generation and lifetime, prevent stale/
replayed apply, and execute atomic updates with normal health/statistics/order
reconciliation. The planner is not a security boundary or complete transaction.
Its scalar validation does not replace route/storage range checks. Sanitize
controller offers and disable invalid/missing fields before rendering.

## Delivery policy and reviewed documentation

This reset increment uses normal push-triggered CI with no skip marker, workflow
change or separate dispatch. The earlier skip applied only to the foundation.
Workflow branch-filter commit: 3baf032c1e16a8b05befc2847f4e2dca98ffb049.
No workflow state, passing CI or completion is claimed before results are reviewed.
The user will provide result locations for the CI-feedback cycle.

README, TODO.md and HANDOVER.md identities were verified against prior complete
reads. README has no new user-facing workflow to document; indexes and in-progress
task identity remain valid without edits. The task detail and this existing
handover section record partial integration and validation limitations. No new
section, link or application feature completion is claimed.
