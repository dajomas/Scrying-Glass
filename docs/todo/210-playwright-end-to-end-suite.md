# 210 - Playwright end-to-end suite

[Back to TODO index](../../TODO.md)

## SG-TODO-021 - Extensive Playwright end-to-end suite with a run-and-push script

Status: in progress - Stage 1 delivered 2026-11-13 ([610 handover](../handover/610-playwright-end-to-end-suite.md)); the user's script run `58556e4c` passed 27 of 27 and the user asked to continue. Stage 2 (rosters and initiative) delivered 2026-11-13 on `features/perplexity-021`, user acceptance pending (no CI on that branch); Stages 3-4 not started. Requested 2026-11-12 (originally as a Selenium suite); decisions recorded 2026-11-13. No priority, owner or deadline assigned.

### User decisions (2026-11-13)

- **Framework:** Playwright (Python, pytest), on the browser stack the repository already uses. Not Selenium.
- **Results location:** a results folder on the feature branch, not a separate results branch.
- **Branch:** all SG-TODO-021 work and result pushes go to `features/perplexity-021` (user instruction 2026-11-13). The Branch tests workflow does not trigger on that branch, and workflow edits are not allowed, so pushes there run no CI.
- **Browsers:** Chromium (Chrome) and Firefox. Every scenario runs in both.
- **Retention:** keep only the latest results folder; the script deletes older ones before committing (2026-11-13).

### Approach

- A pytest suite starts a real local Scrying Glass server for each session. It uses a throwaway config and data directory on a free port. HTTP is not faked or intercepted, which also covers the main limitation of the Deliverable 2 fixture tests.
- The suite lives outside `tests/` (proposed: `e2e/`). The CI workflow runs every `tests/*.py` file, and workflow edits are not allowed, so this keeps the suite out of normal CI. It is run on demand with the script below.
- Screenshots, browser console logs and Playwright traces are saved when a test fails.

### Proposed coverage

- **Login and access:** admin login and logout, the User management page, campaign ownership and reassignment, client viewer access, and redirects for users without access.
- **Campaigns and setup:** create, switch and delete campaigns, backups, and retry and scope handling when switching or copying/moving a setup.
- **Rosters:** add, edit and remove characters and monsters, bulk select-all, compact inputs, and monster refresh and review.
- **Initiative:** the join gate, monster rolls (raw roll, bonus, total), manual edits, ordering and keyboard navigation.
- **Combat:** start validation, turn actions, damage preview, HP display, special monster effects, action statistics and ending an encounter.
- **Feedback policy (097):** success messages clear after 5 seconds globally and 3 seconds in panes; errors stay until dismissed; field errors are linked to their fields; the connection warning and recovery are tested by actually stopping and restarting the server.
- **Client Display:** what the display shows, encounter visibility, and live updates from admin actions.
- **Cross-cutting:** several screen widths, dialog focus handling, an accessibility (axe) scan per page, and screenshots/logs on failure.

### Run-and-push script

`tools/run_e2e.sh` (a PowerShell version optional). The user runs it; the assistant does not push results. It:

1. Creates or reuses a virtual environment, installs the test requirements and the Playwright Chromium and Firefox browsers, and starts the server on a free port.
2. Runs pytest for both browsers. It writes JUnit XML, an HTML report, failure screenshots/traces and a summary into `e2e-results/<timestamp>/`.
3. Commits only that folder to `features/perplexity-021`, with a message like `E2E results <date>: N passed, M failed (chromium, firefox) [skip ci]` and the `Co-authored-by: Perplexity <noreply@perplexity.ai>` trailer, then pushes it.
4. Refuses to commit if anything outside the results folder is staged, so `Patch/` or stray files cannot be included. It also refuses if the local branch is behind the remote.

### Delivery stages

Each stage is a separate commit with normal CI (the suite itself is not run by CI) and its own confirmation:

1. Framework, server setup, run-and-push script, and the login/access and campaign/setup tests.
2. Rosters and initiative.
3. Combat and Client Display.
4. Feedback policy, screen widths and accessibility.

The user can stop after any stage.

### Open points

- Retention is decided: only the latest results folder is kept.
- Retry and scope handling during setup switching under request failures moved from Stage 1 to Stage 4 (it needs failure injection or a server restart).
- Credit usage cannot be estimated in advance.
