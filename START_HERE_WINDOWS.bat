@echo off
setlocal EnableExtensions

REM Always run from the repo root (where this .bat lives)
cd /d "%~dp0"

echo === HUF: Start Here (Windows) ===
echo This will set up a local Python venv and fetch Markham + Toronto inputs.
echo Planck is guided/manual because it is very large.
echo.

REM 1) Bootstrap (creates .venv and installs huf-core + dev tools)
python scripts\bootstrap.py
if errorlevel 1 goto :error

REM 2) Ensure certifi is present (helps SSL on some Windows/Python installs)
.\.venv\Scripts\python -m pip install --upgrade certifi
if errorlevel 1 goto :error

REM 3) Fetch Markham (usually works as-is)
echo.
echo --- Fetch: Markham ---
.\.venv\Scripts\python scripts\fetch_data.py --markham
if errorlevel 1 goto :warn

REM 4) Fetch Toronto (use the correct CKAN Action API base; non-interactive)
echo.
echo --- Fetch: Toronto (non-interactive) ---
set "TORONTO_CKAN_BASE=https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"
.\.venv\Scripts\python scripts\fetch_data.py --toronto --yes --toronto-ckan "%TORONTO_CKAN_BASE%"
if errorlevel 1 goto :warn

echo.
echo ✅ Setup + data fetch complete.
echo Next:
echo   .\.venv\Scripts\huf --help
echo   huf markham --xlsx cases\markham2018\inputs\2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out\markham2018
echo   huf traffic --csv cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_phase
echo   .\.venv\Scripts\python scripts\fetch_data.py --planck-guide
echo.
pause
exit /b 0

:warn
echo.
echo ⚠ One of the fetch steps reported an error.
echo If Toronto still fails, try running this in PowerShell from the repo root:
echo   .\.venv\Scripts\python scripts\fetch_data.py --toronto --yes --toronto-ckan "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"
echo.
echo You can also download the Toronto CSV manually in a browser and save it to:
echo   cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv
echo.
pause
exit /b 1

:error
echo.
echo ❌ Bootstrap failed.
echo Open the console output above for the exact error.
echo.
pause
exit /b 1
