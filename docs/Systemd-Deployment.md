# Deploy Scrying Glass with systemd

This page explains how to run Scrying Glass as a persistent `systemd` service under a dedicated non-root Linux account. The deployment separates application code, credentials/configuration, and writable encounter data so that upgrades do not overwrite saved setups or uploaded images.

See [[Home]] for the project overview, [[User Guide]] for using the Admin and Client Display screens, and [[Technical Documentation]] for architecture and API details.

## What this deployment provides

- Starts Scrying Glass automatically at boot.
- Runs the application as a dedicated non-root user named `scryingglass`.
- Restarts the service after an unexpected failure.
- Keeps configuration in `/etc/scrying-glass`.
- Keeps current state, campaigns, saved setups, and image uploads in `/var/lib/scrying-glass`.
- Applies basic `systemd` filesystem and privilege hardening.

The application runs two HTTP services from one Python process:

| Service | Default port | URL |
|---|---:|---|
| Admin | 3000 | `http://SERVER:3000/` |
| Client Display | 4000 | `http://SERVER:4000/display` |

## Prerequisites

- A Linux host using `systemd`.
- Python **3.14** or newer available as `python3.14`.
- Git, if installing from the repository.
- Network/firewall access to TCP ports 3000 and 4000 for intended users.
- An Administrator account with `sudo` access.

Scrying Glass requires:

```text
fastapi
uvicorn[standard]
PyYAML
python-multipart
```

## Deployment layout

This guide uses the following paths:

```text
/opt/scrying-glass/                 Application code and virtual environment
├── .venv/
├── scrying_glass_server.py
├── admin_html.py
├── client_html.py
├── login_html.py
└── config.example.yaml

/etc/scrying-glass/                 Protected configuration
└── config.yaml

/var/lib/scrying-glass/             Writable persistent encounter data
├── state.json
├── campaigns.json                    Campaign registry (active campaign, names)
├── uploads/
└── setups/
    └── <campaign>/                   One folder per campaign
        └── <setup>.json
```

Do not put the live `storage_dir` inside the Git checkout. The persistent directory must survive Git pulls, release replacements, and application upgrades.

## Create the service account

Create a system account without an interactive shell:

```bash
sudo useradd \
  --system \
  --user-group \
  --home-dir /var/lib/scrying-glass \
  --create-home \
  --shell /usr/sbin/nologin \
  scryingglass
```

Create writable persistent storage for the application:

```bash
sudo install -d \
  -o scryingglass \
  -g scryingglass \
  -m 0750 \
  /var/lib/scrying-glass
```

Create a protected configuration directory:

```bash
sudo install -d \
  -o root \
  -g scryingglass \
  -m 0750 \
  /etc/scrying-glass
```

## Install the application

Clone the project into `/opt`:

```bash
sudo git clone https://github.com/dajomas/scrying-glass.git \
  /opt/scrying-glass

cd /opt/scrying-glass
sudo git checkout features/development
```

Create a virtual environment and install dependencies:

```bash
sudo python3.14 -m venv /opt/scrying-glass/.venv

sudo /opt/scrying-glass/.venv/bin/python -m pip install --upgrade pip
sudo /opt/scrying-glass/.venv/bin/python -m pip install \
  "fastapi>=0.115" \
  "uvicorn[standard]>=0.30" \
  "PyYAML>=6.0" \
  python-multipart
```

Make the application checkout owned by root so the service account cannot modify executable code:

```bash
sudo chown -R root:root /opt/scrying-glass
sudo chmod -R a=rX,u+w /opt/scrying-glass
```

## Create the configuration

Copy the example configuration:

```bash
sudo cp /opt/scrying-glass/config.example.yaml \
  /etc/scrying-glass/config.yaml
```

Edit the configuration:

```bash
sudo editor /etc/scrying-glass/config.yaml
```

Use this as a starting point:

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
  background: "radial-gradient(circle at 50% 15%, #16273d, #080b14 70%)"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  default_monster_color: "#842029"
  default_character_color: "#1f4e79"
  dndbeyond_image_lookup: true
```

Restrict the configuration because it contains login credentials:

```bash
sudo chown root:scryingglass /etc/scrying-glass/config.yaml
sudo chmod 0640 /etc/scrying-glass/config.yaml
```

The service can read the file through the `scryingglass` group but cannot modify it.

### Use scrypt password hashes

Plaintext passwords work, but scrypt hashes are preferable. Generate one from the application directory:

```bash
cd /opt/scrying-glass
sudo /opt/scrying-glass/.venv/bin/python -c \
  'from scrying_glass_server import password_hash; print(password_hash("replace-me"))'
