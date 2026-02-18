#!/bin/bash
set -e
export HUF_TORONTO_CKAN="${HUF_TORONTO_CKAN:-https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action}"
cd "$(dirname "$0")"

echo
echo "=== HUF: Start Here (Linux) ==="
echo

PYTHON_BIN="python3"
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "ERROR: Python was not found."
  exit 1
fi

$PYTHON_BIN scripts/bootstrap.py
$PYTHON_BIN scripts/fetch_data.py --markham --toronto --yes || true

echo
echo "Setup complete."
echo