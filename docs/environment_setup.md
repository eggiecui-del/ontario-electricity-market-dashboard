# Environment Setup

This project needs three things to run end to end:

- Python with the packages in `requirements.txt`
- PostgreSQL, easiest through Docker Desktop
- Power BI Desktop for the final `.pbix` file

## Common Setup Errors

`ModuleNotFoundError: No module named 'pandas'` means the current Python environment does not have the project dependencies installed. The code can still be correct, but the ETL cannot run until packages are installed. The fix is to create the virtual environment and install `requirements.txt` as shown below.

## Recommended Setup

Open PowerShell in the project folder:

```powershell
cd "$env:USERPROFILE\Desktop\ontario-electricity-market-dashboard"
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Test imports:

```powershell
python -c "import pandas, requests, sqlalchemy, psycopg; print('env ok')"
```

On this machine I saw `python --version` return `Python 3.14.5`, but `py -0p` did not find launcher-managed Python installs. So use `python`, not `py`, unless you install another Python version with the launcher later.

For safest data project setup, Python 3.11 or 3.12 is usually easier than a very new Python version. If package install fails on Python 3.14, install Python 3.12 from python.org and recreate the virtual environment.

## If Activation Is Blocked

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then close and reopen PowerShell, activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

## If `.venv` Is Access Denied

Try putting the virtual environment outside the project folder:

```powershell
python -m venv "$env:USERPROFILE\venvs\ontario-power"
& "$env:USERPROFILE\venvs\ontario-power\Scripts\Activate.ps1"
pip install -r requirements.txt
```

Then run commands from the project folder while that environment is active.

## Run The Pipeline

Start PostgreSQL:

```powershell
docker compose up -d
```

On this machine I did not find the `docker` command. That means Docker Desktop is not installed or not added to PATH. You have two choices:

1. Install Docker Desktop, then run `docker compose up -d`.
2. Install PostgreSQL directly and create a database named `ontario_power`.

Docker is easier for this portfolio project because the project already has `docker-compose.yml`.

Download, transform, and load data:

```powershell
python src/run_pipeline.py --start-date 2024-01-01 --end-date 2026-06-30 --load-postgres
```

If you only want to test the Python transform first:

```powershell
python src/run_pipeline.py --start-date 2026-04-02 --end-date 2026-04-05
```

This smaller date range downloads fewer daily price files.

## Power BI

After PostgreSQL is loaded:

1. Open Power BI Desktop.
2. Get Data -> PostgreSQL database.
3. Server: `localhost`
4. Database: `ontario_power`
5. Load these views:
   - `v_hourly_market_summary`
   - `v_daily_market_summary`
   - `v_monthly_market_summary`
   - `v_market_stress_hours`
6. Build pages using `powerbi/dashboard_build_notes.md`.
7. Save the file as `powerbi/ontario_electricity_dashboard.pbix`.
