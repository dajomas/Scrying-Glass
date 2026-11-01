# Perplexity project instructions — Scrying Glass

These instructions define the repository delivery, documentation, validation
and approval conventions for work on Scrying Glass.

Read this file from the live working branch before planning or preparing
repository changes. Treat the live branch as authoritative over uploaded
project snapshots.

These instructions supplement the project instructions field and do not
override platform safety requirements or mandatory approval mechanisms.

## 1. Repository and preferred delivery

- Repository: https://github.com/dajomas/Scrying-Glass.git
- Default working branch: `features/perplexity`

Use this repository and branch unless the user explicitly specifies otherwise.
Do not merge into or write to another branch without explicit approval.

When implementation changes are requested, prefer committing them directly
to the agreed repository and working branch using the required approval
workflow.

Do not create a downloadable archive by default when direct GitHub delivery
is available. If an archive is explicitly requested, provide it in addition
to GitHub delivery unless the user explicitly says "archive only" or
"do not write to GitHub."

If GitHub delivery is blocked, explain the blocker. Do not silently treat an
archive as a successful GitHub commit or push.

## 2. Required preparation and documentation updates

Before preparing repository changes:

- Read the current `README.md`.
- Read the `HANDOVER.md` index and relevant linked sections under
  `docs/handover/`.
- Read the `TODO.md` index and relevant linked sections under `docs/todo/`,
  when TODO tracking exists.
- Read additional implementation or application documentation relevant to
  the requested change.
- Inspect the actual implementation and test configuration rather than
  relying only on documentation or earlier conversation.

If a required documentation file does not exist, state that explicitly.
Do not invent its contents or silently substitute an uploaded snapshot.
Follow section 4 when TODO tracking does not yet exist.

Before committing or pushing:

- Review and update relevant existing documentation, including `README.md`,
  the indexed handover and the indexed TODO documents, so they accurately
  reflect the implementation, remaining work and validation status.
- Preserve existing filename capitalization and documentation structure.
- Include necessary documentation and task-status updates in the same
  proposed commit as the implementation changes.
- Record significant decisions, validation results, known limitations and
  unfinished work in the relevant `docs/handover/` sections.
- Record actionable remaining work, dependencies, blockers and acceptance
  criteria in the relevant `docs/todo/` sections.
- Cross-link related handover and TODO entries rather than duplicating
  detailed content.
- Do not make unrelated or cosmetic documentation changes merely to touch
  a file.
- Never claim tests were executed or passed unless they actually were.

## 3. Indexed handover structure and maintenance

`HANDOVER.md` at the repository root is a concise index and entry point,
not a monolithic handover document.

Keep substantive handover content in numbered Markdown section files under
`docs/handover/`. Read and follow the maintenance rules linked from
`HANDOVER.md`.

For every handover addition or update:

- Update the relevant existing section when the topic belongs there.
- For a new topic, create a file named `NNN-descriptive-topic.md` with a
  matching numbered heading.
- Use three-digit numbers in increments of ten where possible.
- Use available numbers between existing sections for insertions; avoid
  renaming stable paths unnecessarily.
- Add or update the relative link in `HANDOVER.md` in the same commit when
  sections are added, renamed, removed or reordered.
- Keep index ordering consistent with section numbers.
- Include a relative link back to `../../HANDOVER.md` near the top of each
  section.
- Keep facts, decisions, pending work and validation evidence distinct.
- Date material status changes and include commit or workflow-run identifiers
  where available.
- Do not invent a commit SHA or workflow-run identifier before it exists.
- Link to detailed application documentation rather than duplicating it.

Do not expand `HANDOVER.md` into a monolithic document.
Do not modify the index merely to touch it when its links remain unchanged.

Treat this structure as a required maintenance convention for future edits.
Do not claim it is automatically enforced unless an enforcement mechanism
has actually been implemented and verified.

## 4. Indexed TODO structure and maintenance

`TODO.md` at the repository root is a concise index and entry point,
not a monolithic task list.

Keep substantive task content in numbered Markdown section files under
`docs/todo/`, using the same indexed-document approach as `HANDOVER.md`
and `docs/handover/`.

### Initial creation

If `TODO.md` does not yet exist:

- State that explicitly.
- Create the index and initial relevant sections when TODO tracking is first
  requested.
- Do not invent an existing backlog or infer previously agreed commitments.
- Include the new files in the proposed change and obtain approval before
  writing them to GitHub.

A request to document this convention does not, by itself, request creation
of a repository backlog.

### Task additions and updates

For every TODO addition or update:

- Update the relevant existing section when the task belongs there.
- For a new topic, create a file named `NNN-descriptive-topic.md` with a
  matching numbered heading.
- Use three-digit numbers in increments of ten where possible.
- Use available numbers between existing sections for insertions; avoid
  renaming stable paths unnecessarily.
- Add or update the relative link in `TODO.md` in the same commit when
  sections are added, renamed, removed or reordered.
- Keep index ordering consistent with section numbers.
- Include a relative link back to `../../TODO.md` near the top of each section.
- Give each task a stable identifier, a clear description and an explicit
  status, such as `proposed`, `ready`, `in progress`, `blocked` or `completed`.
- Record priority, dependencies, acceptance criteria and validation
  requirements where relevant.
- Distinguish proposed priorities or requirements from those explicitly
  agreed with the user.
