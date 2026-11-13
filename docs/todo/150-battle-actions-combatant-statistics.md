# 150. Battle Actions combatant statistics

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-015
- Status: completed and closed, 2026-11-09, after verified covering CI, explicit user sign-off and the user's request to update/commit the TODO list.
- Recorded: 2026-11-06; implementation and alignment correction delivered on features/perplexity, 2026-11-09.
- Delivery: d8f4f57b26325623fa662388102094cc1cb35fcd includes the final alignment correction and regression coverage.
- Covering CI: Branch tests run 42624239041, attempt 1, completed successfully on that exact SHA and branch.
- Published evidence: ci-results-42624239041-attempt-1 at 1214020a14e9e99b75a9ce8444eb7ce6051b2671.
- Detailed evidence and limits: [360 handover](../handover/360-battle-actions-combatant-statistics.md#close-out---2026-11-09).

## Accepted scope

Show available AC, current HP and HP MAX immediately below each selected Battle Actions target and Reaction source. Ordinary, reaction and statistics-reduction target rows share the enhancement. Missing/null/undefined/non-numeric/non-finite fields are omitted; actual numeric zero is preserved. Cleared selections, removed combatants and entirely unavailable data leave no stale summary.

Read-only summaries retain selector names and description/live-region associations. Selection changes, dynamic rows, same-scope refresh, Apply refresh, reopen and scope changes are handled without changing drafts, selected values, existing Applied locks, eligibility, action serialization or resolution. No backend/API/schema/persistence/provider/initiative change or core fragment/failure-marker edit is part of this task.

The final CSS correction aligns labels, control tops and control heights independently of summary presence or wrapping. Critical hit is centered, Remove sits on the control track, Applied has a separate track and narrow fields stack with their own summaries. Target and Reaction source keep their original controls; no wrapper/control replacement is delivered.

## Acceptance and evidence

The user explicitly signed off on SG-TODO-015 on 2026-11-09 after supplying the covering evidence, then requested TODO close-out with skip CI. Published run.json confirms completed/success for the exact implementation SHA; jobs.json confirms successful syntax/import, Python suite including browser fixtures, pytest, JavaScript, standalone browser/audit and visual-artifact-upload steps. The prior covering-CI and user-acceptance gates are therefore resolved for the agreed task scope.

Preparation syntax/AST and isolated Chromium checks remain historical preparation evidence, not the basis for claiming full live-server coverage. Full-Admin tests use intercepted HTTP/fixtures; neither CI metadata nor user sign-off is described as password-login, live TCP/provider, process-restart or exhaustive accessibility verification. No new tests are run for this documentation-only close-out.

## Sequence and retained history

018 and 009.5 remain closed. Overall SG-TODO-009 remains in progress; 009.6/009.7 remain proposed. Under the [agreed sequence](115-admin-delivery-sequence.md), 009.6 is next; this close-out does not start it or approve its implementation.

The [pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/1214020a14e9e99b75a9ce8444eb7ce6051b2671/docs/todo/150-battle-actions-combatant-statistics.md) retains the detailed preparation history and formerly pending gates. They are superseded by this dated close-out, not silently treated as earlier verified results. No owner or deadline is added. The close-out commit is documentation-only and includes [skip ci].
