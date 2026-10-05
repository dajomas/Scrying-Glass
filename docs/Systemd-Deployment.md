# Deploy Scrying Glass with systemd

This guide deploys Scrying Glass as a persistent `systemd` service under a dedicated non-root Linux account. Application code, configuration, and writable encounter data are separated so upgrades do not overwrite campaigns, character rosters, battle setups, working state, or uploads.

See the [README](../README.md), [User Guide](User-Guide.md), and [Technical Documentation](Technical-Documentation.md) for application details.

## Overview

The deployment:

- Starts Scrying Glass at boot.
- Runs it as the non-root `scryingglass` account.
- Restarts after unexpected failure.
- Stores configuration in `/etc/scrying-glass`.
- Stores persistent data in `/var/lib/scrying-glass`.
- Allows optional outbound HTTPS traffic for D&D Beyond image lookup when enabled.

| Service | Default port | URL |
|---|---:|---|
| Admin | 3000 | `http://SERVER:3000/` |
| Client Display | 4000 | `http://SERVER:4000/` or `http://SERVER:4000/display` |

## Prerequisites

- Linux host using `systemd`.
- Python **3.14** or newer.
- Git, if cloning from the repository.
- Firewall access to ports 3000 and 4000 for trusted LAN users.
- An account with `sudo`.

Install dependencies:

```bash
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

## Deployment layout

```text
/opt/scrying-glass/                 Application code and virtual environment
├── .venv/
├── scrying_glass_server.py
├── admin_html.py
├── client_html.py
├── login_html.py
└── static/
    ├── admin.css
    ├── admin.js
    ├── client.css
    ├── client.js
    └── login.css

/etc/scrying-glass/
└── config.yaml

/var/lib/scrying-glass/
├── state.json
├── campaigns.json
├── characters/
│   └── <campaign-slug>.json
├── uploads/
└── setups/
    └── <campaign-slug>/
        └── <setup-name>.json
```

Do not place `storage_dir` in the Git checkout. The `characters/`, `setups/`, `uploads/`, and state files are all persistent application data.

## Create account and storage

```bash
sudo useradd \
  --system \
  --user-group \
  --home-dir /var/lib/scrying-glass \
  --create-home \
  --shell /usr/sbin/nologin \
  scryingglass

sudo install -d -o scryingglass -g scryingglass -m 0750 /var/lib/scrying-glass
sudo install -d -o root -g scryingglass -m 0750 /etc/scrying-glass
```

## Install application

```bash
sudo git clone https://github.com/dajomas/scrying-glass.git /opt/scrying-glass
cd /opt/scrying-glass
sudo git checkout features/development

sudo python3.14 -m venv /opt/scrying-glass/.venv
sudo /opt/scrying-glass/.venv/bin/python -m pip install --upgrade pip
sudo /opt/scrying-glass/.venv/bin/python -m pip install \
  "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart

sudo chown -R root:root /opt/scrying-glass
sudo chmod -R a=rX,u+w /opt/scrying-glass
```

The service account should not be able to modify executable code or static browser assets.

## Configure application

```bash
sudo cp /opt/scrying-glass/config.example.yaml /etc/scrying-glass/config.yaml
sudo editor /etc/scrying-glass/config.yaml
```

```yaml
network:
  bind: "0.0.0.0"
  admin_port: 3000
  client_port: 4000

storage_dir: "/var/lib/scrying-glass"

security:
  users:
    - username: "dm"
      role: "admin"
      password: "replace-with-a-strong-admin-password"
    - username: "table"
      role: "client"
      password: "replace-with-a-strong-client-password"

display:
  background: "#080b14"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  dndbeyond_image_lookup: true
```

```bash
sudo chown root:scryingglass /etc/scrying-glass/config.yaml
sudo chmod 0640 /etc/scrying-glass/config.yaml
```

`dndbeyond_image_lookup: true` permits best-effort lookup of a dedicated D&D Beyond monster image when no image is uploaded. The service needs outbound DNS and HTTPS access for this optional feature. Failures do not block monster creation. Set it to `false` in restricted or offline environments.

## Validate installation

```bash
cd /opt/scrying-glass
sudo /opt/scrying-glass/.venv/bin/python -m py_compile \
  scrying_glass_server.py admin_html.py client_html.py login_html.py
