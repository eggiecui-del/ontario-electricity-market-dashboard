from datetime import date, timedelta
from pathlib import Path

import requests


def download_file(url, output_path, overwrite=False, allow_missing=False):
    output_path = Path(output_path)
    if output_path.exists() and not overwrite:
        return True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=60)

    if response.status_code == 404 and allow_missing:
        return False

    response.raise_for_status()
    output_path.write_bytes(response.content)
    return True


def parse_date(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def date_range(start_date, end_date):
    current = parse_date(start_date)
    end = parse_date(end_date)
    while current <= end:
        yield current
        current += timedelta(days=1)
