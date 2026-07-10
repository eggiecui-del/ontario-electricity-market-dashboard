# Ontario Electricity Market Analytics Dashboard

I made this project to analyze Ontario electricity demand, generation by fuel type, and market price patterns using public IESO data. The project is kept simple on purpose: Python ETL, PostgreSQL tables, SQL views, and a Power BI dashboard.

This is not a forecasting project and it is not an official market model. It is a portfolio analytics project.

## Business Questions

- When does Ontario electricity demand usually peak?
- How does the generation mix change by fuel type?
- Are high prices connected with high demand, gas output, or low renewable share?
- Which hours look like market stress hours?
- What can a non-technical stakeholder understand from the dashboard in 1 minute?

## Data Sources

The data comes from IESO public reports:

- Hourly Demand Report: https://reports-public.ieso.ca/public/Demand/
- Generator Output by Fuel Type Hourly: https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/
- Day-Ahead Hourly Ontario Zonal Price: https://reports-public.ieso.ca/public/DAHourlyOntarioZonalPrice/
- Main IESO power data page: https://www.ieso.ca/power-data

I use "market price" or "day-ahead zonal price" in the project wording. I do not call it HOEP because the pipeline is not using HOEP hourly data.

Checked on 2026-07-01: demand and generation have annual files for 2024, 2025, and 2026. The DA-OZP folder is daily XML files and the available public directory starts from 2026-04-02 in the checked listing, so price is joined only where DA-OZP exists.

## Tech Stack

- Python
- Pandas
- PostgreSQL
- SQL
- Power BI
- Docker Compose (optional)

## Project Structure

```text
ontario-electricity-market-dashboard/
+-- README.md
+-- requirements.txt
+-- docker-compose.yml
+-- data/
|   +-- raw/
|   +-- processed/
|   +-- sample/
+-- sql/
|   +-- 01_create_tables.sql
|   +-- 02_create_views.sql
|   +-- 03_analysis_queries.sql
+-- src/
|   +-- extract_demand.py
|   +-- extract_generation.py
|   +-- extract_price.py
|   +-- transform.py
|   +-- load_postgres.py
|   +-- run_pipeline.py
+-- powerbi/
+-- screenshots/
+-- docs/
```

## Data Pipeline

```text
IESO public reports
        -> Python download scripts
        -> Pandas cleaning
        -> processed CSV files
        -> PostgreSQL fact and dimension tables
        -> SQL views
        -> Power BI dashboard
```

## Database Tables

Dimensions:

- `dim_date`
- `dim_hour`
- `dim_fuel`

Facts:

- `fact_demand_hourly`
- `fact_generation_hourly`
- `fact_price_hourly`

Main reporting views:

- `v_hourly_market_summary`
- `v_daily_market_summary`
- `v_monthly_market_summary`
- `v_market_stress_hours`

## How To Run

For full setup details, see `docs/environment_setup.md`.

Create the Python environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start PostgreSQL:

```powershell
docker compose up -d
```

Run the ETL:

```powershell
python src/run_pipeline.py --start-date 2024-01-01 --end-date 2026-06-30 --load-postgres
```

If you only want to test the transform using files already in `data/raw`, use:

```powershell
python src/run_pipeline.py --start-date 2024-01-01 --end-date 2026-06-30 --skip-download
```

Default database URL:

```text
postgresql+psycopg://postgres:postgres@localhost:5432/ontario_power
```

## Power BI Build

Connect Power BI to PostgreSQL and use these views:

- `v_hourly_market_summary`
- `v_daily_market_summary`
- `v_monthly_market_summary`
- `v_market_stress_hours`

The dashboard pages are documented in `powerbi/dashboard_build_notes.md`. DAX measures are in `powerbi/dax_measures.md`.

The Power BI Desktop file is saved as:

```text
powerbi/ontario_electricity_dashboard.pbix
```

Dashboard screenshots are saved in `screenshots/`.

The methodology, data dictionary, validation notes, and dashboard findings are documented in `docs/`.

## Key Metrics

- Average demand MW
- Peak demand MW
- Average market price $/MWh
- Price volatility
- Renewable share
- Non-emitting share
- Gas share
- Market stress score

## Limitations

- DA-OZP price data is only joined where the public daily XML file exists.
- IESO reports use hour ending. I convert it into `timestamp_start` and `timestamp_end`.
- The market stress score is my own exploratory metric, not an official IESO metric.
- I did not add weather, forecasting, or real-time 5-minute price data because that would make the first version too large.




