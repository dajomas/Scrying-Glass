# Deploy Scrying Glass with systemd

This guide deploys Scrying Glass as a persistent `systemd` service under a dedicated non-root Linux account. Application code, configuration, and writable encounter data are separated so upgrades do not overwrite setups, campaigns, working state, or uploaded images.

See the [README](../README.md), [User Guide](User-Guide.md), and [Technical Documentation](Technical-Documentation.md) for application details.

## Overview

The deployment:

- Starts Scrying Glass at boot.
- Runs it as the non-root `scryingglass` account.
- Restarts it after unexpected failure.
- Stores protected configuration in `/etc/scrying-glass`.
- Stores state, campaigns, setups, and uploads in `/var/lib/scrying-glass`.
- Uses basic `systemd` privilege and filesystem hardening.

| Service | Default port | URL |
|---|---:|---|
| Admin | 3000 | `http://SERVER:3000/` |
| Client Display | 4000 | `http://SERVER:4000/display` |

## Prerequisites

- A Linux host using `systemd`.
- Python **3.14** or newer available as `python3.14`.
- Git, if cloning from the repository.
- Firewall access to ports 3000 and 4000 for intended LAN users.
- An account with `sudo`.

Dependencies:

```text
fastapi
uvicorn[standard]
PyYAML
python-multipart
```

## Deployment layout

```text
/opt/scrying-glass/                 Application code and virtual environment
├── .venv/
├── scrying_glass_server.py
├── admin_html.py
├── client_html.py
├── login_html.py
├── static/
│   ├── admin.css
│   ├── admin.js
│   ├── client.css
│   ├── client.js
│   └── login.css
├── config.example.yaml
└── run.sh

/etc/scrying-glass/                 Protected configuration
└── config.yaml

/var/lib/scrying-glass/             Writable persistent encounter data
├── state.json
├── campaigns.json
├── uploads/
└── setups/
    └── <campaign-slug>/
        └── <setup-name>.json
```

Do not place the live `storage_dir` inside the Git checkout. Persistent data must survive code replacement and Git updates.

## Create account and storage

Create a non-login service account:

```bash
sudo useradd   --system   --user-group   --home-dir /var/lib/scrying-glass   --create-home   --shell /usr/sbin/nologin   scryingglass
```

Create writable persistent storage and protected configuration storage:

```bash
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
sudo /opt/scrying-glass/.venv/bin/python -m pip install   "fastapi>=0.115"   "uvicorn[standard]>=0.30"   "PyYAML>=6.0"   python-multipart

sudo chown -R root:root /opt/scrying-glass
sudo chmod -R a=rX,u+w /opt/scrying-glass
```

The service account should not be able to change executable code or static browser assets.

## Configure application

```bash
sudo cp /opt/scrying-glass/config.example.yaml /etc/scrying-glass/config.yaml
sudo editor /etc/scrying-glass/config.yaml
```

Example:

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
  default_monster_color: "#842029"
  default_character_color: "#1f4e79"
  dndbeyond_image_lookup: true
```

Secure configuration credentials:

```bash
sudo chown root:scryingglass /etc/scrying-glass/config.yaml
sudo chmod 0640 /etc/scrying-glass/config.yaml
```

`display.background` is the fallback for legacy setup files and the initial background for a new setup. Use the Admin UI to set and save each setup's individual Client Display background. Uploaded image backgrounds are stored below `/var/lib/scrying-glass/uploads/`.

### Use scrypt hashes

Plaintext passwords work, but scrypt hashes are preferable:

```bash
cd /opt/scrying-glass
sudo /opt/scrying-glass/.venv/bin/python -c   'from scrying_glass_server import password_hash; print(password_hash("replace-me"))'
```

Use the resulting `scrypt$...` value in the configuration.

## Validate installation

```bash
cd /opt/scrying-glass

sudo /opt/scrying-glass/.venv/bin/python -m py_compile   scrying_glass_server.py   admin_html.py   client_html.py   login_html.py

sudo find static -maxdepth 1 -type f   \( -name '*.js' -o -name '*.css' \)   -printf '%f\n' | sort
```

The Python command should produce no output. The second command should list `admin.css`, `admin.js`, `client.css`, `client.js`, and `login.css`.

Optional foreground test:

```bash
sudo -u scryingglass   /opt/scrying-glass/.venv/bin/python   /opt/scrying-glass/scrying_glass_server.py   --config /etc/scrying-glass/config.yaml
```

Stop it with `Ctrl+C` after confirming both ports are listening.

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

| Setting | Effect |
|---|---|
| `User` / `Group` | Runs without root privileges |
| `UMask=0027` | Restricts permissions on newly created files |
| `NoNewPrivileges=true` | Prevents privilege gain through execution |
| `PrivateTmp=true` | Uses an isolated temporary directory |
| `ProtectHome=true` | Blocks normal user home directories |
| `ProtectSystem=strict` | Makes most host paths read-only |
| `ReadWritePaths=/var/lib/scrying-glass` | Allows writes only to persistent application data |
| `CapabilityBoundingSet=` | Removes unnecessary Linux capabilities |

The service retains network access for Admin and Client traffic, WebSockets, and optional external image lookup.

## Start and verify

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now scrying-glass.service
sudo systemctl status scrying-glass.service
sudo journalctl -u scrying-glass.service -f
```

Verify listener sockets:

```bash
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
```

Verify writable persistent storage:

