-- Top demand hours.
SELECT
    timestamp_start,
    ontario_demand_mw,
    price_mwh,
    gas_share,
    renewable_share
FROM v_hourly_market_summary
ORDER BY ontario_demand_mw DESC
LIMIT 10;

-- Demand pattern by hour ending.
SELECT
    hour_ending,
    hour_label,
    AVG(ontario_demand_mw) AS avg_demand_mw
FROM v_hourly_market_summary
GROUP BY hour_ending, hour_label
ORDER BY hour_ending;

-- Weekday vs weekend demand.
SELECT
    is_weekend,
    AVG(ontario_demand_mw) AS avg_demand_mw,
    MAX(ontario_demand_mw) AS peak_demand_mw
FROM v_hourly_market_summary
GROUP BY is_weekend;

-- Monthly demand and price.
SELECT
    year,
    month,
    month_name,
    avg_demand_mw,
    peak_demand_mw,
    avg_price_mwh,
    price_volatility
FROM v_monthly_market_summary
ORDER BY year, month;

-- Fuel shares by month.
SELECT
    year,
    month,
    month_name,
    renewable_share,
    non_emitting_share,
    gas_share
FROM v_monthly_market_summary
ORDER BY year, month;

-- Simple correlation table for the price page.
SELECT
    CORR(price_mwh, ontario_demand_mw) AS corr_price_demand,
    CORR(price_mwh, gas_share) AS corr_price_gas_share,
    CORR(price_mwh, renewable_share) AS corr_price_renewable_share
FROM v_hourly_market_summary
WHERE price_mwh IS NOT NULL;

-- Top market stress hours.
SELECT
    timestamp_start,
    ontario_demand_mw,
    price_mwh,
    gas_share,
    renewable_share,
    market_stress_score
FROM v_market_stress_hours
ORDER BY market_stress_score DESC
LIMIT 20;
