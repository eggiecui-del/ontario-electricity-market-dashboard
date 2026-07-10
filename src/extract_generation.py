import argparse
from pathlib import Path

from utils import download_file


BASE_URL = "https://reports-public.ieso.ca/public/GenOutputbyFuelHourly"


def download_generation_files(years, raw_dir="data/raw", overwrite=False):
    raw_dir = Path(raw_dir)
    downloaded = []

    for year in years:
        file_name = f"PUB_GenOutputbyFuelHourly_{year}.xml"
        url = f"{BASE_URL}/{file_name}"
        output_path = raw_dir / file_name
        if download_file(url, output_path, overwrite=overwrite):
            downloaded.append(output_path)
            print(f"downloaded generation {year}")

    return downloaded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, required=True)
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    download_generation_files(args.years, args.raw_dir, args.overwrite)


if __name__ == "__main__":
    main()