```bash
sudo ls -la /var/lib/scrying-glass
sudo ls -la /var/lib/scrying-glass/uploads
sudo ls -la /var/lib/scrying-glass/setups
sudo ls -la /var/lib/scrying-glass/campaigns.json
```

The first start creates `campaigns.json` and a Default campaign folder. If setup saves or image uploads fail, repair permissions:

```bash
sudo chown -R scryingglass:scryingglass /var/lib/scrying-glass
sudo chmod -R u=rwX,g=rX,o= /var/lib/scrying-glass
sudo systemctl restart scrying-glass.service
```

## Firewall and remote access

Allow ports only on trusted networks. Example for firewalld:

```bash
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=4000/tcp
sudo firewall-cmd --reload
```

Do not publish the default HTTP ports to the public internet. If remote access is necessary, place an HTTPS reverse proxy in front of the service, bind or firewall the back-end ports appropriately, use a VPN or access controls for Admin access, and use scrypt password hashes.

## Upgrades and backups

Back up persistent data before every upgrade:

```bash
sudo tar -C /var/lib -czf   /root/scrying-glass-backup-$(date +%F).tar.gz   scrying-glass
```

Upgrade code and dependencies:

```bash
cd /opt/scrying-glass
sudo git fetch --all --prune
sudo git checkout features/development
sudo git pull --ff-only

sudo /opt/scrying-glass/.venv/bin/python -m pip install   "fastapi>=0.115"   "uvicorn[standard]>=0.30"   "PyYAML>=6.0"   python-multipart

sudo /opt/scrying-glass/.venv/bin/python -m py_compile   scrying_glass_server.py   admin_html.py   client_html.py   login_html.py

sudo find /opt/scrying-glass/static -maxdepth 1 -type f   \( -name '*.js' -o -name '*.css' \)   -printf '%f\n' | sort

sudo systemctl restart scrying-glass.service
sudo systemctl status scrying-glass.service
```

The working encounter, campaigns, setups, activity logs, per-setup backgrounds, and uploads persist because they remain outside the Git checkout in `/var/lib/scrying-glass`.

After an upgrade, hard-refresh both Admin and Client browser pages. Static browser files live in `/opt/scrying-glass/static/`; updating Python files without the corresponding static files can leave the interface loading but behaving like an older release.

### Campaign migration

The first start after upgrading from pre-campaign storage automatically moves:

```text
/var/lib/scrying-glass/setups/*.json
```

to:

```text
/var/lib/scrying-glass/setups/default/
```

It also registers the Default campaign in `campaigns.json`. Review the migration log with:

```bash
sudo journalctl -u scrying-glass.service -b | grep 'unassigned battle setup'
```

Make a backup before the first start. A version without campaign support does not read nested `setups/<campaign>/` folders, so rolling back requires restoring a compatible backup.

## Migrating from Monster Display

Earlier installations may use `/opt/monster-display`, `/etc/monster-display`, `/var/lib/monster-display`, a `monsterdisplay` account, and `monster-display.service`.

1. Stop the former service and back up data.

   ```bash
   sudo systemctl disable --now monster-display.service
   sudo tar -C /var/lib -czf /root/monster-display-backup-$(date +%F).tar.gz monster-display
   ```

2. Rename account and group while retaining UID/GID.

   ```bash
   sudo usermod -l scryingglass -d /var/lib/scrying-glass monsterdisplay
   sudo groupmod -n scryingglass monsterdisplay
   ```

3. Move directories.

   ```bash
   sudo mv /opt/monster-display /opt/scrying-glass
   sudo mv /etc/monster-display /etc/scrying-glass
   sudo mv /var/lib/monster-display /var/lib/scrying-glass
   ```

4. Update repository configuration and application code.

   ```bash
   cd /opt/scrying-glass
   sudo git remote set-url origin https://github.com/dajomas/scrying-glass.git
   sudo git pull --ff-only
   ```

5. Update `storage_dir` in `/etc/scrying-glass/config.yaml`.

   ```bash
   sudo sed -i 's#/var/lib/monster-display#/var/lib/scrying-glass#' /etc/scrying-glass/config.yaml
   ```

6. Create the `scrying-glass.service` unit shown above, remove the old unit, and start the new service.

   ```bash
   sudo rm /etc/systemd/system/monster-display.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now scrying-glass.service
   sudo systemctl status scrying-glass.service
   ```

Campaigns, setups, uploads, and working state move with the persistent directory. Users must sign in again because session cookies changed.

## Troubleshooting

### Service will not start

```bash
sudo journalctl -u scrying-glass.service -n 100 --no-pager
```

Common causes are missing Python 3.14, missing dependencies, invalid YAML, unreadable configuration, unwritable storage/campaign directories, or a port already in use.

### Service cannot write state or uploads

The `scryingglass` account must own the configured storage directory. If `storage_dir` is moved, update `ReadWritePaths` in the unit too.

### Browser uses old page code

Restart the service, verify that all expected files exist in `/opt/scrying-glass/static/`, then hard-refresh:

- Linux/Windows: `Ctrl+Shift+R`
- macOS: `Cmd+Shift+R`

For a dedicated kiosk display, fully close and reopen the browser if hard refresh does not clear cached assets.

### Admin or Client cannot log in

Confirm the configured account, password, role, and port. Sessions are cleared on restart. Admin and Client use distinct cookies and can be logged in simultaneously in one browser.
