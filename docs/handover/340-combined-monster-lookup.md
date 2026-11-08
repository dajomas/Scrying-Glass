# 340 - Combined monster lookup activation

[Back to handover index](../../HANDOVER.md)

2026-11-08. [SG-TODO-018 correction plan](../todo/185-monster-correction-plan.md).
Branch features/perplexity-018. A.1 remains accepted. A.2 and A.3 have covering
corrective CI and the user's manual test/sign-off on 2026-11-08. Initial stage B
was delivered as 11f104058efb2a56365b0309ce8c6ee829d84c18; its first covering CI
failed and the user requested visual corrections. The colour-only/single-line
status follow-up is included here; corrective CI and manual acceptance remain
pending. No overall SG-TODO-018 close-out, merge or write-back authorized.
Earlier dated preparation/delivery gates below are historical and superseded only
where the later acceptance record explicitly says so.

## Runtime and compatibility

Candidate lookup queries both enabled providers, even when D&D Beyond succeeds.
Configured books are enumerated; missing mappings, malformed data, fetch failures
and limits block all candidates/signing. Unconfigured entry sources are excluded.
Versions keep separate statistics and source-bound selection/bonus offers. Exact
retained Refresh identities are not silently replaced. Keys/defaults stay intact;
fivetools_fallback independently enables 5e.tools candidates while legacy stats/
image fallback behavior is unchanged. No permissions/schema/account changes.

Commit 4 replaces fallback-only Admin help and clarifies config comments without
changing values. Existing overwrite/image labels and both creation/import form
blocks are byte-identical. README no longer advertises an interim wording mismatch.
No Admin JavaScript/bundle/marker or selection/Apply behavior changes in commit 4.
A.3 and stage B were excluded from that delivery.

## Evidence and limits

