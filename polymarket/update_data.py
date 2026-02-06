#!/usr/bin/env python3
"""
Polymarket Volume Data Fetcher using Dune Analytics API
"""

import json
import os
import urllib.request
from datetime import datetime

DUNE_API_KEY = os.environ.get('DUNE_API_KEY')
DAILY_VOLUME_QUERY_ID = 3343108
MONTHLY_VOLUME_QUERY_ID = 2683517

def fetch_dune_query(query_id):
    url = f"https://api.dune.com/api/v1/query/{query_id}/results"
    headers = {'X-Dune-API-Key': DUNE_API_KEY, 'Content-Type': 'application/json'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_volume_data():
    daily = fetch_dune_query(DAILY_VOLUME_QUERY_ID)
    monthly = fetch_dune_query(MONTHLY_VOLUME_QUERY_ID)
    metrics = {'volume_24hr': 0, 'volume_1wk': 0, 'volume_1mo': 0, 
               'data_source': 'Dune Analytics', 'query_ids': {'daily': DAILY_VOLUME_QUERY_ID, 'monthly': MONTHLY_VOLUME_QUERY_ID}}
    if daily and 'result' in daily and 'rows' in daily['result']:
        rows = sorted(daily['result']['rows'], key=lambda x: x.get('day', ''), reverse=True)
        if rows:
            metrics['volume_24hr'] = float(rows[0].get('volume', 0))
            metrics['volume_1wk'] = sum(float(r.get('volume', 0)) for r in rows[:7])
    if monthly and 'result' in monthly and 'rows' in monthly['result']:
        rows = sorted(monthly['result']['rows'], key=lambda x: x.get('month', ''), reverse=True)
        if rows:
            metrics['volume_1mo'] = float(rows[0].get('volume', 0))
    return metrics

def main():
    if not DUNE_API_KEY:
        print("ERROR: DUNE_API_KEY not set")
        return
    metrics = get_volume_data()
    metrics['last_updated'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    print(f"24hr: ${metrics['volume_24hr']:,.0f}, 7d: ${metrics['volume_1wk']:,.0f}, 30d: ${metrics['volume_1mo']:,.0f}")
    with open('polymarket/data.json', 'w') as f:
        json.dump(metrics, f, indent=2)

if __name__ == "__main__":
    main()
