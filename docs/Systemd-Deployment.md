# Scrying Glass systemd Deployment

## Layout and prerequisites

Use Linux/systemd, Git and Python 3.14+ with sqlite3. Install Python through your supported distribution mechanism; do not pip-install sqlite3. Run one non-root process per storage directory.

- /opt/scrying-glass: read-only code, templates, static and virtual environment.
- /etc/scrying-glass/config.yaml: restricted configuration.
- /var/lib/scrying-glass: writable database, media and migration backups.
- /etc/systemd/system/scrying-glass.service: service unit.

Restrict network reachability before initial start. Default Admin/Client ports are 3000/4000.

## Account and installation

Skip useradd if the account already exists; verify nologin path on your host.

```bash
sudo useradd --system --user-group --home-dir /var/lib/scrying-glass --create-home --shell /usr/sbin/nologin scryingglass
sudo install -d -o scryingglass -g scryingglass -m 0750 /var/lib/scrying-glass
sudo install -d -o root -g scryingglass -m 0750 /etc/scrying-glass
sudo git clone https://github.com/dajomas/scrying-glass.git /opt/scrying-glass
cd /opt/scrying-glass
sudo git fetch origin features/development
sudo git checkout --detach 1541640f9dcb0f202cc1b2b6afa89836f117989b
sudo python3.14 -m venv /opt/scrying-glass/.venv
sudo /opt/scrying-glass/.venv/bin/python -m pip install --upgrade pip
sudo /opt/scrying-glass/.venv/bin/python -m pip install 'fastapi>=0.115' 'uvicorn[standard]>=0.30' 'PyYAML>=6.0' python-multipart
sudo chown -R root:root /opt/scrying-glass
sudo chmod -R a=rX,u+w /opt/scrying-glass
sudo cp config.example.yaml /etc/scrying-glass/config.yaml
sudo editor /etc/scrying-glass/config.yaml
sudo chown root:scryingglass /etc/scrying-glass/config.yaml
sudo chmod 0640 /etc/scrying-glass/config.yaml
```

Deploy the complete source/templates/static layout. Recreate virtual environments at their final path, rather than moving them.

## Configuration and preflight

Set storage_dir to /var/lib/scrying-glass. Use README example display/network settings. If serving only through a local proxy, consider loopback binding; otherwise restrict the LAN/firewall. New configurations have no account credentials. Preserve legacy security.users only through first verified account import.

```bash
cd /opt/scrying-glass
sudo /opt/scrying-glass/.venv/bin/python -c "import sqlite3; print(sqlite3.sqlite_version)"
sudo /opt/scrying-glass/.venv/bin/python -m compileall -q scrying_glass_server.py python web_html
sudo -u scryingglass /opt/scrying-glass/.venv/bin/python -B -c "import scrying_glass_server"
sudo -u scryingglass test -r /etc/scrying-glass/config.yaml
sudo -u scryingglass test -w /var/lib/scrying-glass
```

Imports do not initialize deployment storage or execute server lifespans. Optional foreground test, only without another instance on the same ports/storage:

```bash
sudo -u scryingglass /opt/scrying-glass/.venv/bin/python -u -B /opt/scrying-glass/scrying_glass_server.py --config /etc/scrying-glass/config.yaml
```

Stop before starting systemd.

## Unit file

Create /etc/systemd/system/scrying-glass.service:

```ini
[Unit]
Description=Scrying Glass tabletop encounter manager
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=scryingglass
Group=scryingglass
WorkingDirectory=/opt/scrying-glass
ExecStart=/opt/scrying-glass/.venv/bin/python -u -B /opt/scrying-glass/scrying_glass_server.py --config /etc/scrying-glass/config.yaml
Restart=on-failure
RestartSec=5
UMask=0027
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
ReadWritePaths=/var/lib/scrying-glass
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
CapabilityBoundingSet=
AmbientCapabilities=

[Install]
WantedBy=multi-user.target
```

