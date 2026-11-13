# 610 - Playwright end-to-end suite (SG-TODO-021)

[Back to handover index](../../HANDOVER.md)

Plan and decisions: [TODO 210](../todo/210-playwright-end-to-end-suite.md).

## Stage 1 - 2026-11-13

User instruction: "Open Point: Only leave the latest result folder. Start SG-TODO-021 Stage 1 for the Playwright end-to-end suite".

### Delivered

- `e2e/conftest.py`: for each test it starts a real `scrying_glass_server.py` process on two free local ports. The server gets a temporary storage directory and a generated config with three fixed accounts (superadmin, admin, client), seeded through `security.users`. Monster lookup providers are switched off, so there is no external network use. No HTTP is intercepted; the server itself serves the assembled `admin.js`, and the checkout is not changed. A session-scoped browser fixture runs each test in Chromium and Firefox (`--browser-name` selects one). Confirm dialogs are accepted, and prompts are answered from a per-session queue. Uncaught page errors fail the test. When a test fails, full-page screenshots, a Playwright trace, the console log and the server log are saved under `<results>/failures/<test>/`.
- `e2e/test_access.py` (6 tests):
  - admin login with a wrong and a correct password, and logout;
  - the login and Admin page redirects;
  - role routing: superadmin goes to `/users`, an admin gets 403 on `/users`, a client account is rejected at the Admin login;
  - unauthenticated API requests get 401 on both portals;
  - a superadmin creates a client user, who can then sign in to the Client display;
  - campaign ownership: unassigning hides the campaign from the admin, and reassigning brings it back;
  - viewer access is granted and revoked, and the Client display follows.
- `e2e/test_campaigns.py` (8 tests):
  - create, edit and switch campaigns, with persistence after a reload;
  - the required name check;
  - the last campaign cannot be deleted;
  - delete a campaign, either moving its setups or deleting them;
  - save, load, rename and delete a battle setup;
  - copy a setup to another campaign;
  - export a campaign bundle and import it again as a new campaign.
- `tools/run_e2e.sh`: the run-and-push script.
  1. Checks that `features/perplexity-021` (override with `E2E_BRANCH`) is checked out, nothing is staged and the branch is not behind the remote.
  2. Creates or reuses `.venv-e2e`, then installs `e2e/requirements.txt` (the test requirements plus `pytest-html`) and the Playwright Chromium and Firefox browsers.
  3. Runs the suite and writes `junit.xml`, `report.html`, `pytest.log`, `summary.md` (counts per browser and the tested commit) and any failure artifacts to `e2e-results/<UTC timestamp>/`.
  4. Deletes every older results folder, so only the latest is kept (user decision).
  5. Refuses to commit anything outside `e2e-results/`.
  6. Commits `E2E results <stamp>: N passed, M failed (chromium, firefox) [skip ci]` with the Co-authored-by trailer and pushes it.

  `--no-push` runs the suite without committing. The script exits with pytest's status.
- The suite is outside `tests/`, so CI's unittest discovery, compile step, Node step and standalone-script step do not pick it up. The workflow is unchanged.

### Not in Stage 1

Retry and scope handling during setup switching under request failures needs a server stop/restart or failure injection. It moves to Stage 4 together with the connection warning and recovery tests. Stages 2-4 are not started.

### Validation (local, this sandbox)

- `python -m pytest -q` in `e2e/` (Playwright 1.65.1, Chromium and Firefox headless): 27 passed. That is 13 tests in each browser plus one server-only HTTP check.
- `tools/run_e2e.sh --no-push`: created the virtual environment, installed the dependencies and browsers, and ran 27 passed. It wrote the summary, JUnit and HTML report, and the folder was deleted afterwards.
- A deliberately failing probe test confirmed that the screenshot, trace, console log and server log are written.

The push path of the script (commit/push of results) was not executed here. CI does not run this suite.

### Branch

On the user's instruction this stage and all later SG-TODO-021 pushes, including result commits, go to `features/perplexity-021`, branched from `features/perplexity` at `187f5be1`. The Branch tests workflow triggers only on `features/perplexity`, `features/perplexity-018` and `features/perplexity-009.7`, and workflow edits are not allowed. So no CI runs for this branch; the regular suite is unaffected by this commit (no `tests/`, application or workflow change). User acceptance is pending.
