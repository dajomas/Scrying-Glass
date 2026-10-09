# Deploy Scrying Glass with systemd

This guide installs the split application as a single process under a dedicated
non-root account. Code, configuration and writable encounter data remain
separate. See [README](../README.md), [Technical Documentation](Technical-Documentation.md)
and [User Guide](User-Guide.md).

## Prerequisites and layout

Use a Linux system with systemd, Python 3.14+, administrative access and the
repository revision containing the split-source layout. Default listeners are
TCP 3000 (Admin) and 4000 (Client Display).

```text
/opt/scrying-glass/
├── .venv/
├── scrying_glass_server.py
├── python/                    # Application package, including __init__.py
├── web_html/                  # HTML loaders, including __init__.py
├── templates/admin/           # All 20 HTML fragments
├── static/                    # Browser assets
└── config.example.yaml
/etc/scrying-glass/config.yaml
/var/lib/scrying-glass/
├── scrying-glass.sqlite3
└── uploads/
```

Do not place live storage in the checkout. Deploy the complete package and
asset layout. Templates and code are read-only to the service; persistent data
must be writable. web_html avoids a collision with Python's html package.

## Service account and directories

For a new installation (skip account creation if it already exists):

```bash
sudo useradd --system --user-group \
  --home-dir /var/lib/scrying-glass --create-home \
  --shell /usr/sbin/nologin scryingglass
sudo install -d -o scryingglass -g scryingglass -m 0750 /var/lib/scrying-glass
sudo install -d -o root -g scryingglass -m 0750 /etc/scrying-glass
```

## Install application and dependencies

```bash
sudo git clone https://github.com/dajomas/scrying-glass.git /opt/scrying-glass
cd /opt/scrying-glass
```

Select the branch/release that actually contains the split layout. Do not
assume the default branch contains locally applied refactors. If deploying
from an existing working tree, transfer python/, web_html/, templates/, static/
and the root server together, excluding live storage and local credentials.

```bash
sudo python3.14 -m venv /opt/scrying-glass/.venv
sudo /opt/scrying-glass/.venv/bin/python -m pip install --upgrade pip
sudo /opt/scrying-glass/.venv/bin/python -m pip install \
  'fastapi>=0.115' 'uvicorn[standard]>=0.30' 'PyYAML>=6.0' python-multipart
sudo chown -R root:root /opt/scrying-glass
sudo chmod -R a=rX,u+w /opt/scrying-glass
```

The service uses the virtual-environment executable directly; systemd does not
need to activate the environment or invoke the interactive shell launcher.

## Configuration

```bash
sudo cp /opt/scrying-glass/config.example.yaml /etc/scrying-glass/config.yaml
sudo editor /etc/scrying-glass/config.yaml
sudo chown root:scryingglass /etc/scrying-glass/config.yaml
sudo chmod 0640 /etc/scrying-glass/config.yaml
```

Use the README configuration with:

```yaml
storage_dir: "/var/lib/scrying-glass"
```

Replace default credentials. Set bind and ports for the intended network. The
configuration background is the initial/fallback value; named encounters have
their own backgrounds. Uploaded images remain below storage_dir/uploads.

Generate a scrypt password hash without putting the password in command history:

```bash
cd /opt/scrying-glass
sudo /opt/scrying-glass/.venv/bin/python -c \
  'from getpass import getpass; from python.scrying_glass_init import password_hash; print(password_hash(getpass("Password: ")))'
```

Put the emitted scrypt$... string in config.yaml. Protect configuration and
backups as credentials-sensitive data.

## Validate before startup

Compile as root because source ownership/hardening prevents service-user cache
writes. The service can import source without writing bytecode.

```bash
cd /opt/scrying-glass
sudo /opt/scrying-glass/.venv/bin/python -m compileall -q \
  scrying_glass_server.py python web_html
sudo -u scryingglass /opt/scrying-glass/.venv/bin/python -B -c \
  'from web_html.admin_html import ADMIN_HTML; print("HTML loaded:", len(ADMIN_HTML))'
sudo -u scryingglass /opt/scrying-glass/.venv/bin/python -B -c \
  'import scrying_glass_server; print("Server import passed")'
```

These tests check syntax, imports, fragment reads and API construction. They do
not parse deployment config, initialize persistent storage or bind listeners.
For a foreground test, first ensure another instance is not using the ports or
storage directory:

```bash
cd /opt/scrying-glass
sudo -u scryingglass /opt/scrying-glass/.venv/bin/python -B \
  /opt/scrying-glass/scrying_glass_server.py \
  --config /etc/scrying-glass/config.yaml
```

