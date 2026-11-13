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

## Stage 1 follow-up - progress output and browser preflight - 2026-11-13

User request: "Is there a way to generate output? Something like: Now running test ###: <Short description of test> ... [SUCCESS|FAILED]". The user also pushed the first real results commit `4453a4d7` (`E2E results 20261113T133947Z`). That run tested `158694d2`: Chromium 13 passed and the server-only check passed, but all 13 Firefox tests errored at browser launch, because the host was missing Firefox's system libraries (Playwright: "Host system is missing dependencies to run browsers"; `playwright install-deps` needed). This was an environment failure, not a test failure.

- `e2e/conftest.py` prints one line per test, for example `Now running test 004/027: Campaign ownership: unassign hides, reassign restores the campaign [chromium] ... SUCCESS`. The result is `SUCCESS`, `FAILED` (test body), `ERROR` (setup/teardown, for example a browser that cannot start, or uncaught page errors) or `SKIPPED`. The description is the first docstring line of each test; every Stage 1 test now has one. pytest's progress dots are suppressed while these lines are active, and `--no-progress` restores the normal output. The final pytest summary only lists failures and errors (`-rfE`).
- `tools/run_e2e.sh` now starts Chromium and Firefox once before the tests (`Browser check: <name> ... OK|FAILED`). If either cannot start, it stops with the `sudo .venv-e2e/bin/python -m playwright install-deps chromium firefox` instruction, before any test runs or anything is committed.
- `--no-push` no longer removes older results folders; pruning to the latest folder now happens only when results are committed.

Validation (local): `tools/run_e2e.sh --no-push` passed both browser checks and printed 27 progress lines, all `SUCCESS` (27 passed). Deliberate failing-test and setup-error probes printed `FAILED` and `ERROR`. The preflight failure path was not exercised, because both browsers start here. No CI runs on `features/perplexity-021`. User acceptance is pending.

## Stage 1 follow-up - dnf system package check - 2026-11-13

User request: Playwright does not natively support RHEL-like systems such as Rocky Linux 10.2, so add a dependency check. Playwright's missing-library message lists apt packages (`libxcursor1 libgtk-3-0t64 libpangocairo-1.0-0 libpango-1.0-0 libcairo-gobject2 libcairo2 libgdk-pixbuf-2.0-0`). The user gave the dnf equivalents: `sudo dnf install -y libXcursor gtk3 pango cairo cairo-gobject gdk-pixbuf2`.

- `tools/run_e2e.sh` reads `/etc/os-release`. When `ID`/`ID_LIKE` contains rhel, fedora, centos, rocky or almalinux and `rpm` is available, it runs `rpm -q` for `libXcursor gtk3 pango cairo cairo-gobject gdk-pixbuf2` before it creates the virtual environment. If any are missing, it stops with `sudo dnf install -y <missing packages>` before any download, test or commit. `E2E_SKIP_DEPS_CHECK=1` skips the check.
- If a browser still cannot start on such a system, the preflight message names the dnf packages instead of `playwright install-deps` (which uses apt). Other systems keep the `install-deps` advice.
- The package list covers the Firefox libraries the user reported. Chromium already started on the user's Rocky host, so no Chromium packages are checked; the browser preflight still catches any other missing library.

Validation (local): `bash -n`. The check block was run on its own with a simulated Rocky `os-release` and a stub `rpm`:
  - with two packages missing, it stopped with `sudo dnf install -y gtk3 pango`;
  - with all packages present, it printed `... OK`;
  - with `E2E_SKIP_DEPS_CHECK=1`, it was skipped;
  - with an Ubuntu `os-release`, it was skipped.

It has not been run on a real Rocky/RHEL host. No CI runs on `features/perplexity-021`.

### User run after the system packages were installed

The user pushed `58556e4c` (`E2E results 20261113T135544Z: 27 passed, 0 failed (chromium, firefox) [skip ci]`). Its `summary.md` reports that the run tested `2fe31145` with pytest exit status 0: Chromium 13 passed, Firefox 13 passed, server-only 1 passed. The commit also deleted the older `e2e-results/20261113T133947Z/` folder. This is the first observed run of the script's commit/push path and of latest-folder-only retention. The dnf check above was added after that run.

## Stage 1 acceptance and close-out - 2026-11-13

User instruction: "Accept Stage 1 and close it".

