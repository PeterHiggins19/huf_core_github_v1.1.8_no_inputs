#!/bin/bash
set -e
export HUF_TORONTO_CKAN="${HUF_TORONTO_CKAN:-https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action}"
cd "$(dirname "$0")"

echo
echo "=== HUF: Start Here (macOS) ==="
echo "This will set up Python environment and download Markham + Toronto inputs."
echo "Planck is guided/manual because the files are very large."
echo

PYTHON_BIN="python3"
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "ERROR: Python was not found."
  echo "Install Python 3.10+ from https://www.python.org/downloads/macos/"
  exit 1
fi

$PYTHON_BIN scripts/bootstrap.py
$PYTHON_BIN scripts/fetch_data.py --markham --toronto --yes || true

echo
echo "Setup complete. Next try:"
echo "  ./.venv/bin/python -m huf_core.cli --help"
echo "or (if installed as console script):"
echo "  huf --help"
echo
echo "Planck guidance:"
echo "  $PYTHON_BIN scripts/fetch_data.py --planck-guide"
echo