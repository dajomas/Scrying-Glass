# Deploy Scrying Glass with systemd

This guide deploys Scrying Glass as a persistent `systemd` service running under a dedicated non-root Linux account. Keep code, configuration, and writable encounter data separate so upgrades do not overwrite campaigns, character rosters, battle setups, state, or uploaded images.

## Prerequisites

- Linux host using `systemd`.
- Python **3.14** or newer.
- Git, if cloning the repository.
- A sudo-capable account.
- Firewall access to TCP 3000 and TCP 4000 for trusted LAN users.

## Deployment layout

```text
/opt/scrying-glass/                 Application code and virtual environment
├── .venv/
├── scrying_glass_server.py
├── admin_html.py
├── client_html.py
├── login_html.py
└── static/

/etc/scrying-glass/
└── config.yaml

/var/lib/scrying-glass/
├── state.json
├── campaigns.json
├── characters/
│   └── <campaign-slug>.json
├── uploads/
└── setups/
    └── <campaign-slug>/<setup-name>.json
```

Do not use a directory inside the Git checkout as `storage_dir`.

## Create service account and directories

```bash
sudo useradd --system --user-group \
  --home-dir /var/lib/scrying-glass \
  --create-home --shell /usr/sbin/nologin scryingglass

sudo install -d -o scryingglass -g scryingglass -m 0750 /var/lib/scrying-glass
sudo install -d -o root -g scryingglass -m 0750 /etc/scrying-glass
```

## Install the application

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

The service account should not be able to modify code or static browser assets.

## Configure

```bash
sudo cp /opt/scrying-glass/config.example.yaml /etc/scrying-glass/config.yaml
sudo editor /etc/scrying-glass/config.yaml
sudo chown root:scryingglass /etc/scrying-glass/config.yaml
sudo chmod 0640 /etc/scrying-glass/config.yaml
```

Example:

```yaml
network:
  bind: "0.0.0.0"
  admin_port: 3000
  client_port: 4000

storage_dir: "/var/lib/scrying-glass"

display:
  background: "#080b14"
  dndbeyond_image_lookup: true
```

When `dndbeyond_image_lookup` is enabled, the host needs outbound DNS/HTTPS connectivity. D&D Beyond AC/HP/image lookup is optional; failures must not prevent normal monster entry.

## Validate before service installation

```bash
cd /opt/scrying-glass
sudo /opt/scrying-glass/.venv/bin/python -m py_compile \
  scrying_glass_server.py admin_html.py client_html.py login_html.py
```

Optional foreground test:

```bash
sudo -u scryingglass /opt/scrying-glass/.venv/bin/python \
  /opt/scrying-glass/scrying_glass_server.py \
  --config /etc/scrying-glass/config.yaml
```

## systemd unit

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

`AF_INET` and `AF_INET6` are needed for Admin/Client traffic, WebSockets, and optional D&D Beyond HTTPS lookup.

## Start and verify

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now scrying-glass.service
sudo systemctl status scrying-glass.service
sudo journalctl -u scrying-glass.service -f
```

Verify listeners:

```bash
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
```

If state, campaign roster, setup, or upload writes fail:

```bash
sudo chown -R scryingglass:scryingglass /var/lib/scrying-glass
sudo chmod -R u=rwX,g=rX,o= /var/lib/scrying-glass
sudo systemctl restart scrying-glass.service
```

## Persistence and backup

- Character mutations automatically update the active campaign roster.
- Monster mutations automatically update the loaded saved setup.
- An unsaved encounter remains in `state.json` until explicitly saved.
- Selected replacement images are uploaded only after the edit form's **Save monster** action.

Back up the complete persistent directory before upgrades:

```bash
sudo tar -C /var/lib -czf \
  /root/scrying-glass-backup-$(date +%F).tar.gz \
  scrying-glass
```

This must include `characters/`, `setups/`, `uploads/`, `campaigns.json`, and `state.json`.

## Upgrades

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
```

Deploy matching Python, HTML, JavaScript, and CSS assets. After changing static assets, hard-refresh Admin and Client pages. With Chrome DevTools open, enable Network → **Disable cache** while testing.

## Troubleshooting

- **Service fails:** `sudo journalctl -u scrying-glass.service -n 100 --no-pager`
- **D&D Beyond lookup unavailable:** verify configuration, canonical Monster species spelling, DNS/HTTPS access, and expect best-effort behavior.
- **Browser shows old behavior:** restart the service, verify `/opt/scrying-glass/static/`, and hard-refresh.
- **Writes fail:** confirm `storage_dir` ownership and that `ReadWritePaths` matches it.
