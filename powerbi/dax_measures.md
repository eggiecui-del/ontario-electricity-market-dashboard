# DAX Measures

These measures are for Power BI after connecting to the SQL views or fact tables.

## Demand

```DAX
Avg Demand MW =
AVERAGE(v_hourly_market_summary[ontario_demand_mw])
```

```DAX
Peak Demand MW =
MAX(v_hourly_market_summary[ontario_demand_mw])
```

```DAX
Market Demand MW =
AVERAGE(v_hourly_market_summary[market_demand_mw])
```

## Price

```DAX
Avg Price =
AVERAGE(v_hourly_market_summary[price_mwh])
```

```DAX
Price Volatility =
STDEV.P(v_hourly_market_summary[price_mwh])
```

```DAX
Max Price =
MAX(v_hourly_market_summary[price_mwh])
```

## Generation

```DAX
Total Generation MW =
AVERAGE(v_hourly_market_summary[total_generation_mw])
```

```DAX
Renewable Share =
AVERAGE(v_hourly_market_summary[renewable_share])
```

```DAX
Non-emitting Share =
AVERAGE(v_hourly_market_summary[non_emitting_share])
```

```DAX
Gas Share =
AVERAGE(v_hourly_market_summary[gas_share])
```

## Stress

```DAX
Avg Stress Score =
AVERAGE(v_market_stress_hours[market_stress_score])
```

```DAX
Peak Risk Hours =
CALCULATE(
    COUNTROWS(v_market_stress_hours),
    v_market_stress_hours[is_peak_risk_hour] = TRUE()
)
```

## Simple Formatting

Use these formats:

- Demand and generation: whole number, `#,0 MW`
- Price: currency, `$#,0.00/MWh`
- Shares: percentage, `0.0%`
- Stress score: decimal, `0.00`
