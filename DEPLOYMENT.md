# Scrying Glass deployment package

Source: features/development, commit 4d3e3b6946024025854af01329b6c363510c1f0a.
This is a complete source deployment, not an incremental patch or offline installer.
Read [release notes](Patch/Deployment-Release-Notes.md) and
[validation](Patch/Deployment-Validation.md) before use.

## Contents and integrity

The package contains the source tree, example configuration, documentation,
launchers and tests. Live config, databases, uploaded media, accounts, virtualenvs,
Git history and cached bytecode are not included. Python/runtime packages must
be installed separately; requirements.txt is intentionally not a lockfile.
No application runtime code was changed during packaging.

After extracting, enter the top-level package directory and run:

```bash
python3 deployment/check.py
```

On Windows, use `py -3 deployment/check.py`. This checks hashes/sizes of the
listed files; it is not a cryptographic signature and ignores extra local files
such as config.yaml. The manifest excludes itself to avoid circular hashing.
An external SHA-256 file accompanies the ZIP for transfer-integrity checking.

## Fresh installation: explicit environment

Install Python 3.10 or newer with venv/pip and standard-library sqlite3 using your
platform's supported mechanism. Python 3.10 is the launcher minimum, not a claim
of completed end-to-end 3.10 validation. Use the intended interpreter consistently.
For a manual Linux installation from this extracted tree:

```bash
python3.10 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python deployment/check.py --runtime
cp config.example.yaml config.yaml
```

For Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe deployment/check.py --runtime
Copy-Item config.example.yaml config.yaml
```

Only copy the example configuration for a fresh installation. Edit network,
storage and display settings before starting; protect the config appropriately.
Use an explicit existing storage path when migrating an installation. Start
manually using the same environment:

```bash
.venv/bin/python scrying_glass_server.py --config config.yaml
```

On Windows use `.\.venv\Scripts\python.exe scrying_glass_server.py --config config.yaml`.
Keep first-start console output private: new installations print a generated
superadmin password. Follow [Accounts and sign-in](docs/User-Guide.md#accounts-and-sign-in)
to configure account roles and grants. Restrict ports to trusted networks.

The supplied ./run.sh, .\run.ps1 and run.bat remain alternative interactive
launchers: they use ~/dnd or %USERPROFILE%\dnd, not the .venv created above.
Do not assume running a launcher selects this manual environment. Compatible
existing launcher environments are reused; older environments are rejected.

## systemd deployment

Use [Systemd Deployment](docs/Systemd-Deployment.md), but supply the extracted
source tree in place of its git clone/checkout steps. Do not checkout main when
using this commit-pinned package. Create the service virtualenv at its final
/opt/scrying-glass/.venv path, install requirements with that interpreter, and run
its deployment/check.py --runtime. Do not move an existing virtualenv.
The service invokes its interpreter directly, bypassing launcher selection/guards.
Run one application process per storage directory; do not expose HTTP publicly
without the access/proxy protections described in the documentation.

## Upgrade and rollback

1. Record the current code revision, Python, installed dependency versions,
   systemd unit, configuration and absolute storage path. Save the current
   environment's pip freeze output with the operator's backup, not as a package lock.
2. Stop the service/process before making a consistent backup. Back up the whole
   configured storage directory, including SQLite and any -wal/-shm companions
   if present, media and migration backups; preserve config and service-unit copies.
3. Retain the prior code tree and a reproducible way to rebuild its environment.
   Verify that the backup can be read/restored before changing the installation.
4. Stage/extract this package separately, verify checksums, and review release notes.
   Promote the complete source tree into the intended code location while stopped.
   Do not overwrite live config or delete storage; no automated destructive copy
   or data-directory replacement is performed by this package.
5. Create/rebuild an environment at its final path if needed. Install dependencies,
   run runtime preflight with that interpreter, and preserve storage permissions.
6. Start the service, inspect startup/migration logs, then reload Admin and Client
   browsers to match the imported HTML and new JavaScript assets.
7. Complete the smoke test below before reopening the encounter to other users.

If validation fails, stop the process. Restore the matching prior code/config/unit
and environment. If initialization changed stored data or schema, restore the
matching stopped-storage backup too; do not assume a code-only rollback is safe.
Restoring a backup discards changes made after that backup. No new database
migration is introduced by the packaging additions; the source's own startup
migration behavior still applies.

## Required live smoke test

- Sign in with the relevant roles; check campaign ownership and client grants.
- Load a copied encounter and verify persistence and live Client updates.
- Start combat, check character-first tie defaults and manual position swaps.
- Open actions, apply a mixed action/reaction batch, and verify the window remains
  open with locked Applied rows. Apply again unchanged: no duplicate HP/log entry.
- Add another action/reaction and apply: only new rows resolve in displayed order.
- Add an unfinished row then Close: no pending changes apply and earlier changes
  are not undone. Reopen and test explicit target/source selection.
- Verify start-of-turn controls remain separate and Next advances as expected.
- Check log export, backgrounds, restart recovery and intended player display.

## Release status

Static checks and selected mocked/unit suites passed during packaging. Two of
19 additional standalone JavaScript scripts fail with window is not defined in
their VM contexts; see the validation report for exact filenames. These failures
were reproduced on the supplied source and were not silently repaired. This is
not a fully runtime-certified release: FastAPI, Uvicorn and python-multipart are
not installed in the packaging environment, so full server startup/HTTP/browser,
Windows execution, full Python suite and Python 3.10 application tests remain
outstanding. Complete target-machine preflight and smoke tests before live use.
