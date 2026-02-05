#!/usr/bin/env python3
"""
Kalshi Volume Data Updater
Fetches latest data from Kalshi public API and updates the dashboard data file.
Runs daily via GitHub Actions.
"""

import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

def fetch_all_markets():
    """Fetch all markets from Kalshi API"""
    markets = []
    cursor = None

    while True:
        params = {"limit": 200, "status": "active"}
        if cursor:
            params["cursor"] = cursor

        try:
            response = requests.get(f"{BASE_URL}/markets", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            markets.extend(data.get("markets", []))
            cursor = data.get("cursor")

            if not cursor:
                break
        except Exception as e:
            print(f"Error fetching markets: {e}")
            break

    return markets

def fetch_recent_trades(days=90):
    """Fetch trades from the last N days"""
    trades = []
    cursor = None
    min_ts = int((datetime.utcnow() - timedelta(days=days)).timestamp() * 1000)

    # Limit to avoid too many API calls
    max_pages = 100
    page = 0

    while page < max_pages:
        params = {"limit": 1000, "min_ts": min_ts}
        if cursor:
            params["cursor"] = cursor

        try:
            response = requests.get(f"{BASE_URL}/markets/trades", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            batch = data.get("trades", [])
            trades.extend(batch)
            cursor = data.get("cursor")

            print(f"Fetched {len(batch)} trades (total: {len(trades)})")

            if not cursor or len(batch) == 0:
                break

            page += 1
        except Exception as e:
            print(f"Error fetching trades: {e}")
            break

    return trades

def aggregate_daily_volume(trades):
    """Aggregate trades into daily volume"""
    daily_volume = defaultdict(float)

    for trade in trades:
        # Parse timestamp
        created_time = trade.get("created_time", "")
        if created_time:
            try:
                dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
                # count is the number of contracts
                count = trade.get("count", 0)
                daily_volume[date_str] += count
            except:
                pass

    return dict(daily_volume)

def aggregate_weekly_volume(daily_data):
    """Aggregate daily volume into weekly"""
    weekly_volume = defaultdict(float)

    for date_str, volume in daily_data.items():
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        # Get Monday of that week
        week_start = dt - timedelta(days=dt.weekday())
        week_str = week_start.strftime("%Y-%m-%d")
        weekly_volume[week_str] += volume

    return dict(weekly_volume)

def calculate_current_metrics(markets):
    """Calculate current metrics from market data"""
    total_volume_24h = sum(m.get("volume_24h", 0) for m in markets)
    total_open_interest = sum(m.get("open_interest", 0) for m in markets)
    total_volume = sum(m.get("volume", 0) for m in markets)

    return {
        "total_volume_24h": total_volume_24h,
        "total_open_interest": total_open_interest,
        "total_volume": total_volume,
        "active_markets": len(markets)
    }

def main():
    print(f"Starting Kalshi data update at {datetime.utcnow().isoformat()}")

    # Fetch current market data
    print("Fetching market data...")
    markets = fetch_all_markets()
    print(f"Fetched {len(markets)} markets")

    # Calculate current metrics
    metrics = calculate_current_metrics(markets)
    print(f"24h Volume: ${metrics['total_volume_24h']:,}")
    print(f"Open Interest: ${metrics['total_open_interest']:,}")

    # Fetch recent trades for historical data
    print("Fetching recent trades...")
    trades = fetch_recent_trades(days=90)
    print(f"Fetched {len(trades)} trades")

    # Aggregate data
    daily_volume = aggregate_daily_volume(trades)
    weekly_volume = aggregate_weekly_volume(daily_volume)

    # Sort by date
    sorted_daily = sorted(daily_volume.items())
    sorted_weekly = sorted(weekly_volume.items())

    # Prepare output
    output = {
        "source": "Kalshi Official API (api.elections.kalshi.com)",
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "update_frequency": "Daily via GitHub Actions",
        "metrics": {
            "volume_24h": metrics["total_volume_24h"],
            "volume_24h_millions": round(metrics["total_volume_24h"] / 1e6, 2),
            "open_interest": metrics["total_open_interest"],
            "open_interest_millions": round(metrics["total_open_interest"] / 1e6, 2),
            "active_markets": metrics["active_markets"],
            "estimated_daily_revenue": round(metrics["total_volume_24h"] * 0.02, 2)
        },
        "daily_data": [
            {
                "date": date,
                "volume": vol,
                "volume_millions": round(vol / 1e6, 2)
            }
            for date, vol in sorted_daily[-90:]  # Last 90 days
        ],
        "weekly_data": [
            {
                "week_start": week,
                "volume": vol,
                "volume_millions": round(vol / 1e6, 2),
                "volume_billions": round(vol / 1e9, 3)
            }
            for week, vol in sorted_weekly[-14:]  # Last 14 weeks
        ]
    }

    # Save to file
    with open("kalshi_volume_data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Data saved to kalshi_volume_data.json")
    print(f"Daily records: {len(output['daily_data'])}")
    print(f"Weekly records: {len(output['weekly_data'])}")

    return output

if __name__ == "__main__":
    main()
