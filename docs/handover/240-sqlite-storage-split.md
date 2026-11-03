# 240 - SQLite storage source split

[Back to handover index](../../HANDOVER.md)

Updated 2026-11-03. Task: [SG-TODO-008](../todo/080-source-size-refactors.md).
Corrective preparation base: 2e5d1d4ecedc3e88fa5bd3a565e49fbaa11660fb, features/perplexity.

## Delivery and architecture

The five stages were delivered:
1. Fields: a9da32439b01529ab6deba8242b48593d95be594.
2. Schema/migration: 2a651004a7870de461cce32f5dcffd56b91a2aa6.
3. Records/encounters: 8ed072c3cd3be53474a77cc9267bd7708f0d7638.
4. Operations: 0c8f1c9a95763bf8729d775f4596de68835cabf6.
5. Activation: 266487f8d8b605610db11e837f3f26fcdfc7f7f3.

Stages 1-4 were unused preparations; stage 5 activates native mixins behind the
4,710-byte SQLiteStorage facade. Five lifecycle, three schema, ten record and twenty
operation methods retain their original bodies/signatures/decorators/SQL. Seven
field expressions retain their values/types/order. Reference: original 39,486-byte
blob ea80b59cca80c6885f6ba1ba4d32b759beb187b5. SCHEMA_VERSION=8, transactions,
savepoints, backups, lazy migrations, compatibility exports and callers remain.
STATE_FIELDS is the shared runtime export. Stage-module staging comments are
historical provenance; the facade activates their methods. All five source files
are below 20,000 bytes (records is actually 13,068 bytes, including final whitespace).

## Manual validation and inspected CI

On 2026-11-03 the user reported the Admin click-by-click runbook completed
successfully. This is user-reported manual evidence, not an assistant execution or
a claim about unspecified optional checks. Final task closure still requires CI.

Evidence at ci-results-41602398857-attempt-1, committed in
2e5d1d4ecedc3e88fa5bd3a565e49fbaa11660fb, identifies Branch tests run
41602398857 attempt 1, head 266487f8d8b605610db11e837f3f26fcdfc7f7f3, completed/failure.
Setup/dependencies and syntax/server import passed. Main unittest ran 1,004 tests
with 12 failures, all at Storage reference AST pins before the guarded fixture
bodies. The inspected v1/v2 upgrade tests and new file-backed v8 persistence/reopen
and constructor-cleanup tests passed. Pytest and JavaScript steps report success.
Standalone connection audit reran 1,004 tests with the same 12 failures; it reported
652 connections and zero without explicit close. Log-clear and round-3 audits
reported passes; browser smoke reported no page errors with mocked HTTP/WS and real
Chromium rendering. These are not full authenticated live-server browser checks.

## AST fixture correction prepared

The test oracle used ast.dump formatting to calculate fixed hashes. Python 3.14 CI
omits optional empty lists that the local 3.12 format included. This was reproduced
locally with an available 3.14 interpreter on the verified original source. Both
method and field hashes differed despite unchanged AST semantics. This explains
why the manual run and runtime tests passed while reference guards failed.

Replace only the test helper canonical serializer with explicit recursive AST/list
serialization matching the original format. Preserve optional empty lists, semantic
values and nonempty type parameters; omit location attributes, optional None
defaults and empty type_params as before. METHOD_PIN and FIELD_PIN remain unchanged;
no accepted hashes, production code, schema, workflow or assertions are weakened.

Four new regression methods passed on Python 3.12 and 3.14 (eight test executions):
original 38-method/seven-field pins and reference class with real base SQLite,
independence from ast.dump/line numbers, semantic-value/nonempty-type-parameter
sensitivity, and rejection of deliberately changed SQL/field definitions in copied
fixtures. They used methods reconstructed from the verified original source, not a
full application checkout. Full corrected workflow has not run or passed locally.
Normal CI discovers the new test automatically; no workflow changes or skip.

Historical activation preparation: eleven consolidated fixture tests plus native
dispatch and constructor cleanup passed locally on 3.12, not proof of cross-version
pins. Fixtures use base v3, limited rename tables and mocked effect boundaries;
complete migrations/services/feature coverage belongs to the configured CI suites.

## Deployment and remaining acceptance

Deploy the complete matching python/ tree with facade, all four support modules and
__init__.py, and restart the single process; do not deploy the facade alone. Existing
README deployment/backup instructions remain applicable. No new migration or special
conversion was introduced. This corrective draft changes tests/documentation only.

README, HANDOVER index/maintenance rules and workflow were reviewed or identity-
verified unchanged; paths and runtime commands remain valid. No archive, manifest
refresh, workflow dispatch or CI skip. Keep SG-TODO-008 open until corrected exact-SHA
CI is reviewed and remaining Admin/oversized-source acceptance is addressed.
