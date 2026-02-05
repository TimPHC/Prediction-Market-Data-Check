# Prediction Market Data Check

**Live Dashboard:** [https://timphc.github.io/Prediction-Market-Data-Check/](https://timphc.github.io/Prediction-Market-Data-Check/)

---

## Kalshi-HOOD PM Dashboard

Real-time Kalshi trading volume dashboard with HOOD PM revenue estimation.

### Features
- **24h Volume** - Real-time trading volume from Kalshi API
- **Open Interest** - Current positions value  
- **Active Markets** - Number of markets currently trading
- **Editable HOOD Fee Rate** - Adjust fee rate ($0.001 - $0.10) to recalculate revenue estimates
- **HOOD PM Revenue Estimates** - Daily, Weekly, Monthly, Annualized projections
- **Interactive Charts** - Daily volume (90 days), Weekly volume trend, Weekly HOOD revenue

### Revenue Calculation Logic

| Metric | Data Source | Calculation |
|--------|-------------|-------------|
| **Daily Revenue** | Kalshi API `volume_24h` | 24h Volume × Fee Rate |
| **Weekly Revenue** | Kalshi API `weekly_data[-1]` | Latest Week Volume × Fee Rate |
| **Monthly Revenue** | Derived | Weekly × 4.3 |
| **Annual Revenue** | Derived | Monthly × 12 |

### Fee Structure
```
$0.02/contract = $0.01 (HOOD share) + $0.01 (Kalshi share)
```
Default HOOD fee rate: **$0.01/contract** (editable in dashboard)

---

## Repository Structure
```
├── index.html                 # Dashboard webpage (GitHub Pages)
├── kalshi_volume_data.json    # Latest data from Kalshi API
├── update_dashboard.py        # Generates index.html from data
├── update_kalshi_data.py      # Fetches data from Kalshi API
├── .github/workflows/         # GitHub Actions for daily auto-update
│
├── README.md                  # This file
│
└── Kalshi-HOOD Dashboard/
    ├── kalshi_api_framework.md
    ├── platform_comparison.md
    ├── polymarket_double_counting_analysis.md
    ├── dune_dashboard_audit_summary.md
    ├── dune_query_results.md
    ├── verification_query.sql
    └── verify_double_counting.py
```

### Auto-Update
- **Schedule:** Daily at 6:00 AM UTC via GitHub Actions
- **Process:**
  1. `update_kalshi_data.py` fetches latest data from Kalshi API
  2. `update_dashboard.py` regenerates `index.html` with new data
  3. Changes auto-committed to repo

---

## Data Source

**Kalshi Official API:** `api.elections.kalshi.com`

- Volume = Contracts traded × $1 notional
- No double counting (YES/NO counted as one contract)
- Real-time 24h volume and open interest
- Historical daily and weekly aggregations

---

## Usage

### View Dashboard
Visit: [https://timphc.github.io/Prediction-Market-Data-Check/](https://timphc.github.io/Prediction-Market-Data-Check/)

### Adjust Fee Rate
Use the green input box on the dashboard to change the HOOD fee rate. All revenue estimates update dynamically.

---

## License
For internal analysis purposes.# Prediction-Market-Data-Check
