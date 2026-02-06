#!/usr/bin/env python3
"""
Polymarket Dashboard HTML Generator
Reads volume data from JSON and generates the dashboard HTML
"""

import json
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

def load_volume_data():
    data_path = os.path.join(SCRIPT_DIR, 'polymarket_volume_data.json')
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            return json.load(f)
    return None

def generate_html(data):
    metrics = data['metrics']
    daily_json = json.dumps(data['daily_data'])
    weekly_json = json.dumps(data['weekly_data'])
    last_updated = data['last_updated']
    
    vol_24h = metrics['volume_24h_millions']
    oi = metrics['open_interest_millions']
    liq = metrics['liquidity_millions']
    active = metrics['active_markets']
    
    # Build HTML string
    html = "<!DOCTYPE html>\n<html><head>"
    html += "<meta charset='UTF-8'><title>Polymarket Volume Dashboard</title>"
    html += "<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>"
    html += "<style>"
    html += "*{margin:0;padding:0;box-sizing:border-box}"
    html += "body{font-family:system-ui;background:#0f0f23;color:#e0e0e0;padding:20px}"
    html += ".c{max-width:1400px;margin:auto}"
    html += ".h{text-align:center;padding:20px;background:rgba(255,255,255,.05);border-radius:15px;margin-bottom:30px}"
    html += "h1{font-size:2em;color:#ff6b35}"
    html += ".g{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:30px}"
    html += ".m{background:rgba(255,255,255,.05);border-radius:12px;padding:20px;text-align:center}"
    html += ".m .l{color:#888;font-size:.9em}.m .v{font-size:1.8em;font-weight:bold;color:#ff6b35}"
    html += ".box{background:rgba(255,255,255,.05);border-radius:15px;padding:25px;margin-bottom:20px}"
    html += ".wrap{height:350px;position:relative}"
    html += "a{display:inline-block;padding:8px 16px;margin:5px;border-radius:8px;text-decoration:none;background:rgba(255,255,255,.1);color:#00d4ff}"
    html += "</style></head><body>"
    html += "<div class='c'><div class='h'>"
    html += "<h1>Polymarket Volume Dashboard</h1>"
    html += "<p style='color:#888'>Data Source: Gamma API | Updated: " + last_updated + "</p>"
    html += "<div style='margin-top:15px'><a href='../'>Home</a><a href='../kalshi/' style='background:rgba(0,212,255,.2)'>Kalshi</a></div>"
    html += "</div>"
    html += "<div class='g'>"
    html += "<div class='m'><div class='l'>24h Volume</div><div class='v'>$" + str(vol_24h) + "M</div></div>"
    html += "<div class='m'><div class='l'>Open Interest</div><div class='v'>$" + str(oi) + "M</div></div>"
    html += "<div class='m'><div class='l'>Liquidity</div><div class='v'>$" + str(liq) + "M</div></div>"
    html += "<div class='m'><div class='l'>Active Markets</div><div class='v'>" + str(active) + "</div></div>"
    html += "</div>"
    html += "<div class='box'><h3 style='margin-bottom:15px'>Daily Volume</h3><div class='wrap'><canvas id='d'></canvas></div></div>"
    html += "<div class='box'><h3 style='margin-bottom:15px'>Weekly Volume</h3><div class='wrap'><canvas id='w'></canvas></div></div>"
    html += "</div><script>"
    html += "const dd=" + daily_json + ";"
    html += "const wd=" + weekly_json + ";"
    html += "new Chart(document.getElementById('d'),{type:'bar',data:{labels:dd.map(d=>d.date),datasets:[{data:dd.map(d=>d.volume),backgroundColor:'rgba(255,107,53,.6)',borderColor:'rgba(255,107,53,1)',borderWidth:1}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#888',maxTicksLimit:15}},y:{ticks:{color:'#888'}}}}});"
    html += "new Chart(document.getElementById('w'),{type:'line',data:{labels:wd.map(d=>d.week),datasets:[{data:wd.map(d=>d.volume),borderColor:'#f7931e',backgroundColor:'rgba(247,147,30,.2)',fill:true,tension:.3,pointRadius:6}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#888'}},y:{ticks:{color:'#888'},min:0}}}});"
    html += "</script></body></html>"
    return html

def main():
    print("Generating Polymarket dashboard...")
    data = load_volume_data()
    if data:
        html = generate_html(data)
        polymarket_folder = os.path.join(ROOT_DIR, "polymarket")
        os.makedirs(polymarket_folder, exist_ok=True)
        output_path = os.path.join(polymarket_folder, "index.html")
        with open(output_path, 'w') as f:
            f.write(html)
        print("Dashboard saved to " + output_path)
    else:
        print("No data file found")

if __name__ == '__main__':
    main()
