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

Use branch `features/perplexity` unless a different target is explicitly requested. When the user asks for a documentation-only push without CI, include `[skip ci]` in the commit message and do not dispatch a separate workflow. Do not automatically skip CI for application or workflow changes.

## Scope of this convention

These are the required maintenance instructions for this handover and future assistant edits. They are a documented convention, not an automated repository enforcement mechanism. No validation workflow or branch-protection rule is added by this documentation change.