Stage 1 is accepted and closed: the framework, server fixtures, access and campaign/setup tests, `tools/run_e2e.sh`, the progress lines, the browser preflight and the dnf package check. The acceptance is based on the user's script run `58556e4c` (tested `2fe31145`, 27 passed: Chromium 13, Firefox 13, server-only 1). The later dnf check (`c9af4a73`) has not been run on a Rocky/RHEL host. Retry and scope handling under request failures stays in Stage 4. No CI runs on `features/perplexity-021`.

## Stage 2 - rosters and initiative - 2026-11-13

User instruction: "The first run was succesful: Pushed 58556e4c1baf7c8b7f5c27503c1a4006f5c95ea1 to origin/features/perplexity-021. So please move on to Stage 2".

### Delivered

- `e2e/helpers.py`: shared page helpers (log in and open a workflow tab, add characters and monsters, find a roster row by its exact selection label, set inline initiative). `e2e/test_campaigns.py` now imports `admin` and `open_workflow` from it; its tests are unchanged.
- `e2e/test_rosters.py` (8 tests):
  - add, edit and remove a character, with HP shown as current/max and persistence after reload;
  - the character form requires a name and starting HP;
  - add numbered monsters (quantity 3), check AC, HP, bonus and species, edit one, remove one;
  - a dice expression (`2d6+3`) gives HP within its range, with current equal to max;
  - bulk select-all, unselect-all and remove, for characters and monsters, including the confirm text;
  - bulk actions and Clear selection stay disabled until something is selected;
  - compact inline initiative inputs in both rosters are 7.5ch wide;
  - Refresh from source reviews only the selected monsters. With providers off it shows "No usable source candidates found", Apply stays disabled, and Cancel leaves the roster unchanged.
- `e2e/test_initiative.py` (9 tests):
  - the join gate for characters: Join Battle is refused without initiative. The error is shown and linked to the initiative field (`aria-invalid`, `aria-describedby`); after entering initiative, joining works;
  - the join gate for monsters without a raw roll;
  - a monster's total is its raw roll plus its bonus, recalculated after the bonus is edited, with the raw roll kept and persisted after reload;
  - Roll monster initiatives asks for confirmation, then gives each monster a d20 roll plus its bonus;
  - Roll shared initiative gives the selected monsters one common roll and leaves the others unset;
  - inline and dialog initiative edits for a character are saved;
  - battle order follows initiative, and the tie dialog decides equal totals (`Order: Borin ⇒ Cara ⇒ Orc ⇒ Aelwyn`);
  - cancelling the tie dialog keeps the battle inactive;
  - keyboard navigation: Tab and Shift+Tab move between initiative fields and wrap around, a typed value is saved on Tab, and Escape moves focus to the roster region.
- Every new test has a one-line docstring, which the progress line uses.

Notes for later stages: Playwright treats `aria-disabled="true"` buttons as disabled, so the join-gate tests click with `force=True`. The rosters are listed sorted by name, not by insertion order.

### Validation (local, this sandbox)

- `python -m pytest -q -rfE .` in `e2e/` (Playwright 1.65.1, Chromium and Firefox headless): 61 passed. That is 30 tests in each browser (5 access, 8 campaign, 8 roster and 9 initiative) plus one server-only HTTP check.
- No application, `tests/` or workflow file changed, so the regular suite was not run (user instruction to run only relevant tests). No CI runs on `features/perplexity-021`.
- Not yet run with `tools/run_e2e.sh` on the user's host. User acceptance of Stage 2 is pending; Stages 3-4 are not started.

### User run of Stage 2 and the join-click fix

The user pushed `2aad5117` (`E2E results 20261113T143058Z: 60 passed, 1 failed (chromium, firefox) [skip ci]`). It tested `8e519e6f`: Chromium 29 passed and 1 failed, Firefox 30 passed, server-only 1 passed. The failure was `test_join_gate_requires_initiative[chromium]`. After the initiative save, the second Join Battle click reached the row while it was being re-rendered: the button was still marked as gated and Playwright reported "Element is not visible". `force=True` (needed for the `aria-disabled` button) skips Playwright's actionability waits, so the click raced the re-render.

Fix (test-only): `set_initiative` in `e2e/helpers.py` now waits until the row's Join button is no longer gated, and a shared `join` helper waits for the button to be visible before the forced click. `e2e/test_initiative.py` uses that helper. Locally, `test_initiative.py` passed 18 of 18 (both browsers) in three consecutive runs. The full suite was not rerun here; Stage 2 acceptance is pending a new user run.
