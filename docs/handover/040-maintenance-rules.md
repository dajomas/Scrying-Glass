# 040 - Maintaining this handover

[Back to handover index](../../HANDOVER.md)

## Required structure for every addition

1. Keep root `HANDOVER.md` as a concise index and entry point.
2. Put substantive handover content in Markdown section files under `docs/handover/`.
3. Update an existing section when the topic belongs there. For a new topic, add a file named `NNN-descriptive-topic.md` with a matching numbered heading.
4. Use three-digit numbers in increments of ten where possible. Use available numbers between existing sections for insertions; avoid renaming stable paths unnecessarily.
5. Add or update the relative link in `HANDOVER.md` in the same commit as a new or renamed section. Keep index ordering consistent with section numbers.
6. Include `[Back to handover index](../../HANDOVER.md)` near the top of every section.
7. Keep facts, decisions, pending work and validation evidence distinct. Date material status changes and include commit or run identifiers where available.
8. Do not duplicate detailed application documentation; link to it and explain only handover-specific context.

## Publishing changes

Use branch `features/perplexity` unless a different target is explicitly requested. Every documentation-only commit must always contain `[skip ci]` in the proposed, approved and actual commit message, without needing a separate user skip request. Do not modify workflows or separately dispatch CI for that push. This includes handover, TODO, README/guide and project-instruction changes that contain documentation only. Mixed commits containing application code, scripts, tests, templates, styles, runtime configuration, dependencies or workflows are not documentation-only; run CI normally unless the user explicitly requests otherwise. See [root instructions, section 5](../../PERPLEXITY_INSTRUCTIONS.md#5-ci-execution-and-documentation-only-commits).

## Scope of this convention

These are the required maintenance instructions for this handover and future assistant edits. They are a documented convention, not an automated repository enforcement mechanism. No validation workflow or branch-protection rule is added by this documentation change.

## Workflow clarifications - 2026-11-02

The [root project instructions](../../PERPLEXITY_INSTRUCTIONS.md) now clarify early delivery feasibility, reuse of verified complete reads, proportional documentation, explicitly agreed coherent delivery stages, and preparation versus external-write approval. These clarifications preserve branch restrictions, exact-content confirmation and truthful reporting. The existing CI-first feedback workflow and nonempty-payload safeguard remain in place.

Review relevant documentation rather than touching every document mechanically. Update indexes when their entries change, not merely because section content changes. Every agreed delivery stage still includes its appropriate documentation and TODO status updates.

This is a workflow-documentation update only. README, HANDOVER.md and TODO.md were reviewed and remain unchanged; their application descriptions, index entries and task statuses are unaffected. No application code, tests or CI configuration are changed. No automated tests were executed for this update, and no workflow outcome is claimed. SG-TODO-002 implementation remains undelivered by this change.

## Standing documentation-only CI rule - 2026-11-06

The user explicitly requested that documentation-only commits always contain `[skip ci]`. Section 5 of the root instructions and the active publishing/CI handover guidance now reflect that standing rule, replacing the earlier requirement for a separate skip request each time. This policy update is itself documentation-only and includes the marker in its proposed commit message.

The rule does not classify mixed code/documentation changes as documentation-only, waive external-write approval, change workflow configuration, imply automated commit-message enforcement or establish an observed workflow result. Historical dated delivery notes remain historical; prior commits are not rewritten. README, HANDOVER.md and TODO.md were reviewed and left unchanged because runtime descriptions, index links and task statuses remain accurate. No tests were executed for this documentation-only update; no separate workflow is dispatched.

## Standing implement/push directive - 2026-11-17

At the user's request, [section 8 of the root instructions](../../PERPLEXITY_INSTRUCTIONS.md#standing-implementpush-directive---2026-11-17) now preserves the user's exact standing directive and its operational meaning: carry out implementation without routine proceed questions; ask only for a genuinely new/changed consequential decision; treat a GitHub push request as an instruction to prepare and complete delivery without requiring the user to request the push again. The regular exact-payload yes confirmation remains required, and approval is followed by execution of that exact push, not another proceed prompt. Changed payloads require fresh bound approval.

This is a documentation-only update on features/perplexity-statblock, baseline 3cb3f7568558c88e562725fde6ee1fe8df815579, with [skip ci]. No application/test/workflow changes, new tests, CI dispatch, merge or deployment. Prior verified README/HANDOVER/TODO reads were reused against the unchanged relevant files; their behavior/index/task descriptions are unaffected and remain unchanged. Existing 04b implementation closure and deferred 04 validation obligations are unchanged. This is a documented operating convention, not automatic instruction loading or technical enforcement.
