# Dashboard Build Notes

## Data Source

Use Power BI Desktop.

Connection:

- Connector: PostgreSQL database
- Server: `localhost:5432`
- Database: `ontario_power`
- Mode: Import
- Authentication: Database
- User name: `postgres`
- Password: use the local demo password from .env.example, or your own local PostgreSQL password

Do not use the SQL Server connector. This project uses PostgreSQL.

Load these views:

- `v_hourly_market_summary`
- `v_daily_market_summary`
- `v_monthly_market_summary`
- `v_market_stress_hours`

## Report Style

Keep the report simple and student-level:

- White or very light gray background
- Dark gray text
- Blue/teal for demand and generation
- Orange for price and stress
- No heavy gradients
- No decorative images
- Use short titles

## Page 1: Executive Overview

Goal: show the full project in 10 seconds.

Use `v_hourly_market_summary`.

KPI cards:

- Average Demand MW: average of `ontario_demand_mw`
- Peak Demand MW: max of `ontario_demand_mw`
- Average Market Price: average of `price_mwh`
- Price Volatility: standard deviation of `price_mwh`
- Renewable Share: average of `renewable_share`
- Non-emitting Share: average of `non_emitting_share`
- Gas Share: average of `gas_share`

Charts:

- Combo chart: `date` on x-axis, average `ontario_demand_mw` as column, average `price_mwh` as line.
- Stacked area chart: `date` on x-axis, values `nuclear_mw`, `hydro_mw`, `gas_mw`, `wind_mw`, `solar_mw`, `biofuel_mw`.
- Bar chart: top 10 `timestamp_start` by `ontario_demand_mw`.
- Bar or donut chart: average fuel shares using `renewable_share`, `non_emitting_share`, `gas_share`.

Slicers:

- `year`
- `month_name`
- `season`
- `is_weekend`

Small note:

"Price data uses available DA-OZP records from 2026-04-02 to 2026-06-30."

## Page 2: Demand Patterns

Goal: explain when demand is high.

Use `v_hourly_market_summary` and `v_daily_market_summary`.

Charts:

- Line chart: `timestamp_start` and `ontario_demand_mw`.
- Column chart: `hour_ending` and average `ontario_demand_mw`.
- Column chart: `month_name` and average `ontario_demand_mw`; sort by `month`.
- Bar chart: `is_weekend` and average `ontario_demand_mw`.
- Matrix heatmap: rows `day_of_week`, columns `hour_ending`, values average `ontario_demand_mw`.
- Table: top 10 `date` by `peak_demand_mw` from `v_daily_market_summary`.

Main message:

"Demand tends to be highest in evening hours and in winter/summer months."

## Page 3: Supply Mix

Goal: explain how fuel types supply demand.

Use `v_hourly_market_summary`.

Charts:

- Stacked area chart: `date` and fuel MW columns: `nuclear_mw`, `hydro_mw`, `gas_mw`, `wind_mw`, `solar_mw`, `biofuel_mw`.
- Line chart: `date`, average `renewable_share`, average `non_emitting_share`, average `gas_share`.
- Combo chart: `date`, average `ontario_demand_mw` as column, average `gas_mw` as line.
- Cards: average renewable share, non-emitting share, gas share.

Main message:

"The supply mix is mostly non-emitting, and gas appears more important during some high-demand periods."

## Page 4: Price And Volatility

Goal: explain price movement and spikes.

Use `v_hourly_market_summary` and `v_monthly_market_summary`.

Charts:

- Line chart: `timestamp_start` and `price_mwh`.
- Column chart: `year`, `month`, and average `price_mwh`.
- Column chart: `year`, `month`, and `price_volatility` from `v_monthly_market_summary`.
- Table: top 20 `timestamp_start` by `price_mwh`.
- Scatter plot: daily points from `v_daily_market_summary`, x-axis `avg_gas_share`, y-axis `avg_price_mwh`.

Correlation notes:

- corr(price, demand): 0.775
- corr(price, gas share): 0.681
- corr(price, renewable share): -0.428

These correlations use only the available DA-OZP period.

Main message:

"For the available DA-OZP period, higher price is associated with higher demand and higher gas share."

## Page 5: Market Stress

Goal: make the project more business-focused.

Use `v_market_stress_hours`.

Charts:

- Table: top 20 rows sorted by `market_stress_score` descending.
- Line chart: `timestamp_start` and `market_stress_score`.
- Bar chart: `date` and average `market_stress_score`.
- Combo chart: `timestamp_start`, `ontario_demand_mw`, `price_mwh`, and `gas_share`.

Definition:

```text
Peak Risk Hour = demand percentile >= 90%
                 and price percentile >= 90%
                 (price percentile exists only for hours with DA-OZP data)
```

Stress score:

```text
0.4 demand percentile
+ 0.3 price percentile
+ 0.2 gas share percentile
- 0.1 renewable share percentile
```

Price, gas share, and renewable share percentiles are ranked only among hours where the value exists. Hours without DA-OZP price get 0 for the price term.

Do not call it official. It is an exploratory metric.

Page note text box:

"Market stress uses demand, price, gas share, and renewable share. Price percentile and peak risk are calculated only for hours with DA-OZP price data, so this is an exploratory ranking, not an official market risk metric."

Main message:

"The highest stress hours in this load are concentrated in the DA-OZP price window, especially late June 2026 evening hours. Part of this concentration comes from price data coverage, not only market conditions."

## Save And Export

Save the Power BI file as:

```text
powerbi/ontario_electricity_dashboard.pbix
```

Export screenshots:

```text
screenshots/executive_overview.png
screenshots/demand_patterns.png
screenshots/supply_mix.png
screenshots/price_volatility.png
screenshots/market_stress.png
```

