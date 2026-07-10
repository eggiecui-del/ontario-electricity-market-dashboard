CREATE OR REPLACE VIEW v_hourly_market_summary AS
WITH generation_by_hour AS (
    SELECT
        g.timestamp_start,
        g.timestamp_end,
        g.date,
        g.hour_ending,
        SUM(g.output_mw) AS total_generation_mw,
        SUM(CASE WHEN g.fuel_type = 'Nuclear' THEN g.output_mw ELSE 0 END) AS nuclear_mw,
        SUM(CASE WHEN g.fuel_type = 'Hydro' THEN g.output_mw ELSE 0 END) AS hydro_mw,
        SUM(CASE WHEN g.fuel_type = 'Gas' THEN g.output_mw ELSE 0 END) AS gas_mw,
        SUM(CASE WHEN g.fuel_type = 'Wind' THEN g.output_mw ELSE 0 END) AS wind_mw,
        SUM(CASE WHEN g.fuel_type = 'Solar' THEN g.output_mw ELSE 0 END) AS solar_mw,
        SUM(CASE WHEN g.fuel_type = 'Biofuel' THEN g.output_mw ELSE 0 END) AS biofuel_mw,
        SUM(CASE WHEN f.is_renewable THEN g.output_mw ELSE 0 END) AS renewable_mw,
        SUM(CASE WHEN f.is_non_emitting THEN g.output_mw ELSE 0 END) AS non_emitting_mw
    FROM fact_generation_hourly g
    LEFT JOIN dim_fuel f
        ON g.fuel_type = f.fuel_type
    GROUP BY
        g.timestamp_start,
        g.timestamp_end,
        g.date,
        g.hour_ending
)
SELECT
    d.timestamp_start,
    d.timestamp_end,
    d.date,
    d.hour_ending,
    dd.year,
    dd.quarter,
    dd.month,
    dd.month_name,
    dd.day_of_week,
    dd.is_weekend,
    dd.season,
    h.hour_label,
    h.time_block,
    d.ontario_demand_mw,
    d.market_demand_mw,
    g.total_generation_mw,
    g.nuclear_mw,
    g.hydro_mw,
    g.gas_mw,
    g.wind_mw,
    g.solar_mw,
    g.biofuel_mw,
    CASE WHEN g.total_generation_mw > 0 THEN g.renewable_mw / g.total_generation_mw END AS renewable_share,
    CASE WHEN g.total_generation_mw > 0 THEN g.non_emitting_mw / g.total_generation_mw END AS non_emitting_share,
    CASE WHEN g.total_generation_mw > 0 THEN g.gas_mw / g.total_generation_mw END AS gas_share,
    p.price_mwh,
    p.price_type
FROM fact_demand_hourly d
LEFT JOIN generation_by_hour g
    ON d.timestamp_start = g.timestamp_start
LEFT JOIN fact_price_hourly p
    ON d.timestamp_start = p.timestamp_start
LEFT JOIN dim_date dd
    ON d.date = dd.date
LEFT JOIN dim_hour h
    ON d.hour_ending = h.hour_ending;

CREATE OR REPLACE VIEW v_daily_market_summary AS
SELECT
    date,
    year,
    month,
    month_name,
    season,
    AVG(ontario_demand_mw) AS avg_demand_mw,
    MAX(ontario_demand_mw) AS peak_demand_mw,
    AVG(price_mwh) AS avg_price_mwh,
    MAX(price_mwh) AS max_price_mwh,
    STDDEV_POP(price_mwh) AS price_volatility,
    AVG(renewable_share) AS avg_renewable_share,
    AVG(non_emitting_share) AS avg_non_emitting_share,
    AVG(gas_share) AS avg_gas_share
FROM v_hourly_market_summary
GROUP BY
    date,
    year,
    month,
    month_name,
    season;

CREATE OR REPLACE VIEW v_monthly_market_summary AS
SELECT
    year,
    month,
    month_name,
    season,
    AVG(ontario_demand_mw) AS avg_demand_mw,
    MAX(ontario_demand_mw) AS peak_demand_mw,
    AVG(price_mwh) AS avg_price_mwh,
    STDDEV_POP(price_mwh) AS price_volatility,
    AVG(renewable_share) AS renewable_share,
    AVG(non_emitting_share) AS non_emitting_share,
    AVG(gas_share) AS gas_share
FROM v_hourly_market_summary
GROUP BY
    year,
    month,
    month_name,
    season;

CREATE OR REPLACE VIEW v_market_stress_hours AS
WITH scored AS (
    SELECT
        *,
        PERCENT_RANK() OVER (ORDER BY ontario_demand_mw) AS demand_percentile,
        -- Percentiles are ranked only among rows where the value exists.
        -- Without this, the many NULL price hours push every priced hour above 0.9.
        CASE WHEN price_mwh IS NOT NULL THEN
            PERCENT_RANK() OVER (PARTITION BY (price_mwh IS NULL) ORDER BY price_mwh)
        END AS price_percentile,
        CASE WHEN gas_share IS NOT NULL THEN
            PERCENT_RANK() OVER (PARTITION BY (gas_share IS NULL) ORDER BY gas_share)
        END AS gas_share_percentile,
        CASE WHEN renewable_share IS NOT NULL THEN
            PERCENT_RANK() OVER (PARTITION BY (renewable_share IS NULL) ORDER BY renewable_share)
        END AS renewable_share_percentile
    FROM v_hourly_market_summary
)
SELECT
    *,
    (
        0.4 * demand_percentile
        + 0.3 * COALESCE(price_percentile, 0)
        + 0.2 * COALESCE(gas_share_percentile, 0)
        - 0.1 * COALESCE(renewable_share_percentile, 0)
    ) AS market_stress_score,
    price_percentile IS NOT NULL
        AND demand_percentile >= 0.9
        AND price_percentile >= 0.9 AS is_peak_risk_hour
FROM scored;
