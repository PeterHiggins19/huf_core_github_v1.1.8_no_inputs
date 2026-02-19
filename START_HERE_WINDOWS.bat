@echo off

REM Keep the user's original PATH so we can persistently prepend the venv tools.
set "HUF__ORIG_PATH=%PATH%"

REM Default Toronto CKAN API endpoint (can be overridden by environment variable)
if "%HUF_TORONTO_CKAN%"=="" set "HUF_TORONTO_CKAN=https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"

REM Script location (repo root)
set "HUF__SCRIPT_DIR=%~dp0"
set "HUF__VENV_SCRIPTS=%HUF__SCRIPT_DIR%.venv\Scripts"

setlocal EnableExtensions
cd /d "%HUF__SCRIPT_DIR%"
chcp 65001 >nul

echo.
echo === HUF: Start Here (Windows) ===
echo This will set up the Python virtual environment and download Markham + Toronto inputs.
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

REM 1) Create/refresh the venv + install deps
python scripts\bootstrap.py
if errorlevel 1 (
  echo.
  echo ERROR: bootstrap failed.
  pause
  exit /b 1
)

REM 2) Prepend venv Scripts to PATH for this session so `huf` resolves to the venv (not conda)
if exist "%HUF__VENV_SCRIPTS%\huf.exe" (
  set "PATH=%HUF__VENV_SCRIPTS%;%PATH%"
  echo [ok] Using venv tools first: %HUF__VENV_SCRIPTS%
) else (
  echo WARNING: venv huf.exe not found at %HUF__VENV_SCRIPTS%\huf.exe
  echo          Continuing, but `huf` may resolve to a different install.
)

echo.
REM 3) Fetch inputs using the venv Python
"%HUF__VENV_SCRIPTS%\python.exe" scripts\fetch_data.py --markham --toronto --yes
if errorlevel 1 (
  echo.
  echo NOTE: data fetch reported an error. You can re-run interactively with:
  echo   "%HUF__VENV_SCRIPTS%\python.exe" scripts\fetch_data.py --toronto --yes
)

echo.
echo Setup complete. Next try:
echo   huf --help
echo.
echo Markham demo:
echo   huf markham --xlsx cases\markham2018\inputs\2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out\markham2018
echo.
echo Toronto traffic demo:
echo   huf traffic --csv cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_phase
echo.
echo Planck guidance:
echo   "%HUF__VENV_SCRIPTS%\python.exe" scripts\fetch_data.py --planck-guide
echo.

pause

REM Persist PATH change for users who launched this from an existing cmd.exe window.
endlocal & set "PATH=%HUF__VENV_SCRIPTS%;%HUF__ORIG_PATH%"
