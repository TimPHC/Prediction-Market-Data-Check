#!/usr/bin/env python3
"""
Polymarket Volume Data Fetcher
Fetches real-time volume data from Polymarket Gamma API
"""

import json
import urllib.request
import ssl
from datetime import datetime

API_URL = "https://gamma-api.polymarket.com/markets"

def fetch_all_markets():
    """Fetch all active markets from Gamma API"""
    all_markets = []
    offset = 0
    limit = 100
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    while True:
        url = f"{API_URL}?limit={limit}&offset={offset}&active=true"
        print(f"Fetching: offset={offset}")
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json'
            })
            with urllib.request.urlopen(req, timeout=60, context=ctx) as response:
                data = json.loads(response.read().decode())
                if not data:
                    break
                all_markets.extend(data)
                if len(data) < limit:
                    break
                offset += limit
        except Exception as e:
            print(f"Error: {e}")
            break

    print(f"Total markets: {len(all_markets)}")
    return all_markets

def calculate_volume(markets):
    """Calculate aggregated volume metrics"""
    v24hr = v1wk = v1mo = 0
    
    for m in markets:
        try:
            v24hr += float(m.get('volume24hr', 0) or 0)
            v1wk += float(m.get('volume1wk', 0) or 0)
            v1mo += float(m.get('volume1mo', 0) or 0)
        except:
            continue
    
    return {'volume_24hr': v24hr, 'volume_1wk': v1wk, 'volume_1mo': v1mo}

def main():
    print("Fetching Polymarket data...")
    markets = fetch_all_markets()
    
    if not markets:
        print("ERROR: No data")
        return
    
    metrics = calculate_volume(markets)
    metrics['last_updated'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    metrics['markets_count'] = len(markets)
    
    print(f"24h: ${metrics['volume_24hr']:,.0f}")
    print(f"7d:  ${metrics['volume_1wk']:,.0f}")
    print(f"30d: ${metrics['volume_1mo']:,.0f}")
    
    with open('polymarket/data.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    print("Saved to polymarket/data.json")

if __name__ == "__main__":
    main()
