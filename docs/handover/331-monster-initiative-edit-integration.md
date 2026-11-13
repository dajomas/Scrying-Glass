# 331. Monster initiative edit API integration

[Foundation handover](330-monster-initiative-foundations.md) |
[Task SG-TODO-018](../todo/180-monster-initiative-bonus.md)

Updated: 2026-11-07. Status: incremental integration; SG-TODO-018 incomplete.
Branch: features/perplexity-018. No merge or write-back authorized.

## Evidence baseline

Run 42352148442 attempt 1 reports success for exact tested commit
4204ccb78cc70dbe5682c856b42ad44964577582. Repository evidence is
ci-results-42352148442-attempt-1 at publication commit
81e1877c17b7de322bde0cb35a350448f36ff8ac. run.json reports all test,
audit and cleanup steps successful. This is workflow metadata verification;
individual test counts and all log assertions were not audited in this increment.
The publication commit is not the tested code commit. The prior edit handler was
committed but not selected by AdminAPI, so that green run alone does not prove
active-route integration.

## This increment

Changes one production import: AdminAPI now selects
InitiativeEditMonstersMixin, which inherits CandidateMonstersMixin. The existing
POST /api/monsters/{ident}/edit registration, admin dependency, same-origin
check and transactional wrapper are unchanged. Candidate creation/lookup,
legacy monster PATCH and character handlers remain inherited unchanged.
No handler arithmetic, storage schema, UI, bundles or workflows change here.
Normal CI applies; no skip marker or separate dispatch.

Seven regression methods cover three static composition/route contracts and
four runtime inheritance/registration contracts. Three static methods passed
locally against the prepared API source, syntax parsing passed, and an AST
comparison verified the only production change is the import. FastAPI is absent
locally, so the four runtime methods have not executed. The registration fixture
uses real FastAPI routing but replaces the transaction wrapper and supplies a
fixture auth dependency to inspect wiring. It does not prove authorization,
transaction rollback, HTTP mutation, production storage or restart behavior.
No new-stage runtime/CI pass is claimed before covering results are reviewed.

## Outstanding

Add the actual Edit dialog bonus control and read-only roster bonus plus raw-roll
and separate-total controls. Complete authenticated HTTP, storage/restart,
active-order/tie/turn/round and keyboard regressions; implement provider identity,
source bonus extraction and reviewed selected-monster refresh. Review later CI
against its exact tested commit. Task completion still requires all agreed
acceptance and user sign-off. Existing task/foundation documents remain historical
stage records; this supplement records the composition stage and its limits.
