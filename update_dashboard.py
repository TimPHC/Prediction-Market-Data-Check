#!/usr/bin/env python3
"""
Updates the dashboard HTML with latest data from kalshi_volume_data.json
"""

import json
from datetime import datetime

def generate_dashboard_html(data):
    """Generate the complete dashboard HTML with updated data"""

    # Extract metrics
    metrics = data.get("metrics", {})
    daily_data = data.get("daily_data", [])
    weekly_data = data.get("weekly_data", [])
    last_updated = data.get("last_updated", datetime.utcnow().strftime("%Y-%m-%d"))

    # Format data for JavaScript
    daily_js = json.dumps([{"date": d["date"], "volume": d["volume_millions"]} for d in daily_data])
    weekly_js = json.dumps([{"week": w["week_start"], "volume": w["volume_billions"]} for w in weekly_data])

    # Get volume metrics for JavaScript
    daily_volume_24h = metrics.get("volume_24h_millions", 0)
    latest_week_volume_b = weekly_data[-1]["volume_billions"] if weekly_data else 0

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kalshi Notional Volume Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .header p {{ color: #888; font-size: 1.1em; }}
        .auto-update-badge {{
            display: inline-block;
            background: linear-gradient(90deg, #4ade80, #22c55e);
            color: #000;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            margin-top: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .metric-card .label {{ color: #888; font-size: 0.9em; margin-bottom: 8px; }}
        .metric-card .value {{ font-size: 1.8em; font-weight: bold; color: #00d4ff; }}
        .metric-card .subvalue {{ font-size: 0.85em; color: #4ade80; margin-top: 5px; }}
        .chart-container {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        .chart-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .chart-title {{ font-size: 1.3em; color: #fff; }}
        .chart-subtitle {{ color: #888; font-size: 0.9em; }}
        .chart-wrapper {{ position: relative; height: 350px; }}
        .notes {{
            background: rgba(124, 58, 237, 0.1);
            border: 1px solid rgba(124, 58, 237, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }}
        .notes h3 {{ color: #7c3aed; margin-bottom: 10px; }}
        .notes ul {{ margin-left: 20px; color: #bbb; }}
        .notes li {{ margin-bottom: 8px; }}
        .notes code {{
            background: rgba(255,255,255,0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .fee-highlight {{ color: #4ade80; font-weight: bold; }}

        /* Fee Input Styles */
        .fee-input-card {{
            background: rgba(74, 222, 128, 0.1) !important;
            border: 2px solid rgba(74, 222, 128, 0.4) !important;
        }}
        .fee-input-wrapper {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 10px 0;
        }}
        .fee-prefix {{
            font-size: 1.5em;
            font-weight: bold;
            color: #4ade80;
            margin-right: 4px;
        }}
        .fee-input {{
            width: 100px;
            padding: 8px 12px;
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(74, 222, 128, 0.5);
            border-radius: 8px;
            color: #4ade80;
            outline: none;
            transition: all 0.2s;
        }}
        .fee-input:focus {{
            border-color: #4ade80;
            box-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
        }}
        .fee-input::-webkit-inner-spin-button,
        .fee-input::-webkit-outer-spin-button {{
            opacity: 1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Kalshi Notional Volume Dashboard</h1>
            <p>Daily & Weekly Trading Volume Analysis | Data Source: Kalshi Official API</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Last Updated: {last_updated}</p>
            <div class="auto-update-badge">🔄 Auto-updates daily via GitHub Actions</div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="label">24h Volume</div>
                <div class="value">${metrics.get("volume_24h_millions", 0):.1f}M</div>
                <div class="subvalue">From Kalshi API</div>
            </div>
            <div class="metric-card">
                <div class="label">Open Interest</div>
                <div class="value">${metrics.get("open_interest_millions", 0):.1f}M</div>
                <div class="subvalue">Current positions</div>
            </div>
            <div class="metric-card">
                <div class="label">Active Markets</div>
                <div class="value">{metrics.get("active_markets", 0):,}</div>
                <div class="subvalue">Trading now</div>
            </div>
            <div class="metric-card fee-input-card">
                <div class="label">HOOD Fee Rate ($/contract)</div>
                <div class="fee-input-wrapper">
                    <span class="fee-prefix">$</span>
                    <input type="number" id="feeRate" value="0.01" min="0.001" max="0.10" step="0.001" class="fee-input">
                </div>
                <div class="subvalue">Adjust to recalculate revenue</div>
            </div>
            <div class="metric-card">
                <div class="label">Est. Daily HOOD PM Revenue</div>
                <div class="value fee-highlight" id="dailyRevenue">$0.00M</div>
                <div class="subvalue">24h Volume × Fee Rate</div>
            </div>
            <div class="metric-card">
                <div class="label">Est. Weekly HOOD PM Revenue</div>
                <div class="value fee-highlight" id="weeklyRevenue">$0.00M</div>
                <div class="subvalue">Latest week</div>
            </div>
            <div class="metric-card">
                <div class="label">Est. Monthly HOOD PM Revenue</div>
                <div class="value fee-highlight" id="monthlyRevenue">$0.0M</div>
                <div class="subvalue">Weekly × 4.3 weeks</div>
            </div>
            <div class="metric-card">
                <div class="label">Est. Annualized HOOD PM Revenue</div>
                <div class="value fee-highlight" id="annualRevenue">$0M</div>
                <div class="subvalue">Monthly × 12</div>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-header">
                <div>
                    <div class="chart-title">📈 Daily Notional Volume (Last 90 Days)</div>
                    <div class="chart-subtitle">Volume = Contracts Traded × $1 Notional</div>
                </div>
            </div>
            <div class="chart-wrapper">
                <canvas id="dailyChart"></canvas>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-header">
                <div>
                    <div class="chart-title">📊 Weekly Notional Volume</div>
                    <div class="chart-subtitle">Aggregated by ISO Week (Monday start)</div>
                </div>
            </div>
            <div class="chart-wrapper">
                <canvas id="weeklyChart"></canvas>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-header">
                <div>
                    <div class="chart-title">💰 Estimated HOOD PM Revenue (Weekly)</div>
                    <div class="chart-subtitle" id="revenueChartSubtitle">HOOD gets $0.01/contract (adjustable above)</div>
                </div>
            </div>
            <div class="chart-wrapper">
                <canvas id="revenueChart"></canvas>
            </div>
        </div>

        <div class="notes">
            <h3>📝 Data Methodology</h3>
            <ul>
                <li><strong>Data Source:</strong> Kalshi Official API (<code>api.elections.kalshi.com</code>)</li>
                <li><strong>Update Frequency:</strong> Daily at 6:00 AM UTC via GitHub Actions</li>
                <li><strong>Volume Definition:</strong> Notional Volume = Contracts traded × $1</li>
                <li><strong>No Double Counting:</strong> Kalshi counts YES/NO as one contract</li>
                <li><strong>Fee Structure:</strong> <code>$0.02/contract = $0.01 (HOOD) + $0.01 (Kalshi)</code> - adjustable above</li>
                <li><strong>HOOD PM Revenue:</strong> Volume × Fee Rate (editable)</li>
                <li><strong>Monthly Estimate:</strong> Weekly Revenue × 4.3 weeks/month</li>
                <li><strong>Annual Estimate:</strong> Monthly Revenue × 12 months</li>
            </ul>
        </div>
    </div>

    <script>
        const dailyData = {daily_js};
        const weeklyData = {weekly_js};

        // Volume metrics for revenue calculation
        const dailyVolume24h = {daily_volume_24h};
        const latestWeekVolumeB = {latest_week_volume_b};
        const latestWeekVolumeM = latestWeekVolumeB * 1000;

        // Revenue chart reference (will be created later)
        let revenueChart = null;

        // Function to update all revenue displays
        function updateRevenueDisplays() {{
            const feeRate = parseFloat(document.getElementById('feeRate').value) || 0.01;

            // Calculate revenues
            const dailyRevenue = dailyVolume24h * feeRate;
            const weeklyRevenue = latestWeekVolumeM * feeRate;
            const monthlyRevenue = weeklyRevenue * 4.3;
            const annualRevenue = monthlyRevenue * 12;

            // Update metric cards
            document.getElementById('dailyRevenue').textContent = '$' + dailyRevenue.toFixed(2) + 'M';
            document.getElementById('weeklyRevenue').textContent = '$' + weeklyRevenue.toFixed(2) + 'M';
            document.getElementById('monthlyRevenue').textContent = '$' + monthlyRevenue.toFixed(1) + 'M';
            document.getElementById('annualRevenue').textContent = '$' + Math.round(annualRevenue) + 'M';

            // Update chart subtitle
            document.getElementById('revenueChartSubtitle').textContent =
                'HOOD gets $' + feeRate.toFixed(3) + '/contract (adjustable above)';

            // Update revenue chart data
            if (revenueChart) {{
                revenueChart.data.datasets[0].data = weeklyData.map(d => (d.volume * 1000 * feeRate).toFixed(2));
                revenueChart.update();
            }}
        }}

        // Add event listener for fee rate input
        document.getElementById('feeRate').addEventListener('input', updateRevenueDisplays);
        document.getElementById('feeRate').addEventListener('change', updateRevenueDisplays);

        // Daily Chart
        const dailyCtx = document.getElementById('dailyChart').getContext('2d');
        new Chart(dailyCtx, {{
            type: 'bar',
            data: {{
                labels: dailyData.map(d => d.date),
                datasets: [{{
                    label: 'Daily Notional Volume ($M)',
                    data: dailyData.map(d => d.volume),
                    backgroundColor: 'rgba(0, 212, 255, 0.6)',
                    borderColor: 'rgba(0, 212, 255, 1)',
                    borderWidth: 1,
                    borderRadius: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: (ctx) => `$$${{ctx.raw.toFixed(2)}}M` }} }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: '#888', maxTicksLimit: 15, maxRotation: 45 }} }},
                    y: {{ grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: '#888', callback: (val) => '$' + val + 'M' }} }}
                }}
            }}
        }});

        // Weekly Chart
        const weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
        new Chart(weeklyCtx, {{
            type: 'line',
            data: {{
                labels: weeklyData.map(d => d.week),
                datasets: [{{
                    label: 'Weekly Notional Volume ($B)',
                    data: weeklyData.map(d => d.volume),
                    borderColor: '#7c3aed',
                    backgroundColor: 'rgba(124, 58, 237, 0.2)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 6,
                    pointBackgroundColor: '#7c3aed'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: (ctx) => `$$${{ctx.raw.toFixed(3)}}B` }} }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: '#888' }} }},
                    y: {{ grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: '#888', callback: (val) => '$' + val + 'B' }}, min: 0 }}
                }}
            }}
        }});

        // Revenue Chart (with dynamic fee rate)
        const revenueCtx = document.getElementById('revenueChart').getContext('2d');
        const initialFeeRate = parseFloat(document.getElementById('feeRate').value) || 0.01;
        revenueChart = new Chart(revenueCtx, {{
            type: 'bar',
            data: {{
                labels: weeklyData.map(d => d.week),
                datasets: [{{
                    label: 'Est. HOOD PM Revenue ($M)',
                    data: weeklyData.map(d => (d.volume * 1000 * initialFeeRate).toFixed(2)),
                    backgroundColor: 'rgba(74, 222, 128, 0.6)',
                    borderColor: 'rgba(74, 222, 128, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: (ctx) => `$$${{ctx.raw}}M` }} }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: '#888' }} }},
                    y: {{ grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: '#888', callback: (val) => '$' + val + 'M' }} }}
                }}
            }}
        }});

        // Initialize revenue displays on page load
        updateRevenueDisplays();
    </script>
</body>
</html>'''

    return html

def main():
    # Load data
    with open("kalshi_volume_data.json", "r") as f:
        data = json.load(f)

    # Generate HTML
    html = generate_dashboard_html(data)

    # Save
    with open("index.html", "w") as f:
        f.write(html)

    print(f"Dashboard updated: index.html")

if __name__ == "__main__":
    main()