```

Use the emitted `scrypt$...` value as the configured password.

## Validate before systemd

Check that the Python source compiles:

```bash
cd /opt/scrying-glass
sudo /opt/scrying-glass/.venv/bin/python -m py_compile \
  scrying_glass_server.py \
  admin_html.py \
  client_html.py \
  login_html.py
```

No output means compilation succeeded.

You may also test-run it temporarily:

```bash
sudo -u scryingglass \
  /opt/scrying-glass/.venv/bin/python \
  /opt/scrying-glass/scrying_glass_server.py \
  --config /etc/scrying-glass/config.yaml
```

Stop the test with `Ctrl+C` after confirming both ports are listening.

## Create the systemd service

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

### Hardening explanation

| Setting | Effect |
|---|---|
| `User` / `Group` | Runs the application without root privileges |
| `UMask=0027` | New files are not readable by other users by default |
| `NoNewPrivileges=true` | Prevents gaining extra Linux privileges through execution |
| `PrivateTmp=true` | Gives the service an isolated temporary directory |
| `ProtectHome=true` | Blocks access to normal user home directories |
| `ProtectSystem=strict` | Makes most host paths read-only to the service |
| `ReadWritePaths=/var/lib/scrying-glass` | Allows only the expected persistent data location to be written |
| `CapabilityBoundingSet=` | Removes Linux capabilities not needed by the service |

The service retains network access for Admin/Client HTTP traffic, WebSockets, and optional D&D Beyond image lookup.

## Start the service

Load the new unit and start it now and at future boots:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now scrying-glass.service
```

Check status:

```bash
sudo systemctl status scrying-glass.service
```

View live logs:

```bash
sudo journalctl -u scrying-glass.service -f
```

Open:

```text
http://SERVER:3000/
http://SERVER:4000/display
```

## Firewall access

If a firewall is active, allow the application ports on the trusted LAN only.

For firewalld, for example:

```bash
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=4000/tcp
sudo firewall-cmd --reload
```

Do not expose the default HTTP ports to the public internet without a reverse proxy, HTTPS, and access restrictions.

## Verify the service

Confirm that the process runs as the non-root account:

```bash
ps -eo user,pid,cmd | grep scrying_glass_server.py
```

Confirm persistent directories are writable by that account:

```bash
sudo ls -la /var/lib/scrying-glass
sudo ls -la /var/lib/scrying-glass/uploads
sudo ls -la /var/lib/scrying-glass/setups
sudo ls -la /var/lib/scrying-glass/campaigns.json
```

Each campaign has its own folder under `setups/`. The first start creates `campaigns.json` and a `default` campaign folder.

If saving setups or uploading images fails with a permission error:

```bash
sudo chown -R scryingglass:scryingglass /var/lib/scrying-glass
sudo chmod -R u=rwX,g=rX,o= /var/lib/scrying-glass
sudo systemctl restart scrying-glass.service
```

## Upgrade procedure

Back up persistent data before upgrading:

```bash
sudo tar -C /var/lib -czf \
  /root/scrying-glass-backup-$(date +%F).tar.gz \
  scrying-glass
```

Update code and dependencies:

```bash
cd /opt/scrying-glass
sudo git fetch --all --prune
sudo git checkout features/development
sudo git pull --ff-only

sudo /opt/scrying-glass/.venv/bin/python -m pip install \
  "fastapi>=0.115" \
  "uvicorn[standard]>=0.30" \
  "PyYAML>=6.0" \
  python-multipart

sudo /opt/scrying-glass/.venv/bin/python -m py_compile \
  scrying_glass_server.py \
  admin_html.py \
  client_html.py \
  login_html.py

sudo systemctl restart scrying-glass.service
sudo systemctl status scrying-glass.service
```

The working encounter, campaigns, saved setups, Activity Log, and uploads remain intact because they live in `/var/lib/scrying-glass`, outside the Git checkout.

### Upgrading to the campaign version

The first start after upgrading from a version without campaigns migrates existing data automatically:

- Every setup in `/var/lib/scrying-glass/setups/*.json` is moved into `/var/lib/scrying-glass/setups/default/`.
- A `Default` campaign is registered in `/var/lib/scrying-glass/campaigns.json`.

The journal shows which setups were moved:

