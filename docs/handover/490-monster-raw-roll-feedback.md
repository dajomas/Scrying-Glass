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
