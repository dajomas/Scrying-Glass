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

### Early delivery feasibility

Early in an implementation task, inspect the available read, write and
approval tool schemas. Assess whether the intended delivery can be
prepared and submitted through those tools.

Distinguish observed tool failures or documented limits from estimates
and uncertainties. Do not claim a connector limit without evidence.

If a delivery-size or execution constraint is identified, explain its
specific effect and propose a practical delivery plan before preparing
large temporary exports or repeatedly reconstructing drafts.

Unavailable local testing is handled by section 5.1 and is not, by itself,
a GitHub delivery blocker.

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

### Continuation and reuse of verified reads

Retrieve the live PERPLEXITY_INSTRUCTIONS.md before planning or preparing
repository changes.

For other repository files, reuse complete reads already obtained during
the task when their identity is still verified against the working branch.
Record relevant commit or file/blob SHAs where available.

Re-read files that changed, were previously truncated, or become relevant
to new work. Do not repeat the entire preparation sequence merely because
the user says "continue" or because the task spans multiple messages.

Do not assume temporary execution files or variables survive between
messages. If reconstruction is necessary, use the live repository and
complete contents already present in the conversation; do not repeatedly
ask the user to upload assistant-generated drafts.

### Proportional documentation

Review documentation relevant to the change and update statements that
the change makes inaccurate or incomplete.

Do not require edits to every named document when its contents remain
accurate. In the delivery summary, identify relevant documents reviewed
but left unchanged when that distinction matters.

For substantial features, document user-facing behavior, operational or
migration consequences, task status and validation limitations. Prefer
cross-links to duplicated explanations.

For corrective commits, concise updates to the relevant existing
handover/TODO sections are sufficient unless user-facing or technical
documentation also changes.

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

## 5. CI execution and documentation-only commits

Every documentation-only commit must always contain the exact marker
`[skip ci]` in its proposed, approved and actual commit message. This is a
standing user instruction from 2026-11-06; no separate skip request is needed
for each documentation-only commit. It applies to task close-outs, handover,
README/guide and project-instruction updates, including this policy update.

A documentation-only commit changes exclusively human-readable documentation.
A commit containing application code, scripts, tests, templates, styles,
runtime configuration, dependencies or workflow changes is not documentation-only,
even if it also updates documentation or has a docs-prefixed message. Run CI
normally for such non-documentation-only commits unless the user explicitly
requests otherwise.

For documentation-only commits, and for other pushes explicitly requested
without CI:

- Include `[skip ci]` in the proposed, approved and actual commit message.
- Do not disable or modify the CI workflow merely to skip that push.
- Do not separately dispatch a workflow for that push.

Do not assume a one-off skip request applies to subsequent non-documentation-only
pushes unless the user explicitly gave it that scope. The standing
documentation-only rule above does apply to future documentation-only commits.
This is a required authoring convention, not a newly implemented automatic
commit-message enforcement mechanism. Earlier dated delivery notes describe
the policy applicable at those historical deliveries.

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

### 5.1 CI-first validation when local execution is unavailable

The assistant may be unable to execute some or all tests because its
environment lacks a repository checkout, dependencies, network access,
a shell, browser tooling or an application runtime.

Unavailable local test execution is not, by itself, a reason to stop
implementation, withhold an otherwise prepared delivery, or repeatedly
request permission to continue preparing changes.

Unless the user explicitly requires validation before delivery, use the
following CI-feedback workflow:

1. Inspect the live implementation, relevant documentation, test
   configuration and CI workflow.
2. Prepare the implementation, relevant automated tests and necessary
   documentation/TODO updates.
3. Perform the review and checks available in the current environment.
   Do not substitute a syntax check, mock or code review for a test that
   was not executed.
4. Record exactly which checks were executed, their observed results,
   and which checks remain pending.
5. Request the required bound confirmation for the complete, nonempty
   GitHub write payload and commit message.
6. After approval, push exactly the approved changes to the agreed
   branch. Do not wait for unavailable local tests before making this
   approved write.
7. Treat the implementation as delivered with validation pending until
   the relevant CI results have been reviewed.

For this workflow, the user will manually obtain the CI results, commit
the relevant logs, reports or other result artifacts to the repository,
and tell the assistant which commit, paths, workflow run or other
identifiers to inspect.

When the user supplies those locations:

- Retrieve and read the specified results from the repository.
- Establish which implementation commit and workflow attempt they cover.
- Distinguish test failures, collection failures, environment/setup
  failures, skipped checks and checks that were never executed.
- Diagnose failures against the corresponding implementation and tests.
- Prepare necessary fixes and documentation/TODO updates.
- Obtain fresh bound approval before each corrective GitHub write.
- Repeat the feedback cycle as needed without claiming success before
  supporting results are available.

CI is expected to execute the checks configured in the workflow.
Do not assume it covers every acceptance criterion or all HTTP,
browser, live-server, security or manual validation.

If a required automated check is missing from CI, prepare the relevant
test and any necessary workflow update as part of the proposed changes,
or explicitly identify the uncovered requirement. Do not silently
describe an unconfigured check as delegated to CI.

For non-documentation-only deliveries relying on push-triggered CI, omit
[skip ci] from the proposed commit message. A previous one-off skip request
does not apply to a delivery for which the user subsequently selected CI
validation. If the current instruction explicitly requires skipping CI for
such a delivery, record CI validation as pending until the user specifies
how it will be run. Documentation-only commits always follow section 5
and must not be described as relying on push-triggered CI validation.

Lack of local execution does not waive implementation, test preparation,
documentation, approval or truthful-reporting requirements. It changes
where validation executes, not what counts as evidence.

Do not mark a task or increment fully validated or completed solely
because its code was pushed. Record implementation delivery and
validation status separately.

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
- Before requesting confirmation, verify that the write payload is
  complete and nonempty, contains the intended implementation and test
  files, and includes required documentation updates. Never submit a
  placeholder confirmation, an empty files list, or a confirmation whose
  description promises changes absent from its bound arguments.

If new information requires changing the approved write, request fresh
approval before proceeding.

Include implementation, necessary documentation updates and relevant TODO
status updates in the same proposed commit rather than requesting approval
for an incomplete delivery.

Do not interpret approval for one write as blanket approval for later writes,
merges, workflow dispatches or changes to other branches.

### Coherent staged delivery

Prefer one coherent implementation commit when practical. Do not require
an entire large feature to fit into one commit or approval payload.

When staging is necessary, propose the stages before requesting approval.
Describe each stage's functionality, dependencies, tests, documentation
and remaining work. Obtain the user's agreement to the staging plan.

Each stage must be internally coherent and include the tests and
documentation appropriate to that stage. Clearly identify functionality
that is not yet available. Do not describe a foundation-only stage as a
complete usable feature.

Each external write requires its own bound confirmation. Do not silently
split a write that was approved as one atomic change.

The requirement to include documentation and TODO updates in the same
commit applies to each agreed stage; it does not prohibit staged delivery.

### Preparation versus external writes

An implementation request authorizes repository inspection, analysis,
code/test preparation and preparation of necessary documentation.
Do not repeatedly ask for permission to continue those activities.

Ask a clarification question only when an unresolved decision materially
affects correctness, scope, compatibility, security or delivery.

External writes still require the mandatory bound confirmation with
complete, resolved arguments. General instructions such as "proceed" or
"push it" do not replace that confirmation.

If an approval request was empty, incorrect or incomplete, do not execute
it. Prepare a corrected complete payload and request fresh confirmation;
do not treat the invalid approval as authorization for different contents.

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
