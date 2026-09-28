# Deploy Monster Display with systemd

This page explains how to run Monster Display as a persistent `systemd` service under a dedicated non-root Linux account. The deployment separates application code, credentials/configuration, and writable encounter data so that upgrades do not overwrite saved setups or uploaded images.

See [[Home]] for the project overview, [[User Guide]] for using the Admin and Client Display screens, and [[Technical Documentation]] for architecture and API details.

## What this deployment provides

- Starts Monster Display automatically at boot.
- Runs the application as a dedicated non-root user named `monsterdisplay`.
- Restarts the service after an unexpected failure.
- Keeps configuration in `/etc/monster-display`.
- Keeps current state, saved setups, and image uploads in `/var/lib/monster-display`.
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

Monster Display requires:

```text
fastapi
uvicorn[standard]
PyYAML
python-multipart
```

## Deployment layout

This guide uses the following paths:

```text
/opt/monster-display/                 Application code and virtual environment
├── .venv/
├── monster_display_server.py
├── admin_html.py
├── client_html.py
├── login_html.py
└── config.example.yaml

/etc/monster-display/                 Protected configuration
└── config.yaml

/var/lib/monster-display/             Writable persistent encounter data
├── state.json
├── uploads/
└── setups/
```

Do not put the live `storage_dir` inside the Git checkout. The persistent directory must survive Git pulls, release replacements, and application upgrades.

## Create the service account

Create a system account without an interactive shell:

```bash
sudo useradd \
  --system \
  --user-group \
  --home-dir /var/lib/monster-display \
  --create-home \
  --shell /usr/sbin/nologin \
  monsterdisplay
```

Create writable persistent storage for the application:

```bash
sudo install -d \
  -o monsterdisplay \
  -g monsterdisplay \
  -m 0750 \
  /var/lib/monster-display
```

Create a protected configuration directory:

```bash
sudo install -d \
  -o root \
  -g monsterdisplay \
  -m 0750 \
  /etc/monster-display
```

## Install the application

Clone the project into `/opt`:

```bash
sudo git clone https://github.com/dajomas/monster_display_server.git \
  /opt/monster-display

cd /opt/monster-display
sudo git checkout features/development
```

Create a virtual environment and install dependencies:

```bash
sudo python3.14 -m venv /opt/monster-display/.venv

sudo /opt/monster-display/.venv/bin/python -m pip install --upgrade pip
sudo /opt/monster-display/.venv/bin/python -m pip install \
  "fastapi>=0.115" \
  "uvicorn[standard]>=0.30" \
  "PyYAML>=6.0" \
  python-multipart
```

Make the application checkout owned by root so the service account cannot modify executable code:

```bash
sudo chown -R root:root /opt/monster-display
sudo chmod -R a=rX,u+w /opt/monster-display
```

## Create the configuration

Copy the example configuration:

```bash
sudo cp /opt/monster-display/config.example.yaml \
  /etc/monster-display/config.yaml
```

Edit the configuration:

```bash
sudo editor /etc/monster-display/config.yaml
```

Use this as a starting point:

```yaml
network:
  bind: "0.0.0.0"
  admin_port: 3000
  client_port: 4000

storage_dir: "/var/lib/monster-display"

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
sudo chown root:monsterdisplay /etc/monster-display/config.yaml
sudo chmod 0640 /etc/monster-display/config.yaml
```

The service can read the file through the `monsterdisplay` group but cannot modify it.

### Use scrypt password hashes

Plaintext passwords work, but scrypt hashes are preferable. Generate one from the application directory:

```bash
cd /opt/monster-display
sudo /opt/monster-display/.venv/bin/python -c \
  'from monster_display_server import password_hash; print(password_hash("replace-me"))'
```

Use the emitted `scrypt$...` value as the configured password.

## Validate before systemd

Check that the Python source compiles:

```bash
cd /opt/monster-display
sudo /opt/monster-display/.venv/bin/python -m py_compile \
  monster_display_server.py \
  admin_html.py \
  client_html.py \
  login_html.py
```

No output means compilation succeeded.

You may also test-run it temporarily:

```bash
sudo -u monsterdisplay \
  /opt/monster-display/.venv/bin/python \
  /opt/monster-display/monster_display_server.py \
  --config /etc/monster-display/config.yaml
```

Stop the test with `Ctrl+C` after confirming both ports are listening.

## Create the systemd service