Activation 5414f1359808fdc07c75b94b1ca3ffe15c078d70 had failed CI 42503436253 attempt 1:
1,391 main/repeated executions with the same two stale locked-page assertions.
That run remains failed. Test correction e2d06aac12dabbdc7d4febe7be1efc3b3a2b2b29 has
verified successful run 42504619218 attempt 1; publication
ce44afba0e12cd4b46125e735e935753ccb41be0 / ci-results-42504619218-attempt-1.
Every listed job/cleanup step succeeded for that exact tested SHA, not commit 4.
Detailed earlier records remain in the
[pre-finalization snapshot](https://github.com/dajomas/Scrying-Glass/blob/ce44afba0e12cd4b46125e735e935753ccb41be0/docs/handover/340-combined-monster-lookup.md).

Two static help/config tests passed in commit-4 preparation. Original template/
help-test/config blobs were verified; both form blocks and all non-comment YAML
lines are unchanged. Both test modules parse/compile and remain below 20,000 bytes.
The full-Admin intercepted-HTTP browser fixture retains 1440/375 widths, labels,
IDs, no-page-error and no-mutation checks; it was not executed locally.
Four new secured ASGI/real-SQLite methods retain production parsing/signing/creation/
Refresh paths with mocked synthetic provider transport, HP generation and pre-
seeded sessions. They cover both chosen sources/reopen, either-provider failure
without signing/mutation, explicit Refresh choice/apply with raw16+7=23 and unchanged
HP/unselected state, retained identity, and disabled providers/empty sources.
These methods were prepared, not executed locally: FastAPI is absent. No framework
stand-in or browser-to-server, password login, TCP, live-provider or OS-restart proof.
Existing CI discovers both modules normally; the later commit-5 run below covers
the branch containing these tests. Manual workflow acceptance was pending then.
Historical data is linked rather than discarded.

## Remaining gate

A.2/A.3 manual acceptance is recorded below. Review covering CI for the stage-B
visual/fixture correction, then obtain desktop/narrow visual/workflow acceptance
before overall reconciliation. Stage-B delivery is not validation or completion.
Merging remains separate.

## Commit 5 initiative overwrite follow-up - 2026-11-08

Prepared before A.3: remove only the Add Monster initiative-bonus confirmation.
Keep the source/version chooser, its cancellation/focus behavior, and Refresh
review/Apply. Available bonuses fill blanks or replace existing values when the
existing AC/HP overwrite checkbox is enabled. Initiative help explains this shared
option without changing template IDs or checkbox labels. Missing/invalid bonuses
never fill or overwrite. Lookup-start value and edit-revision guards preserve edits,
including edit then revert. Bind the exact signed offer after application events;
later edits, reset, changed species/selection or a new lookup clear attribution.
Unsigned copies remain manual. Server authentication/signature checks are unchanged.
The existing AC/HP handler remains responsible for its own assignments.

Preparation validation: Node syntax passed; seven candidate, eleven source-offer
and three typing/focus Chromium methods passed (21 methods, subcases not counted
as separate methods). Tests use intercepted HTTP, opaque offer tokens and copied
production lookup/listener code in isolated fixtures. This is not full Admin/CSS,
browser-to-server, authentication, live-provider, persistence or deployed desktop/
narrow acceptance. Initial preparation exposed fixture issues: modal-inert fields
needed explicit programmatic edit events; the delayed-response test must intercept
fetch rather than the already wrapped request. Corrected fixtures passed; no
production assertion was relaxed to accept overwriting intervening bonus edits.

README was updated. Root HANDOVER/TODO indexes and workflow were reviewed and left
unchanged at commit 5: existing links and overall in-progress status remained
accurate. Normal push CI applied, without skip/workflow changes/dispatch.
Implementation SHA 7c760064aaa3484974362fb423f89245e4eb55fa has verified successful
Branch tests run 42514703672 attempt 1. Evidence was read at publication SHA
8c7ce113ee00548ac3126744dd98a6c25d2a3579 / ci-results-42514703672-attempt-1.
Run/job metadata agrees on the branch, attempt and exact tested SHA; all listed
steps including cleanup succeeded, none skipped. Main suite: 1,398 tests OK;
connection-audit repeat: 1,398 tests OK, 752 connections opened/0 without explicit
close. Repetition is not unique tests. Syntax/import, pytest, JavaScript, standalone
browser/audit and artifact-upload steps succeeded. Inspected error-labelled
tracebacks are negative-path logging followed by passing assertions, not failing
checks. No setup/collection failure is reported; individual test-level skips were
not independently enumerated across the entire log. Historical failures stay failed.
Deployed acceptance gate at that delivery is retained in the [commit-5 record](../todo/185-monster-correction-plan.md#commit-5-initiative-overwrite-follow-up---2026-11-08); the later explicit sign-off is A.2/A.3, not invented broader acceptance.

## A.3 sole-candidate Refresh - 2026-11-08

Implementation delivered as c62d203d3b92aa277eb7e34f4c90da789ab0e58b.
Identity-less Refresh rows resolve exactly one candidate through the existing
signed snapshot validation and exact-source fetch. Multiple candidates retain
explicit choice; zero remain unavailable with an unresolved status. Failed combined
lookup offers no partial candidates. Invalid retained identity is fail-closed, and
a signed choice conflicting with a retained identity is rejected. No provider, book,
edition or candidate substitution is introduced. Invalid/expired/wrong-species or
identity-less tokens cannot resolve a row. An exact-fetch failure remains failed.

Review continuation resolves only explicitly updated row IDs and preserves all
other server-held rows, including automatic and earlier explicit candidates and
proposals. Reload review starts fresh; failed rows require reload to retry lookup.
The unchanged browser retains individual selections across continuation. No fields
are auto-checked; no live statistics/image change or HP generation occurs in review.
Explicit Apply and all existing authorization, scope/revision/state/configuration,
expiry, signed identity, single-use and transactional guards remain. Add Monster
commit-5 code, Admin assets, schema and CI workflows were unchanged by A.3.

Preparation validation: four prepared Python code/test files compiled and parsed.
Framework application and browser tests were not executed locally: FastAPI and
HTTPX2 are absent. Updated source tests and new secured ASGI/SQLite plus intercepted-
Chromium tests are discovered by existing normal CI. They cover sole/multiple/zero,
identity/token safety, unaffected automatic/explicit rows, checkbox choices, no
review mutation, HP only on explicit Apply, storage reopen, replay, malformed IDs,
stale response/configuration/expiry and 1440/375 review behavior. Provider transport/
HP and browser endpoints are mocked as described in fixtures; no live-provider,
password-login, browser-to-server, new-process restart or deployed acceptance claim.
The first covering A.3 run failed as recorded below; the later corrective CI and
manual acceptance record supersedes its pending gate without relabelling failure.
README and correction-plan status were updated together. See the [A.3 record](../todo/185-monster-correction-plan.md#a3-implementation-and-validation---2026-11-08).
Stage B, overall close-out, merging and other-branch writes were excluded from A.3.

## A.3 first covering CI and fixture correction - 2026-11-08

Run 42516636403 attempt 1 failed on exact tested SHA
c62d203d3b92aa277eb7e34f4c90da789ab0e58b, branch features/perplexity-018.
Evidence read at publication 5c8cd561b46a8694fe3da267771927f31ff7b45c /
ci-results-42516636403-attempt-1. Run and job metadata agree. Main suite and
connection-audit repeat each ran 1,406 tests with one error: the same assembled
Chromium method test_real_candidate_resolution_keeps_other_checks_and_unchecked_hp
timed out waiting for Source candidate for Alpha. Two executions are not two
independent defects. The fixture supplied one candidate, so A.3 correctly omitted
the redundant chooser. This is a stale browser expectation, not setup/collection
failure or evidence of a production auto-resolution defect. The five new A.3
ASGI/isolated-browser methods explicitly report OK. Syntax/server import, pytest,
JavaScript, artifact upload and checkout cleanup succeeded. Node/Python post-setup
cleanup steps were skipped. Connection tracking reports 759 opened/0 without
explicit close, but the audit step remains failed because its repeated suite failed.
Subsequent standalone log/round audits and browser smoke completed; smoke reports
no page errors. No deployed/manual or live-provider acceptance was executed by CI.

Correction changes tests only: give the explicit-choice fixture two distinct
provider URLs/edition flags, assert both candidates and unchecked HP, retain
other-row checkbox and no-review-mutation assertions. Add an assembled Chromium
1440/375 sole-candidate method forwarded through the real secured ASGI/SQLite
review/apply path: no chooser, no automatic checks, no state/persistence mutation
or HP generation during review, one preview request, explicit AC Apply, exact
source identity and unchanged other row/HP. Existing stale/apply/health checks
remain. No production, Add Monster, asset, schema or workflow changes.

Correction preparation: reconstructed original test matches live blob
1b583d9dada1cb3aee7ddc85f1bf196f5d3a3e82; revised 16,382-byte module compiles
and parses. Its five methods were not executed locally: FastAPI/HTTPX2 absent.
Normal CI discovers it; no skip marker/workflow edit/dispatch. Corrective delivery
and covering results remain separate. README and root index links/overall open
status needed no change for that fixture correction. All failed runs stay failed.

## Corrective CI and A.2/A.3 acceptance - 2026-11-08

Correction delivered as 1c289d485bffcf8197fb32238349729e52b822ed. Branch tests
42517614512 attempt 1 succeeded for that exact SHA on features/perplexity-018.
Evidence was read at publication 73183fd70d6111083b2ca0048c6a029c0c04fed8 /
ci-results-42517614512-attempt-1. Run/job metadata agrees; every listed step and
cleanup succeeded, no skipped workflow steps or reported setup/collection failures.
Main suite: 1,407 tests OK; connection-audit repeat: 1,407 tests OK, 761 connections
opened/0 without explicit close. Repetition is not unique tests. The repaired
multiple-candidate method and new assembled sole-candidate method explicitly
report OK, along with stale/apply/health-conflict checks. Other syntax/import,
pytest, JavaScript, standalone checks and artifact upload succeeded.

The user stated: manually tested A2 and A3 and signs off on them (2026-11-08).
A.2 and A.3 are accepted; A.1 acceptance remains. This is user acceptance, not an
assistant-executed deployed/live-provider audit or overall SG-TODO-018 close-out.

## Stage B roster presentation - 2026-11-08

Initial implementation delivered as 11f104058efb2a56365b0309ce8c6ee829d84c18. The
following initial behavior/preparation record is retained; the later follow-up
supersedes its wrapping and visual-marker choices.
The existing loaded roster enhancement removes visible Roll label text and the
(legacy) suffix, preserving the input's raw-roll accessible label and separate
Total output. Retained totals still have no invented raw roll; a tooltip explains
them. The lower-level raw renderer/calculations remain unchanged. Subtree
observation catches late decorators as well as replacements, with idempotent
child writes to avoid an observer feedback loop. Character initiative labels remain
combatant-specific; monster raw-roll labels are no longer overwritten by the
generic roster label. No values, origins, calculation/order or Tab rules change.

Initial roster status mapped standing to alive for display only, including the
character life-state button. Down/stable/dead and stored identifiers/rules remain
unchanged. Initial status phrases used individual nonbreaking spans inside a
wrapping status group. The explicit single-line action group retained table-local
scrolling and button order/focus exposure. Blanket action-cell nowrap was removed;
names/species and individual button captions remained intentionally unwrapped.

AC/HP/Init have fixed captions and server-derived on classes/aria-pressed. Join
Battle/Ally/Visible share pressed semantics and scoped active styling. The initial
minus/check markers are now superseded by the user's colour-only request below;
aria-labels keep accessible button names stable. The old document delegate infers
fixed-stat state from the visible on suffix, so the roster-local fixed-stat handler
stops that delegate and uses the same patch helper once with boolean state. It
does not optimistically change state. Existing PATCH URLs, payload keys,
authentication, server validation, error notices and reload behavior remain.
Other button handlers are untouched.

Initial preparation: Node syntax passed for the roster draft. Isolated Chromium
at 375/768/1440 passed three replacements per width and 18 keyboard toggle
activations overall: one helper call each, zero old-delegate calls, no page errors.
This fixture used copied production enhancement code with a stub patch helper/
minimal markup, not full Admin, HTTP/SQLite or deployed acceptance. The existing
layout test's original blob 731b81475012ffcb61cf252d505dc0cdfbe50249 was verified;
only its three fixed-caption expectations changed. Updated layout and new full-
Admin regression modules compiled/parsed. Full-Admin tests were prepared not
executed locally (FastAPI absent). Initial intercepted-HTTP tests covered long
names, three widths, replacements, raw labels/retained totals, life mapping,
read-only rendering and fixed toggles; they checked individual status phrases,
not the complete status line, so missed the screenshot's short-name wrap defect.
Existing geometry, all-button keyboard/local scrolling, Edit/statistics and
removed-control checks remain. Normal CI discovers them; no workflow changes.

Its first covering CI failed as recorded below. Corrective CI and user stage-B
visual/workflow acceptance remain pending. No schema, Python/server, core bundle
identity, creation or Refresh change. README/User Guide and roster handover 310
were reviewed; their existing workflows/single-line controls remain accurate.
Root index links/overall open status remain accurate for this corrective increment.
No overall task close-out, merge or other-branch write.

## Stage B CI failure and colour-only/single-line follow-up - 2026-11-08

Run 42520146312 attempt 1 failed for exact tested SHA
11f104058efb2a56365b0309ce8c6ee829d84c18 on features/perplexity-018. Evidence read
at publication cdccf96fb0e0abd23d82783c0d38c43c3e0ff921 /
ci-results-42520146312-attempt-1. Run/job metadata agrees. Main and connection-
audit repeat each ran 1,409 tests with one error in the same method
test_fixed_toggles_use_state_not_labels_and_rejection_keeps_state. It waited for
visible fixture rejected text already emitted into monsterAddNotification inside
the collapsed monsterInputPane. This is a runtime fixture-visibility timeout, not
a setup/collection error or two independent defects. Post-wait state assertions
were not reached. Syntax/server import, pytest, JavaScript, artifact upload and
checkout cleanup succeeded; Node/Python post-setup cleanup was skipped. Tracking
reports 762 opened/0 without explicit close, but the audit step remains failed
because its repeated suite failed. Later log/round audits and browser smoke
completed; smoke reports no page errors. This failed run stays failed.

The user rejected the minus/check visual decorations and supplied a screenshot
showing alive wrapping. The request explicitly supersedes the prior non-colour
visual-marker requirement: colours only for active/inactive controls in both
rosters, retaining aria-pressed, fixed accessible names, titles and keyboard
behavior. Status must be one line and may continue beneath AC/HP.

Correction changes production CSS only. Remove both button pseudo-element marker
rules; keep pressed-state colours. Reserve a lower lane using bottom padding in
each main roster data cell. Position the name-cell status in that lane with
nonwrapping flex/max-content width so it can extend beneath adjacent columns
without widening the name cell or covering their values/controls. It remains
inside the roster scroll region, ignores pointer events and stays within the row.
Status separator dots are retained; no dash/check decorations remain. JavaScript,
PATCH behavior, data/statistics/life states, Add Monster and Refresh are unchanged.

The full-Admin fixture opens Battle setup/Monster input using normal toggle UI
before rejection, retaining its visible-error and unchanged-state assertions. The
production pane-specific notification location is unchanged and may be hidden
when that input pane is closed; no broader notification UX change is claimed.
Tests now measure complete-line height, equal phrase baselines, extension past
the short name cell and separation from other cell content; add the Poddy/noble
prodigy case at 375/768/1440 over three replacements. Assert absence of glyphs and
different on/off colours while retaining exact PATCH count/payload/state checks.

Preparation: reconstructed original test matches live blob
6e22b1225f9fa197765bae3c271acdd585338e9c. Revised three-method module compiles/
parses; all 15 embedded JavaScript expressions pass Node syntax checking. Local
isolated Chromium with synthetic two-row tables passed both rosters at three
widths/three replacements: one line extending past the name cell, no adjacent-
content overlap, no glyphs, no viewport widening and no page errors. This is
component CSS geometry, not assembled Admin/server/deployed acceptance. Full-Admin
methods were not executed locally because FastAPI is absent; existing normal CI
discovers them. No skip marker, workflow edit or separate dispatch. Correction
delivery and covering validation remain separate; no new SHA/run invented.
Manual visual acceptance and overall close-out remain outstanding.
