# Deploy Scrying Glass with systemd

Deploy Scrying Glass as a persistent non-root `systemd` service. Keep application code, configuration, and writable data separate so upgrades preserve campaigns, character rosters, battle setups, working state, and uploads.

## Layout

```text
/opt/scrying-glass/                 Application code
/etc/scrying-glass/config.yaml      Protected configuration
/var/lib/scrying-glass/             Persistent data
├── state.json
├── campaigns.json
├── characters/<campaign-slug>.json
├── uploads/
└── setups/<campaign-slug>/<setup>.json
```

Back up the complete persistent directory. Character rosters, setup snapshots, runtime state, activity logs, and uploads are all required for a complete restore.

## Install

```bash
sudo useradd --system --user-group --home-dir /var/lib/scrying-glass   --create-home --shell /usr/sbin/nologin scryingglass
sudo install -d -o scryingglass -g scryingglass -m 0750 /var/lib/scrying-glass
sudo install -d -o root -g scryingglass -m 0750 /etc/scrying-glass

sudo git clone https://github.com/dajomas/scrying-glass.git /opt/scrying-glass
sudo python3.14 -m venv /opt/scrying-glass/.venv
sudo /opt/scrying-glass/.venv/bin/python -m pip install   "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

## Configuration

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

`dndbeyond_image_lookup` allows optional outbound D&D Beyond lookup for dedicated monster images and AC/HP suggestions. The service needs DNS and HTTPS connectivity when enabled. Lookup failures must not block manual monster creation; set it to `false` for offline or restricted deployments.

## Service unit

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

`AF_INET` and `AF_INET6` permit Admin/Client traffic, WebSockets, and optional D&D Beyond HTTPS requests.

## Start and verify

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now scrying-glass.service
sudo systemctl status scrying-glass.service
sudo journalctl -u scrying-glass.service -f
```

If saving campaigns, setups, or uploads fails:

```bash
sudo chown -R scryingglass:scryingglass /var/lib/scrying-glass
sudo chmod -R u=rwX,g=rX,o= /var/lib/scrying-glass
sudo systemctl restart scrying-glass.service
```

## Persistence behavior

- Character mutations automatically write `characters/<campaign>.json`.
- Monster mutations automatically update the currently loaded saved setup.
- Unsaved monster encounters remain in `state.json` until explicitly saved as a setup.
- Battle actions may save both character and setup ownership stores.
- A selected replacement image is not uploaded until **Save monster** submits the edit form.

## Backup and upgrades

```bash
sudo tar -C /var/lib -czf /root/scrying-glass-backup-$(date +%F).tar.gz scrying-glass
```

After deployment, validate Python modules and restart:

```bash
cd /opt/scrying-glass
sudo /opt/scrying-glass/.venv/bin/python -m py_compile   scrying_glass_server.py admin_html.py client_html.py login_html.py
sudo systemctl restart scrying-glass.service
```

Deploy matching server, HTML, JavaScript, and CSS files. After static updates, hard-refresh Admin and Client pages; in Chrome DevTools, enable Network → **Disable cache** while testing.

## Troubleshooting

- **No D&D Beyond suggestions:** confirm `dndbeyond_image_lookup: true`, outbound DNS/HTTPS, and canonical Monster species spelling.
- **Setup, roster, or upload writes fail:** verify service ownership of `storage_dir` and `ReadWritePaths` in the unit.
- **Browser runs old behavior:** verify the new files under `/opt/scrying-glass/static/`, restart the service, and hard-refresh.
