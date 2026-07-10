import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


DEFAULT_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/ontario_power"

LOAD_ORDER = [
    "dim_date",
    "dim_hour",
    "dim_fuel",
    "fact_demand_hourly",
    "fact_generation_hourly",
    "fact_price_hourly",
]


DATE_COLUMNS = {
    "dim_date": ["date"],
    "fact_demand_hourly": ["date"],
    "fact_generation_hourly": ["date"],
    "fact_price_hourly": ["date"],
}

TIMESTAMP_COLUMNS = {
    "fact_demand_hourly": ["timestamp_start", "timestamp_end"],
    "fact_generation_hourly": ["timestamp_start", "timestamp_end"],
    "fact_price_hourly": ["timestamp_start", "timestamp_end"],
}


def get_engine(database_url=None):
    load_dotenv()
    return create_engine(database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))


def execute_sql_file(engine, path):
    sql = Path(path).read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)


def prepare_for_postgres(table_name, df):
    df = df.copy()

    for column in DATE_COLUMNS.get(table_name, []):
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce").dt.date

    for column in TIMESTAMP_COLUMNS.get(table_name, []):
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    return df


def load_processed_tables(processed_dir="data/processed", database_url=None, sql_dir="sql"):
    processed_dir = Path(processed_dir)
    sql_dir = Path(sql_dir)
    engine = get_engine(database_url)

    execute_sql_file(engine, sql_dir / "01_create_tables.sql")

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE dim_date, dim_hour, dim_fuel, fact_demand_hourly, fact_generation_hourly, fact_price_hourly;"))

    for table_name in LOAD_ORDER:
        csv_path = processed_dir / f"{table_name}.csv"
        df = pd.read_csv(csv_path)
        df = prepare_for_postgres(table_name, df)
        df.to_sql(table_name, engine, if_exists="append", index=False, method="multi", chunksize=5000)
        print(f"loaded {table_name}: {len(df)} rows")

    execute_sql_file(engine, sql_dir / "02_create_views.sql")
    print("created reporting views")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--sql-dir", default="sql")
    args = parser.parse_args()

    load_processed_tables(args.processed_dir, args.database_url, args.sql_dir)


if __name__ == "__main__":
    main()