Stop with Ctrl+C before starting the managed service.

## Service unit

Create /etc/systemd/system/scrying-glass.service:

```ini
[Unit]
Description=Scrying Glass tabletop battle display
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=scryingglass
Group=scryingglass
WorkingDirectory=/opt/scrying-glass
ExecStart=/opt/scrying-glass/.venv/bin/python -B /opt/scrying-glass/scrying_glass_server.py --config /etc/scrying-glass/config.yaml
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

ProtectSystem makes code/config/templates read-only. ReadWritePaths grants
storage access; the directory must exist before startup. -B disables bytecode
writes. ProtectHome means code/venv/storage should not live under user homes.
This unit still allows HTTP, WebSockets and optional remote lookups.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now scrying-glass.service
sudo systemctl status scrying-glass.service
sudo journalctl -u scrying-glass.service -f
```

Open http://SERVER:3000/ and http://SERVER:4000/display from the intended LAN.
Use one process/instance per storage directory, not a multi-worker deployment.
Restrict firewall access to intended hosts/subnets. Do not blindly open ports
in a public-facing firewall zone; configure the relevant trusted zone or policy.
For remote use, prefer a VPN and HTTPS reverse proxy with Admin restrictions.

## Upgrade procedure

1. Record the current code revision and preserve config/service unit separately.
2. Stop the server before backing up persistent state.
3. Back up the entire storage directory, including the SQLite database and uploads.
4. Deploy all packages, templates and static files from the same revision.
5. Update dependencies if required, compile and run import checks.
6. Restart and validate workflows, WebSockets and persistence.

```bash
sudo systemctl stop scrying-glass.service
sudo tar -C /var/lib -czf \
  /root/scrying-glass-data-$(date +%F-%H%M%S).tar.gz scrying-glass
```

Update your selected checkout/release. For an already selected Git branch:

```bash
cd /opt/scrying-glass
sudo git pull --ff-only
sudo /opt/scrying-glass/.venv/bin/python -m pip install \
  'fastapi>=0.115' 'uvicorn[standard]>=0.30' 'PyYAML>=6.0' python-multipart
sudo /opt/scrying-glass/.venv/bin/python -m compileall -q \
  scrying_glass_server.py python web_html
sudo -u scryingglass /opt/scrying-glass/.venv/bin/python -B -c \
  'import scrying_glass_server; print("Server import passed")'
sudo systemctl start scrying-glass.service
sudo systemctl status scrying-glass.service
```

A source-only update does not require daemon-reload unless the unit changed.
Do not delete configuration, live data or the virtual environment during file
synchronization. Restart after HTML edits; hard-refresh browsers after assets
change. Roll back matching code and backed-up data if a migration changed the
storage layout; a code-only rollback may not understand migrated data.

## Migrating older installations

The source split alone does not relocate data. Existing explicit storage_dir
continues to work. First startup imports legacy JSON into scrying-glass.sqlite3
without modifying the source files. Loose setups become Default campaign records;
missing campaign rosters are seeded from suitable legacy snapshots. See
[SQLite migration instructions](SQLite-Migration.md).
Back up before the first migration and check the journal afterward.

Monster Display installations used different code/config/storage/service names.
Stop the old service and back up before renaming or transferring anything.
Either retain an explicit old storage path with matching permissions/hardening,
or move the complete directory to /var/lib/scrying-glass and update config.
Update the entry point to scrying_glass_server.py and disable the obsolete
service so both instances cannot start together. Moving a virtual environment
between installation paths may leave absolute interpreter references behind;
recreate .venv at the final path instead of relying on a moved environment.

## Troubleshooting

```bash
sudo journalctl -u scrying-glass.service -n 100 --no-pager
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
```

| Failure | Check |
|---|---|
| No module named uvicorn | Dependencies installed in the ExecStart interpreter |
| No module named local helper | Complete python package and correct relative imports |
| HTML file not found | web_html loader parent.parent path and all templates/admin fragments |
| Static directory missing | Root static directory and its permissions |
| Permission denied saving | storage_dir ownership and ReadWritePaths match |
| Cannot read configuration | root:scryingglass ownership, 0640 file and traversable parent directory |
| Address already in use | Another instance or process owns the configured ports |
| Old page | Restart for markup, hard-refresh for browser assets |

Check campaign rosters in SQLite campaign_characters, not archived JSON files. All sessions are
cleared by restart. A service import test is not a substitute for testing both
ports, login, saving/loading, image uploads and WebSocket delivery.