SQLite needs directory write access for journal/WAL/backup files, not just writable DB file. Code/config remain read-only. -B disables bytecode writes; -u promptly flushes bootstrap output. Protect journal access because first-start credentials can be recorded there. ProtectHome means deployment files should not reside in user homes.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now scrying-glass.service
sudo systemctl status scrying-glass.service
sudo journalctl -u scrying-glass.service -n 100 --no-pager
```

## First-start acceptance

Fresh installation prints random superadmin credentials once. Sign into /users, change the password and create regular admin/client accounts. Legacy initialization may promote the first configured admin; use its existing password. Configuration is not a later reset mechanism.

Verify ownership (unassigned legacy campaigns may need reassignment), client grants, owner isolation and revocation. Exercise both logins, save/load, upload, restart persistence and WebSocket reconnect via the real network/proxy.

One live campaign is shared; no multiple workers, duplicate services or independent per-admin runtimes.

## Network and proxy

Do not expose default HTTP ports directly to the internet or blindly open a public firewall zone. Prefer restricted LAN/VPN plus HTTPS. Proxy WebSocket upgrades and long-lived connections correctly; preserve Host/Origin/scheme consistency for same-origin validation.

Cookies use secure=False at this baseline; review TLS/cookie policy before public exposure. /media is not session-protected. Hidden encounter values do not make uploaded files secret.

## Complete backup

Stop for a consistent filesystem copy. Backups contain account hashes/private GM data. Verify integrity and keep an off-host copy.

```bash
sudo systemctl stop scrying-glass.service
stamp=$(date +%F-%H%M%S)
sudo install -d -m 0700 /root/scrying-glass-backups
sudo tar -C / -czf "/root/scrying-glass-backups/scrying-glass-${stamp}.tar.gz" var/lib/scrying-glass etc/scrying-glass etc/systemd/system/scrying-glass.service
sudo git -C /opt/scrying-glass rev-parse HEAD | sudo tee "/root/scrying-glass-backups/revision-${stamp}.txt" >/dev/null
sudo systemctl start scrying-glass.service
```

Automatic migration backups include database only, not uploads/config. Bundles omit accounts, other campaigns and accumulated recovery collections. Neither replaces full backup.

## Upgrade

1. Record current revision/local changes; stop and verify complete backup.
2. Fetch and deliberately select the target revision.
3. Deploy all source, templates and assets together; preserve config/data.
4. Update dependencies, compile and import-check.
5. Start, inspect migrations and validate real workflows/permissions.
6. Reload existing browser tabs.

```bash
cd /opt/scrying-glass
sudo git status --short
sudo git fetch origin
# Replace TARGET_COMMIT with the reviewed revision before running:
sudo git checkout --detach TARGET_COMMIT
sudo /opt/scrying-glass/.venv/bin/python -m pip install 'fastapi>=0.115' 'uvicorn[standard]>=0.30' 'PyYAML>=6.0' python-multipart
sudo /opt/scrying-glass/.venv/bin/python -m compileall -q scrying_glass_server.py python web_html
sudo -u scryingglass /opt/scrying-glass/.venv/bin/python -B -c "import scrying_glass_server"
sudo systemctl start scrying-glass.service
sudo journalctl -u scrying-glass.service -n 100 --no-pager
```

Detached checkout is not updated with git pull. daemon-reload is needed only if the unit changes. Restart for HTML imports, reload for assets. Never replace live configuration with the example during upgrade.

## Migration and rollback

Original JSON: preserve complete storage and explicit path. Startup imports supported legacy files without modifying them; they then become archival. Loose setups/absent rosters are reconciled through importer rules.

Older SQLite: supported schemas are backed up/upgraded to normalized accounts/features/lairs. Ownership/viewer additive initialization must complete through composed lifespans. Exactly one regular admin receives old campaigns at first ownership migration; otherwise superadmin assignment is required.

Monster Display: stop/disable old service. Keep an explicit old path with matching permissions/ReadWritePaths or move the entire directory while stopped. Use current root entry point and recreate moved virtual environments.

Rollback: stop, preserve failed storage for investigation, restore matching pre-upgrade code/database/media/config. Restore into an empty replacement data directory, not over stale SQLite sidecars. Restore ownership and validate:

```bash
sudo chown -R scryingglass:scryingglass /var/lib/scrying-glass
sudo chown root:scryingglass /etc/scrying-glass/config.yaml
sudo chmod 0640 /etc/scrying-glass/config.yaml
```

Do not edit PRAGMA user_version or perform code-only rollback across unsupported schema changes. Older code may also fail to enforce newer access restrictions. Post-backup changes are lost.

## Offline superadmin recovery

Stop and back up first. Generate a hash using python.scrying_glass_init.password_hash and update the exact existing account with parameterized SQL. Do not use configuration reset. Example interactive session:

```bash
sudo systemctl stop scrying-glass.service
cd /opt/scrying-glass
sudo -u scryingglass /opt/scrying-glass/.venv/bin/python -B
```

```python
import sqlite3
from getpass import getpass
from python.scrying_glass_init import password_hash
username = input("Existing username: ")
password = getpass("New password: ")
assert 8 <= len(password) <= 1024
db = sqlite3.connect("/var/lib/scrying-glass/scrying-glass.sqlite3")
try:
    with db:
        row = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if row is None:
            raise ValueError("Existing user not found")
        db.execute("UPDATE users SET password_hash = ?, role = ? WHERE id = ?", (password_hash(password), "superadmin", row[0]))
finally:
    db.close()
```

Exit and restart. Review ownership if role changed. This is emergency offline administration, not normal user management.

## Troubleshooting

```bash
sudo journalctl -u scrying-glass.service -n 200 --no-pager
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
sudo systemctl cat scrying-glass.service
```

| Failure | Check |
|---|---|
| Missing dependency | ExecStart interpreter and installed packages |
| Missing module/HTML/static | Complete matching source tree |
| SQLite permission/read-only | Writable directory and ReadWritePaths |
| Cannot read config | Group, 0640 and parent traversal |
| Ports used | Old service or foreground instance |
| Missing bootstrap output | First-start protected journal/imported account |
| No campaigns | Ownership assignments, not necessarily lost data |
| Viewer denied | Exact campaign grants/current role |
| Origin rejection | Proxy Host/Origin/scheme |
| Stale display | Session, grants, WebSocket proxy, browser reload |

Import/unit checks do not replace live HTTP, browser, systemd and proxy validation.
