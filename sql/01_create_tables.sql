CREATE TABLE IF NOT EXISTS dim_date (
    date_id integer PRIMARY KEY,
    date date NOT NULL UNIQUE,
    year integer NOT NULL,
    quarter integer NOT NULL,
    month integer NOT NULL,
    month_name text NOT NULL,
    day_of_week text NOT NULL,
    is_weekend boolean NOT NULL,
    season text NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_hour (
    hour_id integer PRIMARY KEY,
    hour_ending integer NOT NULL UNIQUE,
    hour_label text NOT NULL,
    time_block text NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_fuel (
    fuel_id integer PRIMARY KEY,
    fuel_type text NOT NULL UNIQUE,
    fuel_group text NOT NULL,
    is_renewable boolean NOT NULL,
    is_non_emitting boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_demand_hourly (
    timestamp_start timestamp NOT NULL,
    timestamp_end timestamp NOT NULL,
    date date NOT NULL,
    hour_ending integer NOT NULL,
    ontario_demand_mw numeric,
    market_demand_mw numeric
);

CREATE TABLE IF NOT EXISTS fact_generation_hourly (
    timestamp_start timestamp NOT NULL,
    timestamp_end timestamp NOT NULL,
    date date NOT NULL,
    hour_ending integer NOT NULL,
    fuel_type text NOT NULL,
    output_mw numeric,
    output_quality integer
);

CREATE TABLE IF NOT EXISTS fact_price_hourly (
    timestamp_start timestamp NOT NULL,
    timestamp_end timestamp NOT NULL,
    date date NOT NULL,
    hour_ending integer NOT NULL,
    price_mwh numeric,
    price_type text NOT NULL,
    flag text,
    loss_price_capped numeric,
    congestion_price_capped numeric
);

CREATE INDEX IF NOT EXISTS idx_demand_timestamp ON fact_demand_hourly (timestamp_start);
CREATE INDEX IF NOT EXISTS idx_generation_timestamp ON fact_generation_hourly (timestamp_start);
CREATE INDEX IF NOT EXISTS idx_generation_fuel ON fact_generation_hourly (fuel_type);
CREATE INDEX IF NOT EXISTS idx_price_timestamp ON fact_price_hourly (timestamp_start);
