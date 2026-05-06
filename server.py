#!/usr/bin/env python3
"""
Minimal Flask server for Home Dashboard CRT.
Serves static UI and provides simple API endpoints for time, headlines, calendar and weather (proxies Home Assistant when configured).
"""

import os
import json
import time
import threading
from datetime import datetime

from flask import Flask, jsonify
import requests
import feedparser
from ics import Calendar
from dateutil import tz

APP_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(APP_DIR, 'config.json')
DEFAULT_CONFIG_PATH = os.path.join(APP_DIR, 'config.example.json')


def load_config():
    path = CONFIG_PATH if os.path.exists(CONFIG_PATH) else DEFAULT_CONFIG_PATH
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

app = Flask(__name__, static_folder='static')

# Simple in-memory cache
cache = {}
CACHE_LOCK = threading.Lock()


def cache_get(key, ttl=60):
    with CACHE_LOCK:
        item = cache.get(key)
        if item and (time.time() - item['ts'] < ttl):
            return item['value']
    return None


def cache_set(key, value):
    with CACHE_LOCK:
        cache[key] = {'ts': time.time(), 'value': value}


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/config')
def api_config():
    c = dict(config)
    if 'home_assistant' in c:
        c['home_assistant'] = dict(c['home_assistant'])
        c['home_assistant'].pop('token', None)
    return jsonify(c)


@app.route('/api/time')
def api_time():
    tzname = config.get('timezone')
    if tzname:
        now = datetime.now(tz.gettz(tzname))
    else:
        now = datetime.now()
    return jsonify({'iso': now.isoformat(), 'display': now.strftime('%A %d %B %Y %H:%M:%S')})


@app.route('/api/headlines')
def api_headlines():
    minutes = int(config.get('news', {}).get('refresh_minutes', 30))
    ttl = minutes * 60
    cached = cache_get('headlines', ttl)
    if cached:
        return jsonify(cached)
    sources = config.get('news', {}).get('sources', [])
    max_headlines = int(config.get('news', {}).get('max_headlines', 3))
    items = []
    for s in sources:
        if s.get('type') == 'rss' and s.get('url'):
            try:
                feed = feedparser.parse(s.get('url'))
                for e in (feed.entries or [])[:max_headlines]:
                    items.append({
                        'title': e.get('title'),
                        'link': e.get('link'),
                        'summary': (e.get('summary') or '')[:200]
                    })
            except Exception as exc:
                print('rss error', exc)
    items = items[:max_headlines]
    cache_set('headlines', items)
    return jsonify(items)


@app.route('/api/calendar')
def api_calendar():
    cached = cache_get('calendar', 60)
    if cached:
        return jsonify(cached)
    events = []
    ha = config.get('home_assistant', {})
    # Home Assistant calendar entity (best when Google Calendar is integrated into HA)
    if ha.get('url') and ha.get('token') and ha.get('calendar_entity'):
        try:
            headers = {'Authorization': f"Bearer {ha['token']}", 'Content-Type': 'application/json'}
            res = requests.get(f"{ha['url'].rstrip('/')}/api/states/{ha['calendar_entity']}", headers=headers, timeout=10)
            if res.ok:
                data = res.json()
                attrs = data.get('attributes', {})
                if attrs.get('start_time'):
                    events.append({
                        'title': attrs.get('message') or attrs.get('summary') or 'Event',
                        'start': attrs.get('start_time'),
                        'end': attrs.get('end_time'),
                        'all_day': attrs.get('all_day', False)
                    })
        except Exception as exc:
            print('ha calendar error', exc)

    # ICS fallback (public ICS/ICS-export URL)
    if not events and config.get('google_calendar', {}).get('ics_url'):
        try:
            ics_url = config['google_calendar']['ics_url']
            r = requests.get(ics_url, timeout=10)
            if r.ok:
                c = Calendar(r.text)
                for ev in list(c.events)[:10]:
                    events.append({
                        'title': ev.name,
                        'start': ev.begin.isoformat() if ev.begin else None,
                        'end': ev.end.isoformat() if ev.end else None,
                        'description': ev.description
                    })
        except Exception as exc:
            print('ics error', exc)

    cache_set('calendar', events)
    return jsonify(events)


@app.route('/api/weather')
def api_weather():
    cached = cache_get('weather', 60)
    if cached:
        return jsonify(cached)
    ha = config.get('home_assistant', {})
    if ha.get('url') and ha.get('token'):
        try:
            headers = {'Authorization': f"Bearer {ha['token']}", 'Content-Type': 'application/json'}
            res = requests.get(f"{ha['url'].rstrip('/')}/api/states", headers=headers, timeout=10)
            if res.ok:
                states = res.json()
                weather = None
                for s in states:
                    if s.get('entity_id', '').startswith('weather.'):
                        weather = s
                        break
                if weather:
                    payload = {
                        'entity_id': weather.get('entity_id'),
                        'state': weather.get('state'),
                        'attributes': weather.get('attributes')
                    }
                    cache_set('weather', payload)
                    return jsonify(payload)
        except Exception as exc:
            print('weather error', exc)
    return jsonify({})


if __name__ == '__main__':
    port = int(config.get('kiosk', {}).get('port', 5000))
    app.run(host='0.0.0.0', port=port)
