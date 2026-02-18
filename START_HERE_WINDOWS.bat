@echo off
if "%HUF_TORONTO_CKAN%"=="" set "HUF_TORONTO_CKAN=https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"
setlocal EnableExtensions
cd /d "%~dp0"
chcp 65001 >nul

echo.
echo === HUF: Start Here (Windows) ===
echo This will set up Python environment and download Markham + Toronto inputs.
echo Planck is guided/manual because the files are very large.
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found.
  echo Please install Python 3.10+ from https://www.python.org/downloads/windows/
  echo IMPORTANT: check "Add python.exe to PATH" during install.
  echo Then run this file again.
  echo.
  pause
  exit /b 1
)

python scripts\bootstrap.py
if errorlevel 1 (
  echo.
  echo ERROR: bootstrap failed.
  pause
  exit /b 1
)

python scripts\fetch_data.py --markham --toronto --yes
if errorlevel 1 (
  echo.
  echo NOTE: data fetch reported an error. You can re-run interactively with:
  echo   python scripts\fetch_data.py --toronto
)

echo.
echo Setup complete. Next try:
echo   .venv\Scripts\python -m huf_core.cli --help
echo or:
echo   huf --help
echo.
echo Markham demo:
echo   huf markham --xlsx cases\markham2018\inputs\2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out\markham2018
echo.
echo Toronto traffic demo:
echo   huf traffic --csv cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_phase
echo.
echo Planck guidance:
echo   python scripts\fetch_data.py --planck-guide
echo.
pause