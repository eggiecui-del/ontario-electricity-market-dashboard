# Validation Log

## 2026-07-01

Environment:

- Created `.venv` inside the desktop project.
- Installed packages from `requirements.txt`.
- Confirmed imports for `pandas`, `requests`, `sqlalchemy`, and `psycopg`.
- `pandas` version tested: `3.0.3`.

Python checks:

- Parsed all Python files with `ast`.
- Result: `syntax ok`.

Small ETL test:

```powershell
.\.venv\Scripts\python.exe src\run_pipeline.py --start-date 2026-04-02 --end-date 2026-04-03 --years 2026
```

Result:

- Downloaded `PUB_Demand_2026.csv`
- Downloaded `PUB_GenOutputbyFuelHourly_2026.xml`
- Downloaded 2 DA-OZP price XML files
- Wrote processed CSV files into `data/processed`

Row counts:

| File | Rows |
| --- | ---: |
| `fact_demand_hourly.csv` | 48 |
| `fact_generation_hourly.csv` | 336 |
| `fact_price_hourly.csv` | 48 |

Data quality report:

- Missing Ontario demand: 0
- Missing generation output: 0
- Missing price: 0
- Demand date range: 2026-04-02 to 2026-04-03
- Generation date range: 2026-04-02 to 2026-04-03
- Price date range: 2026-04-02 to 2026-04-03

Remaining at this point:

- Power BI connection
- Final `.pbix`
- Dashboard screenshots

PostgreSQL load test:

- Local PostgreSQL 18 service was running on port 5432.
- Fixed `load_postgres.py` date/timestamp conversion before inserting CSV data.
- Loaded 2-day test data into PostgreSQL successfully.
- Created SQL views successfully.

Database row-count check:

| Object | Rows |
| --- | ---: |
| `fact_demand_hourly` | 48 |
| `fact_generation_hourly` | 336 |
| `fact_price_hourly` | 48 |
| `v_hourly_market_summary` | 48 |

Remaining at this point:

- Power BI connection
- Final `.pbix`
- Dashboard screenshots

## 2026-07-02

Full PostgreSQL load check:

| Object | Rows | Date Range |
| --- | ---: | --- |
| `fact_demand_hourly` | 21,887 | 2024-01-01 to 2026-06-30 |
| `fact_generation_hourly` | 142,248 | 2024-01-01 to 2026-06-30 |
| `fact_price_hourly` | 2,160 | 2026-04-02 to 2026-06-30 |
| `v_hourly_market_summary` | 21,887 | demand-based hourly summary |
| `v_daily_market_summary` | 912 | daily summary |
| `v_monthly_market_summary` | 30 | monthly summary |
| `v_market_stress_hours` | 21,887 | hourly stress scoring |

Data quality note:

- Expected demand hours from 2024-01-01 to 2026-06-30 are 21,888.
- Loaded demand rows are 21,887.
- The missing row is 2025-05-01 HE 1.
- The raw IESO `PUB_Demand_2025.csv` starts 2025-05-01 at HE 2 for that date, so the pipeline did not drop this row.

Remaining at this point:

- Power BI connection
- Final `.pbix`
- Dashboard screenshots

## 2026-07-03

Power BI build:

- Connected Power BI Desktop to PostgreSQL (`localhost:5432`, database `ontario_power`, Import mode).
- Loaded the 4 reporting views.
- Built 5 report pages: Executive Overview, Demand Patterns, Supply Mix, Price & Volatility, Market Stress.
- Added the DAX measures from `powerbi/dax_measures.md`.
- Saved `powerbi/ontario_electricity_dashboard.pbix`.
- Exported 5 page screenshots into `screenshots/`.

## 2026-07-05

Stress score fix:

- Found that `v_market_stress_hours` ranked NULL prices together with real prices. Because most hours have no DA-OZP price, every priced hour landed above the 90th price percentile, which inflated stress scores in the priced window.
- Rewrote the view so price, gas share, and renewable share percentiles are ranked only among non-NULL rows.
- `is_peak_risk_hour` now requires a real price percentile, so it can only be true inside the DA-OZP coverage period.

After re-running the SQL:

- `Peak Risk Hours`: 80.
- Top stress hours are still mainly late June 2026 evening hours.

Top rows from `v_market_stress_hours` after the fix:

| Timestamp | Stress Score | Demand MW | Price | Gas Share | Renewable Share |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-06-30 19:00 | 0.8839 | 23,361 | 233.14 | 0.3356 | 0.2471 |
| 2026-06-30 20:00 | 0.8823 | 23,300 | 148.23 | 0.3323 | 0.2460 |
| 2026-06-30 21:00 | 0.8757 | 22,310 | 133.07 | 0.3120 | 0.2408 |
| 2026-06-30 18:00 | 0.8645 | 23,526 | 231.71 | 0.3169 | 0.2779 |
| 2026-06-29 17:00 | 0.8642 | 22,234 | 167.65 | 0.3120 | 0.2678 |
