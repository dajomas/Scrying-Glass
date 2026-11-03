# Scrying Glass deployment

## Current checkout versus historical packages

Deploy a reviewed Git revision and record that revision with your backup. The old
root package manifest described a historical deployment archive, not the current
working tree. Manifest-based verification is retired. `deployment/check.py` is
now runtime-only preflight: no arguments and `--runtime` perform the same check.
It does not verify hashes, package completeness, authenticity or provenance. A
legacy manifest, if present during staged cleanup, is unused; its physical
deletion is a separate housekeeping commit. Use release-specific checksums or
Git identity when you need source/package integrity.

Historical overlay instructions and validation reports belong to their original
Git revisions/packages. Do not assume old Patch/ paths exist in this checkout or
that their recorded results validate today's code. The technical reference is
an [index](docs/Technical-Documentation.md) with required topic files under
`docs/technical/`; keep those files together when copying documentation.

## Requirements and layout

Use Python 3.10 or newer with venv/pip and working standard-library sqlite3. The
launcher minimum is not proof of compatibility for every Python/dependency pair.
Run one application process per storage directory; multiple workers/replicas are
unsupported. Runtime dependencies are in requirements.txt, not a lockfile. Node
and Playwright are test dependencies, not server runtime requirements.

Deploy `scrying_glass_server.py`, `python/`, `web_html/`, `templates/` and the
complete `static/` tree together. Keep package __init__.py files. Do not deploy the
tracked static/admin.js marker alone: the matching adapter assembles eight source
fragments at runtime. The service account needs a writable temporary directory.
Restart after imported Python/HTML changes and reload browsers for matching assets.

## Fresh installation with an explicit environment

From the reviewed source checkout on Linux:

```bash
python3.10 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python deployment/check.py --runtime
cp config.example.yaml config.yaml
.venv/bin/python scrying_glass_server.py --config config.yaml
```

A newer compatible interpreter may replace python3.10. For Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe deployment/check.py --runtime
Copy-Item config.example.yaml config.yaml
.\.venv\Scripts\python.exe scrying_glass_server.py --config config.yaml
```

Copy the configuration only on a fresh install. Set network, storage and display
settings before startup; preserve existing config/storage during upgrades. Use an
absolute storage path for services. Start the root script directly, not external
uvicorn module:app imports that skip main-guard initialization.

Preflight checks the interpreter, sqlite3, installed runtime dependencies and a
server import/route-construction subprocess. It does not run application
lifespans, initialize deployment storage, bind listeners, authenticate users or
exercise browser workflows. A successful result is not deployment certification.

The interactive launchers use ~/dnd or %USERPROFILE%\dnd, not the .venv above.
They reuse compatible environments and reject older ones rather than replacing
or downgrading them. Systemd runs its explicitly configured interpreter directly,
without launcher discovery/guards; see [Systemd Deployment](docs/Systemd-Deployment.md).
Create service environments at their final path and do not move virtualenvs.

## Accounts and exposure

New installs print a generated superadmin password once; keep that output private
and change the password. Create regular admin/client accounts and separately
assign campaign ownership and client viewer grants. Use a regular admin for
interactive battles; superadmins land on user management. See the
[User Guide](docs/User-Guide.md#accounts-and-sign-in).

Restrict ports to a trusted LAN/VPN or protected HTTPS proxy. Sessions are in
memory and clear on restart. Media is a static mount without session protection.
Coordinate admins because one shared active runtime remains. Review proxy/TLS
and WebSocket handling before exposing listeners.

## Upgrade and rollback

1. Record the current Git revision, Python/dependency versions, configuration,
   service unit and absolute storage path. Preserve operator pip-freeze output
   with the backup; do not mistake it for a repository dependency lock.
2. Stop the process before a consistent backup. Back up the entire storage
   directory, SQLite and any WAL/SHM companions, uploaded media, migration backups,
   configuration and service-unit copies. Verify that the backup is restorable.
3. Keep matching prior code and a reproducible way to rebuild its environment.
   Stage the new reviewed source separately; do not overwrite config or storage.
4. Promote the complete matching source tree while stopped. Install requirements
   in the intended environment and run runtime preflight with that interpreter.
   Preserve storage permissions and the generated-bundle temporary-directory access.
5. Start, inspect migration/startup logs and reload Admin and Client browsers.
   Run the copied-data smoke checks below before reopening the encounter.

If validation fails, stop and restore matching prior code/config/unit/environment.
If startup changed schema or data, restore the matching stopped-storage backup
too; code-only rollback is not necessarily safe. Restoring a backup discards
subsequent edits. Automatic database migration backups omit media/configuration.
Never fake a downgrade by editing PRAGMA user_version. Older code rejects schema 8;
see [attack statistics](docs/Technical-Documentation.md#attack-statistics-schema-8).

## Copied-data live smoke checks

- Sign in with relevant roles; check ownership, grants and cross-owner denial.
- Load an encounter, verify persistence and live Client updates.
- Start combat; check initiative ties, manual position swaps, rounds and Next.
- Apply mixed actions/reactions and statistic reductions. Confirm Applied rows
  stay locked, the window remains open and applying unchanged rows does not replay.
- Add a pending row then Close; no draft applies and earlier changes are not undone.
- Check restoration/base editing, HP and life states, effects and lairs.
- Check row controls, readable names, table-local keyboard scrolling and retained
  alternate damage/healing workflows.
- Check log export, backgrounds, restart recovery, backups/bundles/media and proxy
  WebSockets. Validate Windows and the chosen Python version on the actual target.

These are instructions, not claims that this maintenance change executed live
validation. Local preflight tests mock dependencies and the server-import process.
CI is skipped only as explicitly requested for the agreed two maintenance commits.
