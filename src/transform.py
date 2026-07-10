import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd


NS = {"ieso": "http://www.ieso.ca/schema"}

DEMAND_COLUMNS = [
    "timestamp_start",
    "timestamp_end",
    "date",
    "hour_ending",
    "ontario_demand_mw",
    "market_demand_mw",
]

GENERATION_COLUMNS = [
    "timestamp_start",
    "timestamp_end",
    "date",
    "hour_ending",
    "fuel_type",
    "output_mw",
    "output_quality",
]

PRICE_COLUMNS = [
    "timestamp_start",
    "timestamp_end",
    "date",
    "hour_ending",
    "price_mwh",
    "price_type",
    "flag",
    "loss_price_capped",
    "congestion_price_capped",
]


def _text(node, path, default=None):
    if node is None:
        return default
    child = node.find(path, NS)
    if child is None or child.text is None:
        return default
    return child.text.strip()


def _to_float(value):
    if value in (None, ""):
        return None
    return float(value)


def _to_int(value):
    if value in (None, ""):
        return None
    return int(value)


def _add_hour_timestamps(df):
    if df.empty:
        return df

    dates = pd.to_datetime(df["date"])
    hours = pd.to_numeric(df["hour_ending"], errors="coerce").astype("Int64")

    # IESO reports use hour ending, so I keep both the start and end timestamps.
    df["timestamp_start"] = dates + pd.to_timedelta(hours - 1, unit="h")
    df["timestamp_end"] = dates + pd.to_timedelta(hours, unit="h")
    return df


def parse_demand_file(path):
    df = pd.read_csv(path, comment="\\")
    df.columns = [col.strip() for col in df.columns]
    df = df.rename(
        columns={
            "Date": "date",
            "Hour": "hour_ending",
            "Ontario Demand": "ontario_demand_mw",
            "Market Demand": "market_demand_mw",
        }
    )

    df = df[["date", "hour_ending", "ontario_demand_mw", "market_demand_mw"]]
    df["hour_ending"] = pd.to_numeric(df["hour_ending"], errors="coerce").astype("Int64")
    df["ontario_demand_mw"] = pd.to_numeric(df["ontario_demand_mw"], errors="coerce")
    df["market_demand_mw"] = pd.to_numeric(df["market_demand_mw"], errors="coerce")
    df = df.dropna(subset=["date", "hour_ending"])
    df = _add_hour_timestamps(df)
    return df[DEMAND_COLUMNS]


def parse_generation_xml(path):
    root = ET.parse(path).getroot()
    rows = []

    for daily in root.findall(".//ieso:DailyData", NS):
        day = _text(daily, "ieso:Day")

        for hourly in daily.findall("ieso:HourlyData", NS):
            hour = _to_int(_text(hourly, "ieso:Hour"))

            for fuel_total in hourly.findall("ieso:FuelTotal", NS):
                fuel_type = _text(fuel_total, "ieso:Fuel", "").title()
                energy_value = fuel_total.find("ieso:EnergyValue", NS)

                rows.append(
                    {
                        "date": day,
                        "hour_ending": hour,
                        "fuel_type": fuel_type,
                        "output_mw": _to_float(_text(energy_value, "ieso:Output")),
                        "output_quality": _to_int(_text(energy_value, "ieso:OutputQuality")),
                    }
                )

    df = pd.DataFrame(rows, columns=["date", "hour_ending", "fuel_type", "output_mw", "output_quality"])
    df = _add_hour_timestamps(df)
    return df[GENERATION_COLUMNS]


def parse_price_xml(path):
    root = ET.parse(path).getroot()
    delivery_date = _text(root, ".//ieso:DeliveryDate")
    rows = []

    for item in root.findall(".//ieso:HourlyPriceComponents", NS):
        rows.append(
            {
                "date": delivery_date,
                "hour_ending": _to_int(_text(item, "ieso:PricingHour")),
                "price_mwh": _to_float(_text(item, "ieso:ZonalPrice")),
                "price_type": "DA-OZP",
                "flag": _text(item, "ieso:Flag"),
                "loss_price_capped": _to_float(_text(item, "ieso:LossPriceCapped")),
                "congestion_price_capped": _to_float(_text(item, "ieso:CongestionPriceCapped")),
            }
        )

    df = pd.DataFrame(rows, columns=["date", "hour_ending", "price_mwh", "price_type", "flag", "loss_price_capped", "congestion_price_capped"])
    df = _add_hour_timestamps(df)
    return df[PRICE_COLUMNS]


def _main_report_files(paths):
    paths = list(paths)
    main_files = [path for path in paths if "_v" not in path.stem]
    return main_files if main_files else paths


def _filter_dates(df, start_date, end_date):
    if df.empty:
        return df

    dates = pd.to_datetime(df["date"])
    mask = (dates >= pd.Timestamp(start_date)) & (dates <= pd.Timestamp(end_date))
    return df.loc[mask].copy()


def _season(month):
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Fall"


