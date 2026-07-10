# Data Dictionary

This file explains the tables in plain words. I kept the model simple.

## dim_date

One row per date.

| Column | Meaning |
| --- | --- |
| date_id | Simple numeric key |
| date | Calendar date |
| year | Calendar year |
| quarter | Calendar quarter |
| month | Month number |
| month_name | Month name |
| day_of_week | Monday, Tuesday, etc. |
| is_weekend | True for Saturday and Sunday |
| season | Winter, Spring, Summer, Fall |

## dim_hour

One row per IESO hour ending value.

| Column | Meaning |
| --- | --- |
| hour_id | Same as hour ending |
| hour_ending | IESO hour ending, 1 to 24 |
| hour_label | Label like HE 01 |
| time_block | Overnight, Morning, Afternoon, Evening |

## dim_fuel

One row per fuel type.

| Column | Meaning |
| --- | --- |
| fuel_id | Simple numeric key |
| fuel_type | Nuclear, Hydro, Gas, Wind, Solar, Biofuel, Storage |
| fuel_group | Renewable, Nuclear, Fossil, Storage, Other |
| is_renewable | True for Hydro, Wind, Solar, Biofuel |
| is_non_emitting | True for Nuclear, Hydro, Wind, Solar, Biofuel |

I use Hydro as renewable and non-emitting. Gas is emitting. Nuclear is non-emitting but not renewable.

## fact_demand_hourly

Hourly Ontario demand data from the IESO Demand report.

| Column | Meaning |
| --- | --- |
| timestamp_start | Start of the hour |
| timestamp_end | End of the hour |
| date | Report date |
| hour_ending | IESO hour ending |
| ontario_demand_mw | Ontario demand in MW |
| market_demand_mw | Market demand in MW |

## fact_generation_hourly

Hourly generation output by fuel type.

| Column | Meaning |
| --- | --- |
| timestamp_start | Start of the hour |
| timestamp_end | End of the hour |
| date | Report date |
| hour_ending | IESO hour ending |
| fuel_type | Fuel type |
| output_mw | Output in MW |
| output_quality | IESO quality flag from the XML |

## fact_price_hourly

Hourly price data from the DA-OZP report.

| Column | Meaning |
| --- | --- |
| timestamp_start | Start of the hour |
| timestamp_end | End of the hour |
| date | Delivery date |
| hour_ending | Pricing hour |
| price_mwh | Zonal price in $/MWh |
| price_type | DA-OZP |
| flag | IESO report flag |
| loss_price_capped | Loss price component |
| congestion_price_capped | Congestion price component |

## Views

`v_hourly_market_summary` is the main Power BI view. It joins demand, generation, price, date, and hour.

`v_daily_market_summary` is used for daily trend charts.

`v_monthly_market_summary` is used for seasonal and month-level reporting.

`v_market_stress_hours` adds demand percentile, price percentile, gas share percentile, renewable share percentile, and a simple stress score.
