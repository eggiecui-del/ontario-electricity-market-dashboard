# Methodology

## Goal

The goal is to build an end-to-end analytics dashboard for Ontario electricity market data. I wanted the project to show more than only charts, so I included ETL scripts, a PostgreSQL model, SQL views, and Power BI notes.

## Data Choice

I used these IESO public report groups:

- Demand: annual CSV files
- Generation by fuel type: annual XML files
- Day-ahead Ontario zonal price: daily XML files

I did not label the project as HOEP because the price pipeline uses DA-OZP. If I add HOEP later, I would keep it as a separate price type and explain it clearly.

## Date Range

The intended project range is:

```text
2024-01-01 to 2026-06-30
```

Demand and generation have annual files for this range. DA-OZP price is only loaded for the daily files that exist in the public folder. In the checked directory on 2026-07-01, DA-OZP starts from 2026-04-02, so older hours have no DA-OZP price.

## Extract

The extract scripts download public files into `data/raw`.

- `extract_demand.py` downloads annual CSV files.
- `extract_generation.py` downloads annual XML files.
- `extract_price.py` downloads daily DA-OZP XML files.

The scripts download the non-versioned report files, for example `PUB_Demand_2024.csv`. I ignore `_v###` files in the transform step unless only versioned files exist.

## Transform

The transform step uses Pandas and XML parsing.

Main cleaning steps:

- Standardize column names.
- Convert IESO hour ending into `timestamp_start` and `timestamp_end`.
- Convert numeric fields to numeric types.
- Keep generation in long format for the fact table.
- Create date, hour, and fuel dimensions.
- Write a small data quality report.

## Hour Ending

IESO reports use hour ending. Example:

```text
2024-01-01, HE 1
```

This means the hour ending at 1:00, so I store:

```text
timestamp_start = 2024-01-01 00:00
timestamp_end   = 2024-01-01 01:00
```

For HE 24, the end time becomes midnight of the next day.

## Load

The load script creates the PostgreSQL tables, truncates old rows, loads processed CSV files, and creates reporting views.

I chose PostgreSQL because it is common in BI/data analyst work and lets Power BI connect to stable SQL views instead of raw files.

## Market Stress Score

The market stress score is not an official metric. I made it as an exploratory score:

```text
0.4 * demand_percentile
+ 0.3 * price_percentile
+ 0.2 * gas_share_percentile
- 0.1 * renewable_share_percentile
```

The idea is simple: high demand, high price, and higher gas share increase the score. Higher renewable share lowers it a little.

One important detail: the price percentile is calculated only among the hours that actually have DA-OZP price data (2026-04-02 onward). Hours without price data get 0 for the price term, so their maximum possible score is lower. This means the top stress rankings are naturally concentrated in the priced period, partly because of data coverage and not only because of market conditions. An earlier version of the view ranked NULL prices together with real prices, which pushed every priced hour above the 90th price percentile. I fixed this by ranking price only within the non-NULL rows.

This limitation is noted because the available price data only covers part of the project period. It is only a ranking tool for dashboard exploration.

## Interpretation Limits

The dashboard shows associations, not causation. For example, high prices appear to be associated with high demand or lower renewable share in the available data, but the project does not prove that one factor directly caused another.
