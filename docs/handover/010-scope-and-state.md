# 010 - Scope and current state

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-16. Dated sections retain their historical scope. Complete
pre-2C.3b statblock records are linked below; no prior validation is promoted.

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
requested cancellation. [SG-TODO-004](../history/040-dndbeyond-account-access.md) is
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

022.02 model/storage/startup remains accepted and closed: activation
28d75d08febf5b595afe8145b4097410eb987986, reviewed Branch tests 43713643326
attempt 1 and the user's 2026-11-15 13:48 CET sign-off.
[Accepted record](../history/222-statblock-persistence.md). The approved display,
model, ownership, limits and backup contracts remain binding. Historical model-only
schema-8/unwired wording is superseded, not a reason to reopen accepted 022.02.

[Complete pre-2C.3b scope, commits, failures and evidence](https://github.com/dajomas/Scrying-Glass/blob/13cc61b95fa3e62ec9e1f2a6a85ec0dcff981e5d/docs/handover/010-scope-and-state.md)
and [complete pre-2C.3b lifecycle TODO](https://github.com/dajomas/Scrying-Glass/blob/13cc61b95fa3e62ec9e1f2a6a85ec0dcff981e5d/docs/todo/223-statblock-lifecycle.md)
retain every dated delivery, test count, limitation and unfinished requirement.
The headings below preserve existing anchors while current contracts/gates are
summarized in the [lifecycle task](../history/223-statblock-lifecycle.md). Consolidation
promotes no result and removes no requirement. Prior intermediate [skip ci]/final-
Stage-3-only validation descriptions are historical for the current CI-enabled
2C.3b delivery; final covering validation remains mandatory.

## Activation preparation B - 2026-11-15

Historical a44727ef76f810ab593305033947c84eb9af26ae: lair-v5/feature-v4 fixtures,
backup/account/FK checks, no local production pass. The full record is archived
above; later accepted activation supersedes pending status, not evidence limits.

## Activation preparation C - 2026-11-15

Historical 1ccd5c36afb88a99b812b79bacd5a63c7c194654: attack-v7 fixtures and three
isolated resource-lifetime passes, not full startup/CI. Full evidence is archived;
later accepted activation supersedes pending status, not its recorded limits.

## 022.03 counter-only row rebuilds - 2026-11-15

da7654059808795880361ae643e6b5523ffc5c0f corrected CHECK-incompatible counter
encoding without weakening accepted schema/CI. Eleven isolated constrained-SQLite
methods passed; eleven production writer methods remained unexecuted. The eight
earlier incomplete-fixture passes were not production proof. Durable hidden marker/
filter/rebinding/corruption contracts and detailed failures remain in the archive.

## 022.03 trusted clearing - 2026-11-15

Recovery-only scope/highest-revision bindings, durable tombstones, overflow preflight
and atomic clearing/replacement were supplied. Ordinary omission has no clearing
authority. Six isolated SQL passes were not graph/service validation; twelve kernel
and nine service methods remained unexecuted. Authorization, confirmation, roster/
runtime/history and rollback gates remain; see the archive and current task.

## 022.03 save-decision detection - 2026-11-15

Private-aware post-reconciliation save detection preserves character/setup/runtime
save order. Six isolated mock routing passes were not production persistence.
Timeout causes remained unconfirmed; notebook harness corrections were not app fixes.
Full import/integration validation remains pending in the linked lifecycle record.

## 022.03 private save and refresh - 2026-11-15

Protected private flush follows tracker saves and precedes history/revisions, with
exact native bindings and post-success live metadata refresh. Non-native behavior,
caller authority and separate trusted clearing remain. Six prepared native methods
were unexecuted; mutation producers were corrected in 2B.9 without relaxing digests.

## 022.03 lifecycle integration - 2026-11-15

2B.9 coalesces final private-signature notifications, emits after history/revisions
and commit, suppresses no-op extra notifications and discards rollback requests.
Trusted carry/load retains explicit absence; plain input gains no authority. Eight
new native methods plus six 2B.8 methods remained unexecuted; older suites remain
separate. Three isolated empty-carrier checks passed without graph/SQLite/services.
No 2B, Stage 1/2 or 022.03 acceptance was inferred. Retain all historical restart,
undo, limits, scope, exhaustion, privacy and rollback gates in the current task.

## 022.03 clone-kernel foundation - 2026-11-15

2C.1 supplied an internal matching-encounter clone kernel, not transfer/Save As
wiring at that date. Source content/counters remain immutable; destination owners,
revision/time and graph rows are independent, without exporting counter-only history.
Four native methods were prepared/unexecuted; AST parsing did not establish a pass.
Caller authorization and outer tracker-creation atomicity remain required.

## 022.03 stored-setup copy - 2026-11-16

2C.2a added the copy-only storage override around inherited tracker transfer and
private clone, resolving the actual returned name. Naming, roster/effect/reference
rules remain inherited; other modes delegate. Six native methods were unexecuted;
five isolated stub routing checks passed, not native transfer/kernel/schema tests.
Source/input privacy and rollback gates remain; historical no-copy-wiring statements
apply only to their earlier increments.

## 022.03 move-preservation regressions - 2026-11-16

2C.2b supplied four unexecuted native methods for ownership, exact metadata/counters,
canonical references, collision/last-setup isolation, reopen/MAX_REVISION, rollback
and scope/roster rejection. Static inspection found no demonstrated production gap,
not proof that none exists. No production-code change or move acceptance was claimed.

## 022.03 protected-copy regressions - 2026-11-16

2C.2c.1 supplied three unexecuted protected-copy native methods and five isolated
stub handler passes. Actual destination ownership, source/live metadata isolation,
trusted loading, collision naming, late clone rollback and injected campaign denial
were covered by prepared assertions, not executed integration/HTTP evidence.

## 022.03 loaded-move detachment - 2026-11-16

2C.2c.2 wires only loaded moves to fresh runtime ownership before changed(), keeping
the moved setup's owners/content/metadata/counters. The helper requires a protected
outer transaction and active-campaign reference, validates trusted graphs and refuses
shared setup/recovery ownership. Singleton replacement retires only the old exclusive
runtime with owned children; plain input supplies no graphs and serialized private
input rejects. Runtime revisions/time are fresh; counter-only source history is not
exported. Copies/background moves bypass it; non-native clearing stays legacy.
Four native methods were unexecuted; nine minimal-SQLite/stub helper checks passed,
not schema/model/graph/service validation. Missing-import harness corrections were
not production fixes. Broader history/privacy/authorization gates remain.

## 022.03 transfer-boundary regressions - 2026-11-16

2C.2c.3 supplied four native and two selected-route ASGI methods, all unexecuted.
Prepared coverage includes history/revision boundaries, checkpoint preservation,
commit-only notifications, late rollback, missing-source checkpoint rejection and
privacy. ASGI uses actual route/model/AuthService/ownership/SQLite with seeded
sessions, not login/password/full-server/browser/socket validation. Notification
observation uses a deferred-emitter seam. The module AST-parsed; no native/HTTP/
authorization/CI pass or feature acceptance was claimed.

## 022.03 Save As kernel - 2026-11-16

2C.3a supplies native schema-9 save_new_setup: caller-authorized canonical campaign/
name and setup projection, trusted live private content, new destination rejection
for existing names, atomic tracker/private writes, independent ownership/revision 1/
fresh time, immutable source/input and returned saved metadata. Plain input contributes
no graphs; serialized private input rejects. Four native methods were unexecuted;
two files AST-parsed. The kernel-only delivery had no handler wiring; 2C.3b supplies
that integration without promoting earlier evidence. 2C.3c remains combined protected
Save As/copy/move/history/notification/privacy/authorization and acceptance work.

## 022.03 Save As handler integration - 2026-11-16

Baseline: 13cc61b95fa3e62ec9e1f2a6a85ec0dcff981e5d. 2C.3b adds protected
save_setup_with_private and narrow existing AdminSetupsMixin.save_setup wiring.
Authorization and active-campaign checks still precede writes. New native destinations
use 2C.3a. Same-owner saves retain revision/stale guards; other existing destinations
rebase incoming revision/time onto destination-owned counter history, without owner
or ledger resets. Surviving private omission rejects, not clears. Plain state retains
existing destination metadata without importing source authority. Legacy storage
keeps its save path and returns no metadata refresh request.

The handler saves the roster, updates active/last-setup references, then refreshes
live private metadata from the stored destination before changed() and transaction-
end flush. Native calls require the protected outer transaction; existing rollback
restores database and live state after later roster/reference/refresh failures.
No route, permissions, schema, import or ordinary clearing authority changes.

Executed during preparation: ten isolated exact-helper tests using simplified SQLite/
JSON bindings and stub native facade, capture, kernel and private adapter; five
changed-handler routing/order tests with stub helper/context. All fifteen passed.
The first handler-harness run had five missing-asyncio-import errors; correcting
the harness and rerunning produced five passes, not an application fix. These are
not native-schema, actual graph-writer, full-module or protected integration results.
Helper, changed handler method and six-method native regression module AST-parsed.
Six native methods remain unexecuted for new/live and unsaved-runtime Save As,
ordinary/no-op/stale saves, overwrite history/source isolation, omission and rollback
after roster writes/live refresh.

Local checkout/test files and FastAPI were checked and are absent. GitHub exposes
file tools but no test runner/dispatch here. The user's test request selects a
CI-enabled code/test push with no [skip ci], superseding earlier intermediate CI
skip/deferral for this delivery. The existing workflow discovers the new filename;
no workflow edit or separate dispatch is included. A configured/expected run is not
an observed trigger, completion or pass. Review user-published run/log evidence
against the actual pushed commit and attempt; correct failures with fresh approval.
Final Stage 3 covering validation remains required; docs-only commits still skip CI.

[Current contracts, test counts, pending work and acceptance gates](../history/223-statblock-lifecycle.md#2c3b-save-handler-integration---2026-11-16).
Implementation delivery is not acceptance: 2C.3c, earlier execution/corrections,
2D/bundles and Stage 1/2/022.03 remain open. README/root indexes were reviewed and
remain accurate/unchanged. Schema stays 9; deploy matching complete code/data only
after validation/acceptance, keep matching storage/config/media/code backups, and
never roll old code alone over ledger-bearing data. No viewer/provider/listener,
merge/deployment/release or whole-feature closure is implied.

## Documentation entry points

- [README](../../README.md)
- [Deployment](../../DEPLOYMENT.md)
- [Technical documentation index](../Technical-Documentation.md)
- [User guide](../User-Guide.md)
- [Systemd deployment](../Systemd-Deployment.md)
- [Refactor task and acceptance](../history/080-source-size-refactors.md)

Use live branch files as authoritative; older attachments may describe an earlier
architecture or Python requirement.
