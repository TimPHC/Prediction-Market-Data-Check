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
#!/usr/bin/env python3
            """
            Polymarket Volume Data Fetcher using Dune Analytics API
            Fetches real on-chain volume data from Dune Analytics queries.
            Data source: Polygon blockchain transactions (same as Dune Dashboard)
            """
            
            import json
            import os
            import urllib.request
            from datetime import datetime
            
            DUNE_API_KEY = os.environ.get('DUNE_API_KEY')
            
            # Query IDs from Dune Analytics (Polymarket volume queries)
            DAILY_VOLUME_QUERY_ID = 3343108   # Daily volume query
            MONTHLY_VOLUME_QUERY_ID = 2683517  # Monthly volume query
            
            
            def fetch_dune_query(query_id):
                    """Fetch latest results from a Dune Analytics query"""
                    url = f"https://api.dune.com/api/v1/query/{query_id}/results"
                    headers = {
                                'X-Dune-API-Key': DUNE_API_KEY,
                                'Content-Type': 'application/json'
                    }
                
                req = urllib.request.Request(url, headers=headers)
            
                try:
                            with urllib.request.urlopen(req, timeout=60) as response:
                                            data = json.loads(response.read().decode())
                                            return data
                except Exception as e:
                            print(f"Error fetching Dune query {query_id}: {e}")
                            return None
                    
            
            def get_volume_data():
                    """Get volume metrics from Dune Analytics"""
                
                print("Fetching daily volume data from Dune...")
                daily_data = fetch_dune_query(DAILY_VOLUME_QUERY_ID)
            
                print("Fetching monthly volume data from Dune...")
                monthly_data = fetch_dune_query(MONTHLY_VOLUME_QUERY_ID)
            
                metrics = {
                            'volume_24hr': 0,
                            'volume_1wk': 0,
                            'volume_1mo': 0,
                            'data_source': 'Dune Analytics (Polygon on-chain)',
                            'query_ids': {
                                            'daily': DAILY_VOLUME_QUERY_ID,
                                            'monthly': MONTHLY_VOLUME_QUERY_ID
                            }
                }
            
                # Parse daily volume
                if daily_data and 'result' in daily_data and 'rows' in daily_data['result']:
                            rows = daily_data['result']['rows']
                            if rows:
                                            sorted_rows = sorted(rows, key=lambda x: x.get('day', x.get('date', '')), reverse=True)
                                            if len(sorted_rows) >= 1:
                                                                metrics['volume_24hr'] = float(sorted_rows[0].get('volume', sorted_rows[0].get('daily_volume', 0)))
                                                            week_volume = sum(float(r.get('volume', r.get('daily_volume', 0))) for r in sorted_rows[:7])
                                            metrics['volume_1wk'] = week_volume
                                            print(f"Daily data: {len(rows)} rows, latest: ${metrics['volume_24hr']:,.0f}")
                                
                        # Parse monthly volume
                if monthly_data and 'result' in monthly_data and 'rows' in monthly_data['result']:
                            rows = monthly_data['result']['rows']
                            if rows:
                                            sorted_rows = sorted(rows, key=lambda x: x.get('month', x.get('date', '')), reverse=True)
                                            if sorted_rows:
                                                                metrics['volume_1mo'] = float(sorted_rows[0].get('volume', sorted_rows[0].get('monthly_volume', 0)))
                                                            print(f"Monthly data: {len(rows)} rows, latest: ${metrics['volume_1mo']:,.0f}")
                                
                        return metrics
            
            
            def main():
                    if not DUNE_API_KEY:
                                print("ERROR: DUNE_API_KEY environment variable not set")
                                return
                        
                    print(f"Using Dune API Key: {DUNE_API_KEY[:8]}...")
                    metrics = get_volume_data()
                    metrics['last_updated'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
                
                print(f"\n=== Polymarket Volume (Dune Analytics) ===")
                print(f"24hr: ${metrics['volume_24hr']:,.0f}")
    print(f"7d:   ${metrics['volume_1wk']:,.0f}")
    print(f"30d:  ${metrics['volume_1mo']:,.0f}")

    with open('polymarket/data.json', 'w') as f:
                json.dump(metrics, f, indent=2)
            print("Saved to polymarket/data.json")


if __name__ == "__main__":
        main()print(f"Error: {e}")
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
