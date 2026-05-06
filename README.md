# Home Dashboard CRT

Raspberry Pi → CRT dashboard for Home Assistant, Google Calendar, headlines and small "fun" widgets (compact UI for 10.2" CRT).

## Quick features
- Local weather (proxied from Home Assistant)
- Google Calendar / calendar events (via HA or ICS)
- Headlines (RSS / NewsAPI) — keep 2–4 items for small screen
- Kiosk mode in Chromium (24/7)

## One-line installer (recommended on the Pi)
Replace `USERNAME/REPO` with your GitHub repo (or use the provided one):

```bash
wget -qO- https://raw.githubusercontent.com/USERNAME/REPO/main/install_pi.sh | sudo bash
```

## Manual install (clone & installer)
```bash
sudo git clone https://github.com/USERNAME/REPO.git /opt/home_dashboard_crt
cd /opt/home_dashboard_crt
sudo ./install_pi.sh
```

## Edit configuration
After the installer runs, edit the generated `config.json` (contains your Home Assistant token):

```bash
sudo -u pi nano /opt/home_dashboard_crt/config.json
```

Keep `config.json` private — it is excluded by `.gitignore` by default.

## Run server (manual)
Activate the venv and run the server for debugging:

```bash
/opt/home_dashboard_crt/venv/bin/python3 /opt/home_dashboard_crt/server.py
```

## Systemd (installed by the installer)
The installer will install and enable `home_dashboard.service` and `home_dashboard_kiosk.service` (if available). Manage them with:

```bash
sudo systemctl restart home_dashboard.service
sudo systemctl restart home_dashboard_kiosk.service
sudo systemctl enable --now home_dashboard.service home_dashboard_kiosk.service
```

## Pushing this repo to GitHub
If you want me to push the current project to GitHub, tell me:
- GitHub repo (USERNAME/REPO)
- Whether to use SSH or HTTPS
- Confirm you allow me to run `git push` from this machine (requires your auth already configured)

If you prefer to push yourself, run these commands locally:

SSH (recommended)
```bash
git init
git add .
git commit -m "Initial commit: Home Dashboard CRT"
git branch -M main
git remote add origin git@github.com:USERNAME/REPO.git
git push -u origin main
```

HTTPS (you will be prompted for credentials or PAT)
```bash
git init
git add .
git commit -m "Initial commit: Home Dashboard CRT"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

## Notes
- Do not commit `config.json`. The installer creates `config.json` from `config.example.json` and sets permissions to `600`.
- Statista content is often license-restricted — prefer RSS or properly licensed sources.

## Next steps I can do for you
- Push this repo to a new GitHub repository (if you provide repo name and allow push).  
- Improve UI styling for CRT appearance.  
- Add more robust HA/calendar parsing or tests.

