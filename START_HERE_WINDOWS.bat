@echo off
setlocal
cd /d "%~dp0"

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

REM --- Fix Windows SSL cert issues by using certifi ---
.\.venv\Scripts\python -m pip install -q certifi
for /f "delims=" %%i in ('.\.venv\Scripts\python -c "import certifi; print(certifi.where())"') do set "SSL_CERT_FILE=%%i"

REM --- Toronto CKAN Action API base (portal front-end is NOT the action API) ---
set "TORONTO_CKAN=https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"

.\.venv\Scripts\python scripts\fetch_data.py --markham --toronto --yes --toronto-ckan %TORONTO_CKAN%
if errorlevel 1 (
  echo.
  echo NOTE: data fetch reported an error. You can re-run with:
  echo .\.venv\Scripts\python scripts\fetch_data.py --toronto --yes --toronto-ckan %TORONTO_CKAN%
)

echo.
echo Setup complete. Next try:
echo .\.venv\Scripts\huf --help
echo.
echo Markham demo:
echo .\.venv\Scripts\huf markham --xlsx cases\markham2018\inputs\2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out\markham2018
echo.
echo Toronto traffic demo:
echo .\.venv\Scripts\huf traffic --csv cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_phase
echo.
echo Planck guidance:
echo .\.venv\Scripts\python scripts\fetch_data.py --planck-guide
echo.
pause