```bash
sudo journalctl -u scrying-glass.service -b | grep 'unassigned battle setup'
```

The migration only needs write access to `/var/lib/scrying-glass`, which `ReadWritePaths` already grants. Make the backup above before the first start. To roll back to a version without campaigns, restore that backup; the old version does not read `setups/<campaign>/` folders.

## Migrating from Monster Display

Earlier versions of this guide installed the application as Monster Display, with `/opt/monster-display`, `/etc/monster-display`, `/var/lib/monster-display`, the `monsterdisplay` account, and `monster-display.service`. Follow these steps once to move such an installation to the Scrying Glass names used in this guide.

1. Stop and disable the old service, and make a backup:

   ```bash
   sudo systemctl disable --now monster-display.service
   sudo tar -C /var/lib -czf /root/monster-display-backup-$(date +%F).tar.gz monster-display
   ```

2. Rename the service account and its group. This keeps the same UID/GID, so file ownership stays valid:

   ```bash
   sudo usermod -l scryingglass -d /var/lib/scrying-glass monsterdisplay
   sudo groupmod -n scryingglass monsterdisplay
   ```

3. Move the directories:

   ```bash
   sudo mv /opt/monster-display /opt/scrying-glass
   sudo mv /etc/monster-display /etc/scrying-glass
   sudo mv /var/lib/monster-display /var/lib/scrying-glass
   ```

4. Point the checkout at the renamed repository and update the code, as in [Upgrade procedure](#upgrade-procedure):

   ```bash
   cd /opt/scrying-glass
   sudo git remote set-url origin https://github.com/dajomas/scrying-glass.git
   sudo git pull --ff-only
   ```

5. In `/etc/scrying-glass/config.yaml`, change `storage_dir` to `/var/lib/scrying-glass`:

   ```bash
   sudo sed -i 's#/var/lib/monster-display#/var/lib/scrying-glass#' /etc/scrying-glass/config.yaml
   ```

6. Create `/etc/systemd/system/scrying-glass.service` as shown in [Create the systemd service](#create-the-systemd-service), then remove the old unit and start the new one:

   ```bash
   sudo rm /etc/systemd/system/monster-display.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now scrying-glass.service
   sudo systemctl status scrying-glass.service
   ```

Campaigns, setups, uploads, and the working encounter move with `/var/lib/scrying-glass`. Everyone signs in again once, because the session cookie names changed.

## Routine commands

```bash
# Service state
sudo systemctl status scrying-glass.service

# Start, stop, restart
sudo systemctl start scrying-glass.service
sudo systemctl stop scrying-glass.service
sudo systemctl restart scrying-glass.service

# Follow logs
sudo journalctl -u scrying-glass.service -f

# Logs from the current boot
sudo journalctl -u scrying-glass.service -b

# Verify listening sockets
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
```

## Troubleshooting

### Service will not start

Review the last logs:

```bash
sudo journalctl -u scrying-glass.service -n 100 --no-pager
```

Common causes:

- Python 3.14 is absent or the virtual-environment path is incorrect.
- A dependency was not installed in `/opt/scrying-glass/.venv`.
- `config.yaml` has invalid YAML.
- `/var/lib/scrying-glass/setups/` or `campaigns.json` is not writable, so the startup campaign migration fails.
- The service account cannot read `/etc/scrying-glass/config.yaml`.
- Port 3000 or 4000 is already in use.

### Service cannot write state, campaigns, or uploads

The service must own `/var/lib/scrying-glass`:

```bash
sudo chown -R scryingglass:scryingglass /var/lib/scrying-glass
```

Do not set `storage_dir` to a location outside `ReadWritePaths` unless you also update the systemd unit.

### Browser shows old page code

The Admin and Client HTML are loaded from the Python modules. After a service restart, hard-refresh the browser:

- Linux/Windows: `Ctrl+Shift+R`
- macOS: `Cmd+Shift+R`

### Admin or Client cannot log in

Confirm the configured users and passwords. After a service restart, sessions are cleared and users must sign in again. Admin and Client use different session cookies, so both can be used in the same browser.

## Internet-exposure warning

Scrying Glass is designed for a trusted local network. If remote access is necessary:

1. Put an HTTPS reverse proxy in front of the application.
2. Bind application ports to localhost or restrict them using firewall rules.
3. Use a VPN or strong network access controls for the Admin service.
4. Use scrypt password hashes and protect `/etc/scrying-glass/config.yaml`.
5. Run only one Scrying Glass service instance per storage directory.