Create `/etc/systemd/system/monster-display.service`:

```ini
[Unit]
Description=Monster Display tabletop battle display
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=monsterdisplay
Group=monsterdisplay
WorkingDirectory=/opt/monster-display

ExecStart=/opt/monster-display/.venv/bin/python /opt/monster-display/monster_display_server.py --config /etc/monster-display/config.yaml

Restart=on-failure
RestartSec=5

UMask=0027

NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
ReadWritePaths=/var/lib/monster-display

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
| `ReadWritePaths=/var/lib/monster-display` | Allows only the expected persistent data location to be written |
| `CapabilityBoundingSet=` | Removes Linux capabilities not needed by the service |

The service retains network access for Admin/Client HTTP traffic, WebSockets, and optional D&D Beyond image lookup.

## Start the service

Load the new unit and start it now and at future boots:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now monster-display.service
```

Check status:

```bash
sudo systemctl status monster-display.service
```

View live logs:

```bash
sudo journalctl -u monster-display.service -f
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
ps -eo user,pid,cmd | grep monster_display_server.py
```

Confirm persistent directories are writable by that account:

```bash
sudo ls -la /var/lib/monster-display
sudo ls -la /var/lib/monster-display/uploads
sudo ls -la /var/lib/monster-display/setups
```

If saving setups or uploading images fails with a permission error:

```bash
sudo chown -R monsterdisplay:monsterdisplay /var/lib/monster-display
sudo chmod -R u=rwX,g=rX,o= /var/lib/monster-display
sudo systemctl restart monster-display.service
```

## Upgrade procedure

Back up persistent data before upgrading:

```bash
sudo tar -C /var/lib -czf \
  /root/monster-display-backup-$(date +%F).tar.gz \
  monster-display
```

Update code and dependencies:

```bash
cd /opt/monster-display
sudo git fetch --all --prune
sudo git checkout features/development
sudo git pull --ff-only

sudo /opt/monster-display/.venv/bin/python -m pip install \
  "fastapi>=0.115" \
  "uvicorn[standard]>=0.30" \
  "PyYAML>=6.0" \
  python-multipart

sudo /opt/monster-display/.venv/bin/python -m py_compile \
  monster_display_server.py \
  admin_html.py \
  client_html.py \
  login_html.py

sudo systemctl restart monster-display.service
sudo systemctl status monster-display.service
```

The working encounter, saved setups, Activity Log, and uploads remain intact because they live in `/var/lib/monster-display`, outside the Git checkout.

## Routine commands

```bash
# Service state
sudo systemctl status monster-display.service

# Start, stop, restart
sudo systemctl start monster-display.service
sudo systemctl stop monster-display.service
sudo systemctl restart monster-display.service

# Follow logs
sudo journalctl -u monster-display.service -f

# Logs from the current boot
sudo journalctl -u monster-display.service -b

# Verify listening sockets
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
```

## Troubleshooting

### Service will not start

Review the last logs:

```bash
sudo journalctl -u monster-display.service -n 100 --no-pager
```

Common causes:

- Python 3.14 is absent or the virtual-environment path is incorrect.
- A dependency was not installed in `/opt/monster-display/.venv`.
- `config.yaml` has invalid YAML.
- The service account cannot read `/etc/monster-display/config.yaml`.
- Port 3000 or 4000 is already in use.

### Service cannot write state or uploads

The service must own `/var/lib/monster-display`:

```bash
sudo chown -R monsterdisplay:monsterdisplay /var/lib/monster-display
```

Do not set `storage_dir` to a location outside `ReadWritePaths` unless you also update the systemd unit.

### Browser shows old page code

The Admin and Client HTML are loaded from the Python modules. After a service restart, hard-refresh the browser:

- Linux/Windows: `Ctrl+Shift+R`
- macOS: `Cmd+Shift+R`

### Admin or Client cannot log in

Confirm the configured users and passwords. After a service restart, sessions are cleared and users must sign in again. Admin and Client use different session cookies, so both can be used in the same browser.

## Internet-exposure warning

Monster Display is designed for a trusted local network. If remote access is necessary:

1. Put an HTTPS reverse proxy in front of the application.
2. Bind application ports to localhost or restrict them using firewall rules.
3. Use a VPN or strong network access controls for the Admin service.
4. Use scrypt password hashes and protect `/etc/monster-display/config.yaml`.
5. Run only one Monster Display service instance per storage directory.
