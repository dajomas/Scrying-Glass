# 490 - Stage 2 monster raw-roll feedback

[Back to handover index](../../HANDOVER.md)

## Step 1 implementation checkpoint - 2026-11-11

Effective monster-row raw-roll changes use explicit encounter-scoped controller
identities: monster.raw-roll.validation, .request and .refresh, each targeted by
monster ID. Errors persist; matching recovery preserves unrelated notices. The
per-target pending guard spans mutation and refresh, including replaced inputs.
Obsolete mutation completions do not initiate refresh; obsolete refresh results
do not publish or resolve feedback. Already-sent server requests are not undone.

Blank/null, signed safe whole numbers, encoded IDs and raw-only PATCH transport
remain unchanged; the server still adds the bonus once. Saved mutation/failed
refresh has a distinct persistent reload instruction. No success notice or
automatic mutation replay is added. Character initiative, accepted Join reporting,
combat/authorization, monster Edit and roll-all behavior are unchanged.

The retained native-browser fixture installs the production feedback dependencies
and waits for refresh as well as transport. Only the raw-roll asset reference and
its composition assertion advance to v=2. No Admin fragment, bundle pin, failure
marker, other asset reference or workflow changes. README was reviewed and remains
accurate; the indexes link this checkpoint and its task record.

Preparation: revised handler and Node suite syntax checks passed; 16 focused Node
cases passed with zero failures/cancellations/skips using the production controller
(Git blob c4a82d73b21f4657da651ce45f76003c3348a6ef verified locally), controlled
DOM/transport and deterministic timers. The revised browser fixture compiles.
These checks are not full Admin/bootstrap, native-browser handler, live-server,
human visual, screen-reader or exhaustive accessibility acceptance. Native-browser
handler execution, full suite, covering CI and acceptance remain pending. Existing
CI discovers the .cjs and test_*.py files; this mixed commit uses normal CI, without
a skip marker, workflow edit or separate dispatch. No commit/run outcome is invented.

[Task status and remaining gates](../todo/099-monster-raw-roll-feedback.md). Stage 2,
Stage 1, both feedback deliverables and 009.7 remain open. Monster Edit, roll-all,
select-dead, bulk Join pane success and compatibility retirement are not included.
No phase close-out, merge or deployment.

## Step 1 local covering evidence - 2026-11-11

Implementation 162a3892ef330c62961b05409d07916af7d8b4e6 is covered by the
completed local suite=all run run-20261111T203731Z-cNHOP5, published at
50e3123ccec5d8cae2db727271a0ba8c434f3a52 under
local-tests-162a389/run-20261111T203731Z-cNHOP5. Environment identifies a detached
clone, Python 3.14.7, Node v22.23.2, completed=1 and overall exit code 0.
All 74 listed commands report exit 0: syntax/import, unittest, selected pytest,
63 JavaScript files and seven standalone scripts. The raw-roll script-37 log
individually confirms 16 passes, no failures/cancellations/skips. The unittest
log retrieval was truncated; its visible portion confirms core assembly/pins,
loading/rendering and complete-Admin composition passes, not an exhaustive direct
review of its tail or every browser result. Summary-level success covers the
local CI-command suite; this is not a GitHub Actions run outcome or live-server,
manual visual, screen-reader or exhaustive accessibility acceptance.
The user's conditional request to continue Step 2 is satisfied by this green run;
no whole-stage or phase close-out is inferred.

## Related Step 2 monster Edit checkpoint - 2026-11-11

The same monster initiative workflow now has explicit monster.edit.validation,
monster.edit and monster.edit.refresh identities with monster-specific targets.
Persistent matching recovery preserves raw-roll and unrelated notices. Per-target
pending guards span mutation/refresh; exact Edit object and open-sequence guards
suppress old completions, including reopen-then-close during refresh. An old
finally cannot remove a newer attempt's aria-busy state. Controls restore their
prior disabled values. Existing rendering, FormData, trimming, bonus omission,
image handling, encoded POST, character delegation and native validity remain.
No success notice or automatic mutation replay is added; saved/failed-refresh
remains a separate persistent reload error. No server/combat/authorization or
accepted Join changes, roll-all, select-dead or compatibility retirement.

