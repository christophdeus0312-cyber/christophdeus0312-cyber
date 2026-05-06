Home Dashboard CRT — Quick setup

1) Generate a config file

Run the interactive script to create `config.json`:

```bash
python3 setup_config.py
```

The script writes `config.json` and sets file permissions to `600` so the token is not world-readable.

2) Notes about fields

- `city`: set to a city name like "Hamburg" or "Eckernförde" (used for local weather lookup).
- `home_assistant.url` and `home_assistant.token`: point to your Home Assistant instance and a long-lived access token.
- `home_assistant.calendar_entity`: use this if your Google Calendar is integrated into HA (preferred).
- `google_calendar.ics_url`: optional public ICS URL if you prefer to fetch calendar directly.
- `news.sources`: prefer RSS feeds for free sources; `newsapi` requires an API key (paid limits).
- `news.max_headlines`: keep this small (2–4) for a 10.2" CRT screen.

3) Running the dashboard (short)

- Install minimal server deps on the Pi:

```bash
sudo apt update
sudo apt install -y python3-pip chromium-browser x11-xserver-utils
pip3 install flask requests
```

- Start your dashboard server (example):

```bash
python3 server.py  # server should load config.json and serve the UI on the configured port
```

- Start kiosk mode in Chromium (replace URL if needed):

```bash
xset s off && xset -dpms && xset s noblank
chromium-browser --kiosk --noerrdialogs --disable-infobars --incognito http://localhost:5000
```

4) About Statista / headlines

Statista content is often licensed; consider using curated RSS feeds or `newsapi.org` with queries like "Statista" or "statistics". For a small CRT screen, keep `news.max_headlines` at 2–4 and use short summaries only.

5) Security

- Keep `config.json` on the Pi and do not commit it to git.
- `chmod 600 config.json` was applied automatically by the setup script.

6) Next steps I can do for you

- Scaffold the small Flask server that reads `config.json` and exposes a safe `/api` proxy for Home Assistant + calendar + headlines.
- Build the frontend HTML/CSS suitable for CRT display and start/auto-restart systemd service files for kiosk mode.

Tell me which of those you'd like next.
