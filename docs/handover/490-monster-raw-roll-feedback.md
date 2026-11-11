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
