# 170 - Manual reductions restart plan

[Back to handover index](../../HANDOVER.md)

Recorded: 2026-11-01. Related task: [SG-TODO-002](../todo/020-monster-damage-effects.md).

## Superseding request — 2026-11-02

The current user request selects attack-window reduction rows for all seven
statistics and a Restore statistics button beside character Reset, built from the
original archive rather than the previous assistant patch. See [180: attack
statistics delivery](180-attack-statistics-delivery.md). Historical scope/delivery
requirements below remain history, not the current implementation status or an
instruction to stack the earlier patch.

## Actual delivery state

The preceding chat created and repeatedly reconstructed temporary drafts for a manual-only first increment. No implementation commit or push succeeded in that chat. Exported files and JSON payloads are not repository delivery and must not be assumed available to another chat. Do not ask the user to upload those drafts: implement from the live working branch and the agreed requirements below.

The preceding chat reported 17 focused Python tests and four mocked DOM/fetch JavaScript tests passing for its local draft. Those are historical draft-only results, not validation of an implementation delivered to this repository. Four repository-context integration tests, the full application suite, authenticated HTTP and real-browser validation were not completed. Do not carry the draft's passing results forward as evidence for new code.

This handover update is documentation only. README and TODO were reviewed; runtime descriptions remain unchanged, and the broader SG-TODO-002 remains proposed and unfinished. No application code, schema, tests or workflow configuration is changed by this handover update. No application tests are claimed for it.

## Agreed first implementation increment

Implement complete, usable manual maximum-HP and Strength reductions. The user selected manual-only scope; do not reopen rules-edition or monster-preset questions for this increment. Internal data structures from the preceding chat were proposals, not existing API contracts or required implementations. Choose structures compatible with the actual application.

Required behavior:

- Preserve base maximum HP and base Strength separately from active reductions and effective values. Do not invent missing Strength; reject a Strength reduction clearly until its base is known.
- Allow reductions to be applied, stacked, inspected and removed individually. Keep full reduction amounts even when effective values reach zero. Validate types, bounds, identifiers and supported schema versions.
- Recompute effective statistics from bases and active effects. A maximum-HP reduction clamps current HP only when above the new maximum. It is not a second damage event, does not consume temporary HP and does not invoke damage-triggered death saves or massive-damage death.
- Increasing a base or removing a reduction must not itself heal or resurrect. Strength zero and maximum-HP zero do not infer monster-specific death rules; resolve special consequences manually while maintaining ordinary life-state consistency.
- Provide explicit base-stat editing and define legacy max-HP editing while reductions exist. Do not silently reinterpret or ignore edits. Reset retains manual reductions and caps its normal HP result; document how monster reset templates interact with base edits.
- Manual recovery only: no rest expiry, turn expiry or concentration-dependent removal for these reductions. Removing a source combatant must not silently recover its target's statistics.
- Add GM controls with preview, base/effective values, active reduction details and manual removal. Preserve draft inputs, cancellation behavior and target/campaign isolation; reject stale applies using existing concurrency mechanisms where suitable.
- Preserve public/private filtering. Private notes, base statistics and mechanical payloads must not leak to players. Public effect names and existing HP-visibility policies remain intentional.
- Use the existing transaction, persistence, audit, undo and reconciliation architecture. Validation or storage failure must leave no partial live-state or database change and must not broadcast an uncommitted result.
- Cover rosters, setups/runtime, reload/restart, snapshots/checkpoints, undo and campaign import/export. Implement a safe normalized persistence migration and backup approach. Reject unsupported mechanical imports rather than silently dropping them; document downgrade limitations.

Explicit exclusions: monster presets, automatic recovery, special zero-stat/death rules, attack/save automation, conditional attack riders, linked attacker healing, healing prohibition, absorption and recurring effects. These belong to later SG-TODO-002 increments.

## Implementation and validation work still required

Read live PERPLEXITY_INSTRUCTIONS.md first, then README, this index and relevant handover sections, TODO and relevant task sections, application documentation, actual implementation and test/workflow configuration. Inspect HP/effect validation, handlers, state normalization, storage/migrations, reset/import paths, campaign bundles, admin UI and filtered player state. Do not substitute old snapshots or temporary drafts.

Build and integrate the feature rather than deliver only a library or design. Add and run focused rules, persistence, rollback, snapshot/undo, import/export and UI tests. Exercise zero/boundary cases, unknown Strength, stale revisions, cancellation, source removal, reset, private visibility and ordinary combat regressions. Run the existing suite where feasible. Separate mocked checks from real browser/server checks and record unavailable validation precisely.

Update relevant README, application documentation, indexed handover and indexed TODO in the same implementation delivery. Keep the broader task open while later increments or required validation remain unfinished; record manual-increment progress separately. Do not invent owners, deadlines, commits or workflow runs.

## Delivery requirements for the next chat

Target only dajomas/Scrying-Glass, branch features/perplexity. Complete creation, integration, validation and GitHub delivery are requested, not another export/reconstruction loop. Establish early whether available tools can submit the complete write through the required exact-content approval mechanism. If a concrete tool limit blocks delivery, explain it before claiming completion or requesting repeated file uploads. Do not silently split an approved atomic write or substitute an archive for GitHub delivery.

Resolve targets, prepare exact file contents and the commit message, request the mandatory bound confirmation, then write only the approved arguments. The user's restart request explicitly asks for [skip ci] on the implementation push as well as this documentation push. Include the token in each corresponding proposed commit message; do not disable CI or dispatch a separate workflow. Skipping CI does not waive local validation or truthful reporting.

After a successful write, report the actual commit SHA, branch, changed files, tests actually executed and remaining limitations. Do not report a workflow as skipped, triggered or passed without observing its state.