Preparation: Node syntax checks of the revised handler and new production-controller
regression suite passed; revised browser fixture compilation passed. Step 2 Node
runtime, native-browser and full-suite execution remain pending; Step 1 evidence
does not cover Step 2. Existing CI discovery includes both tests. The retained
browser fixture installs production feedback and asserts controller errors rather
than compatibility notices, preserving prior transport/rendering assertions.
The v=1 template reference and complete-Admin inventory remain unchanged: production
cache_bust_html appends a fresh _cb token per HTML render, and the browser source
fixture now verifies token replacement for this asset. Reload the page after
updating. No Admin fragment/pin, template, workflow or unrelated source changes.
README and root indexes retain accurate links/open boundaries and are unchanged.
This mixed commit uses normal CI. Stage 2 and wider deliverables remain open.

## Step 2 composition fixture correction - 2026-11-12

CI run 43100121386 attempt 1 covered implementation
31bb7c459e776f9c20aac27659a0824524359398 and failed its JavaScript step.
The character Edit suite reported 13 passes and two failures: both retained
monster-wrapper composition tests threw ReferenceError: openEdit is not
defined during asset evaluation, before their submission assertions.

The shared VM harness now exposes its existing Edit-opening helper as
openEdit with the production (kind, id) argument order. Production session
guards and existing integration assertions are unchanged.

Corrective runtime and covering CI validation remain pending. This draft
does not establish that all JavaScript failures have been resolved.
Stage 2 and wider deliverables remain open.

## Covering CI reconciled and roll-all preparation - 2026-11-12

Branch tests 43150070549 attempt 1 succeeded for corrective revision
cd1599e7cf485d55ae83f4e622384be70ebe0bcf, published at
49da8bc04b36824005342640902d1c44de679169. Run/job metadata confirms all
configured main stages succeeded, including JavaScript and Python/browser/audit.
This supersedes earlier pending-covering-CI notes for the Edit fixture correction,
not an exhaustive individual-log review or wider acceptance. It does not cover
this later roll-all draft. No old failed run is relabelled.

Bounded roll-all scope: replace only its effective handler in complete 040-source.js.
Keep the bodyless POST /api/monsters/roll-initiative, confirmation and count wording;
server dice/bonus arithmetic, order, permissions and character initiative are unchanged.
Use monster.roll-all.validation/request/refresh with all-monsters target and monster
pane placement. Empty roster is deduplicated information; cancellation performs no
mutation or feedback clearing. Errors persist and matching recovery leaves raw-roll,
Edit, Join and independent targets untouched. Confirmed success appears before strict
load(true), expires after 3s, and does not misreport a refresh failure as a failed roll.
A separate persistent refresh error instructs reload, not another roll or automatic
mutation replay. Encounter/supersession guards suppress obsolete results/refreshes.
One pending owner disables the roll-all button through mutation and refresh, including
scope changes until that attempt settles; prior disabled state is restored. Other
handlers and controls are not locked. Already-sent mutations are not cancelled.

Preparation executed: complete-fragment syntax, test syntax, 15 Node regressions
with zero failures/cancellations/skips, four detected negative controls and restored
15/15 run; pin-file Python compilation and exact reverse-replacement checks passed.
The complete original 040 matches Git blob 5030c15e60e41b194ff841b3ea96c5f49a0b6496;
controller matches c4a82d73b21f4657da651ce45f76003c3348a6ef. Tests execute complete
040 with the production controller, controlled DOM/transport, deterministic timers
and a scoped adapter, not full Admin bootstrap/view, native browser or live server.
Negative controls remove duplicate/relevance protection, strict refresh propagation
or operation isolation separately and each makes the suite fail.

040 is 19,070 UTF-8 bytes, SHA-256
f72e71725b2952ed8b0aea6bb5f0da0fa4abc0b570013161a4beae1caf6a1ea1.
Only its expected digest and calculated bundle size 126,506 change in the pin fixture;
all other pins and guard logic remain. Surrounding 040 bytes are unchanged. Actual
eight-fragment assembly/reader/tamper/runtime and full-suite/browser validation remain
pending combined validation; calculated total is not a locally assembled-bundle identity.
No new asset, template/cache reference, failure-marker or workflow change is needed.
README, indexes and established links remain applicable and unchanged. Existing CI
discovers the new .cjs. At the user's 2026-11-12 request, this and the remaining
intermediate Stage 2 commits use [skip ci] until all Stage 2 changes and updates are
pushed. No workflow is changed or separately dispatched. Combined covering validation
remains pending until a final run is arranged; the marker alone is not a verified
workflow-run outcome.

Select-dead, bulk Join pane success, final Stage 2 reconciliation/acceptance and
all work outside this bounded handler remain separate. No phase close-out or merge.
[Task status](../todo/099-monster-raw-roll-feedback.md#roll-all---2026-11-12).