def build_dim_date(frames):
    date_values = []
    for frame in frames:
        if not frame.empty:
            date_values.append(frame["date"])

    if not date_values:
        return pd.DataFrame(columns=["date_id", "date", "year", "quarter", "month", "month_name", "day_of_week", "is_weekend", "season"])

    dates = pd.to_datetime(pd.concat(date_values)).drop_duplicates().sort_values()
    records = []
    for idx, value in enumerate(dates, start=1):
        records.append(
            {
                "date_id": idx,
                "date": value.date().isoformat(),
                "year": value.year,
                "quarter": value.quarter,
                "month": value.month,
                "month_name": value.month_name(),
                "day_of_week": value.day_name(),
                "is_weekend": value.dayofweek >= 5,
                "season": _season(value.month),
            }
        )
    return pd.DataFrame(records)


def build_dim_hour():
    records = []
    for hour in range(1, 25):
        if hour <= 6 or hour == 24:
            block = "Overnight"
        elif hour <= 11:
            block = "Morning"
        elif hour <= 17:
            block = "Afternoon"
        else:
            block = "Evening"

        records.append(
            {
                "hour_id": hour,
                "hour_ending": hour,
                "hour_label": f"HE {hour:02d}",
                "time_block": block,
            }
        )
    return pd.DataFrame(records)


def build_dim_fuel(generation):
    default_fuels = ["Nuclear", "Hydro", "Gas", "Wind", "Solar", "Biofuel", "Storage"]
    found_fuels = [] if generation.empty else sorted(generation["fuel_type"].dropna().unique())
    fuels = sorted(set(default_fuels + found_fuels))

    renewable = {"Hydro", "Wind", "Solar", "Biofuel"}
    non_emitting = {"Nuclear", "Hydro", "Wind", "Solar", "Biofuel"}
    records = []

    for idx, fuel in enumerate(fuels, start=1):
        if fuel in renewable:
            group = "Renewable"
        elif fuel == "Nuclear":
            group = "Nuclear"
        elif fuel == "Gas":
            group = "Fossil"
        elif fuel == "Storage":
            group = "Storage"
        else:
            group = "Other"

        records.append(
            {
                "fuel_id": idx,
                "fuel_type": fuel,
                "fuel_group": group,
                "is_renewable": fuel in renewable,
                "is_non_emitting": fuel in non_emitting,
            }
        )

    return pd.DataFrame(records)


def build_quality_report(demand, generation, price):
    rows = [
        {"check_name": "demand_rows", "value": len(demand)},
        {"check_name": "generation_rows", "value": len(generation)},
        {"check_name": "price_rows", "value": len(price)},
        {"check_name": "missing_ontario_demand", "value": int(demand["ontario_demand_mw"].isna().sum()) if not demand.empty else 0},
        {"check_name": "missing_generation_output", "value": int(generation["output_mw"].isna().sum()) if not generation.empty else 0},
        {"check_name": "missing_price", "value": int(price["price_mwh"].isna().sum()) if not price.empty else 0},
    ]

    for name, frame in [("demand", demand), ("generation", generation), ("price", price)]:
        if frame.empty:
            rows.append({"check_name": f"{name}_date_range", "value": "no rows"})
        else:
            rows.append({"check_name": f"{name}_date_range", "value": f"{frame['date'].min()} to {frame['date'].max()}"})

    return pd.DataFrame(rows)


def _read_many(files, parser, columns):
    frames = []
    for path in files:
        frames.append(parser(path))

    if not frames:
        return pd.DataFrame(columns=columns)

    return pd.concat(frames, ignore_index=True)


def transform_all(raw_dir="data/raw", processed_dir="data/processed", start_date="2024-01-01", end_date="2026-06-30"):
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    demand_files = _main_report_files(sorted(raw_dir.glob("PUB_Demand*.csv")))
    generation_files = _main_report_files(sorted(raw_dir.glob("PUB_GenOutputbyFuelHourly*.xml")))
    price_files = _main_report_files(sorted(raw_dir.glob("PUB_DAHourlyOntarioZonalPrice*.xml")))

    demand = _read_many(demand_files, parse_demand_file, DEMAND_COLUMNS)
    generation = _read_many(generation_files, parse_generation_xml, GENERATION_COLUMNS)
    price = _read_many(price_files, parse_price_xml, PRICE_COLUMNS)

    demand = _filter_dates(demand, start_date, end_date)
    generation = _filter_dates(generation, start_date, end_date)
    price = _filter_dates(price, start_date, end_date)

    dim_date = build_dim_date([demand, generation, price])
    dim_hour = build_dim_hour()
    dim_fuel = build_dim_fuel(generation)
    quality = build_quality_report(demand, generation, price)

    outputs = {
        "fact_demand_hourly.csv": demand,
        "fact_generation_hourly.csv": generation,
        "fact_price_hourly.csv": price,
        "dim_date.csv": dim_date,
        "dim_hour.csv": dim_hour,
        "dim_fuel.csv": dim_fuel,
        "data_quality_report.csv": quality,
    }

    for file_name, frame in outputs.items():
        frame.to_csv(processed_dir / file_name, index=False)

    print(f"wrote processed files to {processed_dir}")
    return outputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--start-date", default="2024-01-01")
    parser.add_argument("--end-date", default="2026-06-30")
    args = parser.parse_args()

    transform_all(args.raw_dir, args.processed_dir, args.start_date, args.end_date)


if __name__ == "__main__":
    main()
