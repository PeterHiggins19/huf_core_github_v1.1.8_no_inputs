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

REM 3) Tell Python/urllib to use certifi CA bundle for this session
for /f "delims=" %%i in ('.\.venv\Scripts\python -c "import certifi; print(certifi.where())"') do set "SSL_CERT_FILE=%%i"

REM 4) Fetch Markham
echo.
echo --- Fetch: Markham ---
.\.venv\Scripts\python scripts\fetch_data.py --markham
if errorlevel 1 goto :warn

REM 5) Fetch Toronto (non-interactive)
echo.
echo --- Fetch: Toronto (non-interactive) ---
set "TORONTO_CKAN_BASE=https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"
.\.venv\Scripts\python scripts\fetch_data.py --toronto --yes --toronto-ckan "%TORONTO_CKAN_BASE%"
if errorlevel 1 goto :warn

echo.
echo OK. Setup + data fetch complete.
echo Next:
echo   .\.venv\Scripts\huf --help
echo   .\.venv\Scripts\huf markham --xlsx cases\markham2018\inputs\2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out\markham2018
echo   .\.venv\Scripts\huf traffic --csv cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_phase
echo   .\.venv\Scripts\python scripts\fetch_data.py --planck-guide
echo.
pause
exit /b 0

:warn
echo.
echo WARNING: One of the fetch steps reported an error.
echo If Toronto fails, try this in PowerShell from the repo root:
echo   .\.venv\Scripts\python scripts\fetch_data.py --toronto --yes --toronto-ckan "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"
echo.
pause
exit /b 1

:error
echo.
echo ERROR: Bootstrap failed.
echo Open the console output above for the exact error.
echo.
pause
exit /b 1
