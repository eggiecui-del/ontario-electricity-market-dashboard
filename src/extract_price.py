import argparse
from pathlib import Path

from utils import date_range, download_file


BASE_URL = "https://reports-public.ieso.ca/public/DAHourlyOntarioZonalPrice"


def download_price_files(start_date, end_date, raw_dir="data/raw", overwrite=False):
    raw_dir = Path(raw_dir)
    downloaded = []
    missing = 0

    for current_date in date_range(start_date, end_date):
        file_name = f"PUB_DAHourlyOntarioZonalPrice_{current_date:%Y%m%d}.xml"
        url = f"{BASE_URL}/{file_name}"
        output_path = raw_dir / file_name
        ok = download_file(url, output_path, overwrite=overwrite, allow_missing=True)

        if ok:
            downloaded.append(output_path)
        else:
            missing += 1

    print(f"downloaded {len(downloaded)} price files, skipped {missing} missing days")
    return downloaded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    download_price_files(args.start_date, args.end_date, args.raw_dir, args.overwrite)


if __name__ == "__main__":
    main()