- Assign an owner or deadline only when explicitly agreed; do not invent
  commitments.
- Update relevant task statuses in the same commit as implementation and
  documentation changes.
- Mark a task completed only when its acceptance criteria are satisfied.
- If implementation is delivered but required validation remains outstanding,
  record that distinction explicitly.
- Link completed work to the relevant implementation commit or verification
  evidence when available.
- Do not invent a commit SHA before the commit exists.

Do not expand `TODO.md` into a monolithic document.
Do not modify the index merely to touch it when its links remain unchanged.
Do not silently delete unfinished tasks or mark them completed to remove
them from the active backlog.

### Relationship to the handover

Keep the documents complementary:

- TODO documents planned work, task status, dependencies and acceptance
  criteria.
- HANDOVER documents current state, significant decisions, delivered work,
  validation evidence, limitations and continuity information.
- Cross-link related entries rather than duplicating detailed content.

Treat this structure as a required maintenance convention for future edits.
Do not claim it is automatically enforced unless an enforcement mechanism
has actually been implemented and verified.

## 5. CI execution and explicit skip requests

Run CI normally unless the user explicitly requests otherwise.

When a push without CI is requested:

- Include `[skip ci]` in the proposed and approved commit message.
- Do not disable or modify the CI workflow merely to skip that push.
- Do not separately dispatch a workflow for that push.

Do not automatically skip CI merely because a change is documentation-only.
Do not assume a previous skip request applies to subsequent pushes unless
the user explicitly gave it that scope.

Distinguish between:

- A workflow being configured.
- A workflow being triggered.
- A workflow completing.
- Its tests passing.

Report only the states supported by actual evidence. Including `[skip ci]`
in a commit message is not, by itself, verification of the workflow-run state.

Do not claim mocked, static or fixture-based checks provide full live-server
or end-to-end coverage. Describe the validation actually performed and its
limitations.

## 6. Downloadable archive requirements

When a downloadable archive is explicitly requested, include:

- All changed and newly created project files.
- Updated versions of relevant existing documentation files.
- The current `HANDOVER.md` index and all section files under
  `docs/handover/`, so the delivered handover is complete and its internal
  links resolve.
- Relevant handover-section updates describing the delivered changes.
- When TODO tracking has been created, the current `TODO.md` index and all
  section files under `docs/todo/`, so the delivered task documentation is
  complete and its internal links resolve.
- Relevant TODO-section updates reflecting delivered work, outstanding
  validation, blockers and remaining tasks.
- An archive-only `Patch/` folder containing:
  - Documentation of the changes made, including purpose, affected files,
    installation/application instructions, validation results and known
    limitations.
  - A plain-text Git commit message in a file whose name contains
    `COMMIT_MESSAGE`, for example `Patch/COMMIT_MESSAGE.txt`.

Preserve repository-relative paths for project files so they can be applied
to a local checkout. Include complete replacement files rather than only
diffs, unless the user requests otherwise.

Explicitly document file deletions, renames and manual steps in `Patch/`,
because an overlay archive alone cannot apply deletions.

Generate the archive from the same approved changes delivered to GitHub
when both delivery methods are requested. Explain any intentional differences.

## 7. Patch/ is archive-only delivery material

The `Patch/` folder requested in section 6 is not part of the repository:

- Do not add, commit or push this newly generated archive-only folder or
  its contents to GitHub.
- Keep it separate from repository files when preparing a GitHub commit.
- Explain in the archive instructions that `Patch/` is supporting delivery
  material and must be excluded from Git staging.

If a tracked `Patch/` folder already exists in the live repository, do not
delete or modify it merely to enforce this rule. Distinguish existing
repository content from newly generated archive-only material, and flag
any naming conflict before packaging.

## 8. Approval workflow

Before an external write:

- Resolve the exact repository, branch, paths and other targets.
- Prepare the complete proposed content and commit message.
- Request approval using the required confirmation mechanism.
- Make the write only after approval, using exactly the approved targets,
  content and commit message.

If new information requires changing the approved write, request fresh
approval before proceeding.

Include implementation, necessary documentation updates and relevant TODO
status updates in the same proposed commit rather than requesting approval
for an incomplete delivery.

Do not interpret approval for one write as blanket approval for later writes,
merges, workflow dispatches or changes to other branches.

## 9. Completion reporting

For GitHub delivery, report the actual commit SHA, target branch and changed
files only after the write succeeds.

For CI, report observed workflow status and test results only after checking
the relevant run. If the run has not been checked, say so explicitly.

For archive delivery, provide the generated archive and summarize its scope,
how to apply it, and any required manual steps.

If both GitHub and archive delivery are requested, complete the approved
GitHub delivery first, then provide the archive.

Never claim either delivery succeeded before it has.

## 10. Maintaining these instructions

Keep this file at the repository root as `PERPLEXITY_INSTRUCTIONS.md`.

Changes to these instructions must follow the same review and approval
workflow as other repository documentation.

Keep the short project instructions field pointed at this filename on the
agreed working branch. Do not assume this file is loaded automatically:
retrieve and read it before planning or preparing repository changes.

If this file cannot be retrieved, state the problem and do not proceed with
repository writes using assumed or remembered instructions.

These requirements are documented operating conventions. Do not claim
automatic loading or repository enforcement unless it has been implemented
and verified.
