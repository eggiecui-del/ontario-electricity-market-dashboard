import argparse
from datetime import date
from pathlib import Path

from extract_demand import download_demand_files
from extract_generation import download_generation_files
from extract_price import download_price_files
from load_postgres import load_processed_tables
from transform import transform_all
from utils import parse_date


DEFAULT_PRICE_START = date(2026, 4, 2)


def _year_range(start_date, end_date):
    return list(range(start_date.year, end_date.year + 1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default="2024-01-01")
    parser.add_argument("--end-date", default="2026-06-30")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--sql-dir", default="sql")
    parser.add_argument("--years", nargs="+", type=int)
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--load-postgres", action="store_true")
    parser.add_argument("--database-url", default=None)
    args = parser.parse_args()

    start_date = parse_date(args.start_date)
    end_date = parse_date(args.end_date)
    years = args.years or _year_range(start_date, end_date)

    raw_dir = Path(args.raw_dir)
    processed_dir = Path(args.processed_dir)

    if not args.skip_download:
        download_demand_files(years, raw_dir, args.overwrite)
        download_generation_files(years, raw_dir, args.overwrite)

        # DA-OZP daily files start later in public folder I checked.
        price_start = max(start_date, DEFAULT_PRICE_START)
        download_price_files(price_start, end_date, raw_dir, args.overwrite)

    transform_all(raw_dir, processed_dir, start_date.isoformat(), end_date.isoformat())

    if args.load_postgres:
        load_processed_tables(processed_dir, args.database_url, args.sql_dir)


if __name__ == "__main__":
    main()