```

Optional foreground test:

```bash
sudo -u scryingglass \
  /opt/scrying-glass/.venv/bin/python \
  /opt/scrying-glass/scrying_glass_server.py \
  --config /etc/scrying-glass/config.yaml
```

Stop the foreground test with `Ctrl+C` after confirming both ports listen.

## Create service

Create `/etc/systemd/system/scrying-glass.service`:

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
ExecStart=/opt/scrying-glass/.venv/bin/python /opt/scrying-glass/scrying_glass_server.py --config /etc/scrying-glass/config.yaml
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

`AF_INET` and `AF_INET6` are required for Admin/Client traffic and optional D&D Beyond HTTPS lookups. No additional write path is required: all uploads, campaign rosters, setup snapshots, and runtime state are kept below `/var/lib/scrying-glass`.

## Start and verify

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now scrying-glass.service
sudo systemctl status scrying-glass.service
sudo journalctl -u scrying-glass.service -f
```

```bash
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
sudo ls -la /var/lib/scrying-glass
sudo ls -la /var/lib/scrying-glass/characters
sudo ls -la /var/lib/scrying-glass/setups
sudo ls -la /var/lib/scrying-glass/uploads
```

If setup saves, campaign roster writes, or image uploads fail, repair permissions:

```bash
sudo chown -R scryingglass:scryingglass /var/lib/scrying-glass
sudo chmod -R u=rwX,g=rX,o= /var/lib/scrying-glass
sudo systemctl restart scrying-glass.service
```

## Persistence behavior

- Any character mutation is saved automatically to the active campaign roster in `characters/<campaign-slug>.json`.
- Any monster mutation is saved automatically to the currently loaded saved battle setup.
- An encounter with no active saved setup remains an unsaved working encounter in `state.json` until it is explicitly saved.
- Battle operations that can change both monsters and characters persist both ownership stores.
- Uploading a monster image through **Save monster** writes a new file below `uploads/`; selecting a replacement file in the browser without saving does not upload it.

## Upgrades and backups

Back up the complete persistent directory before every upgrade:

```bash
sudo tar -C /var/lib -czf \
  /root/scrying-glass-backup-$(date +%F).tar.gz \
  scrying-glass
```

This backup must include campaign metadata, campaign character rosters, setup snapshots, `state.json`, activity logs, and uploads. A setup or roster can reference uploaded monster or background images, so do not back up JSON files without `uploads/`.

Upgrade:

```bash
cd /opt/scrying-glass
sudo git fetch --all --prune
sudo git checkout features/development
sudo git pull --ff-only

sudo /opt/scrying-glass/.venv/bin/python -m pip install \
  "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart

sudo /opt/scrying-glass/.venv/bin/python -m py_compile \
  scrying_glass_server.py admin_html.py client_html.py login_html.py

sudo systemctl restart scrying-glass.service
sudo systemctl status scrying-glass.service
```

After upgrades that change static files, hard-refresh Admin and Client pages:

- Linux/Windows: `Ctrl+Shift+R`
- macOS: `Cmd+Shift+R`

For troubleshooting static browser assets, open Chrome DevTools → **Network**, enable **Disable cache**, then reload. Deploy matching versions of `admin_html.py`, `static/admin.js`, `static/admin.css`, and `scrying_glass_server.py` together.

## Troubleshooting

### Service will not start

```bash
sudo journalctl -u scrying-glass.service -n 100 --no-pager
```

Common causes are missing Python, dependencies, invalid YAML, unreadable configuration, unwritable storage, or a port already in use.

### Service cannot save setup, roster, or image

Confirm the service account owns the configured `storage_dir`. If it changed, also update `ReadWritePaths` in the systemd unit.

### D&D Beyond image lookup does not work

Confirm `display.dndbeyond_image_lookup: true`, outbound DNS/HTTPS connectivity, and that **Monster species** is a canonical D&D Beyond monster name. The lookup is best effort; upload an image manually when it returns no exact usable monster-page image.

### Browser uses old page code

Restart the service, check `/opt/scrying-glass/static/`, then hard-refresh. A stale `admin.js` can leave a newer HTML template apparently loaded while its form behavior remains old.

## Migrating from Monster Display

Back up the old persistent directory, move it deliberately, update `storage_dir`, and deploy the renamed service. Users must sign in again because session cookies changed. See the README and Technical Documentation for the storage and state model.
