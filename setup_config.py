#!/usr/bin/env python3
"""
Interactive setup script for the Home Dashboard CRT project.
Generates `config.json` in the current directory from prompted values.
Run: python3 setup_config.py
"""

import json
import os
import getpass


def input_default(prompt, default):
    try:
        s = input(f"{prompt} [{default}]: ").strip()
    except EOFError:
        s = ""
    return s if s else default


def parse_csv(s):
    return [x.strip() for x in s.split(",") if x.strip()]


def main():
    print("Home Dashboard CRT — interactive setup\n")
    out_path = "config.json"
    if os.path.exists(out_path):
        overwrite = input_default(f"{out_path} exists. Overwrite? (y/n)", "n")
        if overwrite.lower() != "y":
            print("Aborted. No changes made.")
            return

    city = input_default("City (for local weather)", "Hamburg")
    timezone = input_default("Timezone (TZ)", "Europe/Berlin")

    ha_url = input_default("Home Assistant URL", "http://homeassistant.local:8123")
    print("Create a long-lived access token in Home Assistant (Profile → Long-Lived Access Tokens).")
    ha_token = getpass.getpass("Home Assistant token (hidden): ").strip()
    if not ha_token:
        print("Warning: token left empty — Home Assistant-powered features will not work.")

    ha_calendar = input_default("Home Assistant calendar entity id (leave blank if using ICS URL)", "")
    ics_url = input_default("Google Calendar ICS/public URL (optional)", "")

    news_choice = input_default("News source type (rss/newsapi/none)", "rss").lower()
    sources = []
    if news_choice == "rss":
        default_feeds = "https://rss.example.com/feed.xml"
        feeds = input_default("Comma-separated RSS feed URLs", default_feeds)
        for url in parse_csv(feeds):
            sources.append({"type": "rss", "url": url})
    elif news_choice == "newsapi":
        api_key = input_default("NewsAPI.org API key (leave empty to skip)", "")
        query = input_default("NewsAPI query keywords (e.g., Statista OR statistics)", "Statista")
        sources.append({"type": "newsapi", "api_key": api_key, "query": query})
    else:
        print("No news configured.")

    max_headlines = int(input_default("Maximum headlines on screen", "3"))
    refresh_minutes = int(input_default("News refresh (minutes)", "30"))

    fun_widget = input_default("Fun widget (headlines/quotes/photos)", "headlines")

    config = {
        "city": city,
        "timezone": timezone,
        "home_assistant": {
            "url": ha_url,
            "token": ha_token,
            "calendar_entity": ha_calendar
        },
        "google_calendar": {
            "ics_url": ics_url
        },
        "news": {
            "sources": sources,
            "max_headlines": max_headlines,
            "refresh_minutes": refresh_minutes
        },
        "fun": {
            "widget": fun_widget,
            "max_items": max_headlines
        },
        "kiosk": {
            "port": 5000,
            "refresh_interval_seconds": 60
        },
        "display": {
            "theme": "crt",
            "crt_scanlines": True,
            "font_scale": 1.0
        }
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    os.chmod(out_path, 0o600)
    print(f"\nWrote {out_path} (permissions set to 600). Keep your token secret.")
    print("Next: copy config.json to the Pi project folder and start the dashboard server.")


if __name__ == "__main__":
    main()
