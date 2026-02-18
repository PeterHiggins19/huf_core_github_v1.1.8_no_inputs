# Start Here (Zero GitHub Knowledge)

This guide is for people who want to **run HUF from scratch** without learning “git commands”.

You have **two easy paths**:

- **Path A (fastest):** download a ZIP from GitHub and run HUF locally (no GitHub account needed).
- **Path B (recommended):** use **GitHub Desktop** (point-and-click) so updates are easy.

---

## What you need

- A Windows PC or Mac (Linux works too)
- Internet access
- **Python 3.10+** installed  
  - Windows: install from python.org and **check “Add Python to PATH”**
  - Mac: Python 3 is usually available; if not, install from python.org

Optional but recommended:
- **GitHub Desktop** (no command line): https://desktop.github.com/

---

## Path A: Download ZIP (no GitHub account needed)

1. Open the HUF GitHub page in your browser.
2. Click the green **Code** button → **Download ZIP**.
3. Unzip it to a folder like `Documents\HUF` (Windows) or `~/Documents/HUF` (Mac).
4. Continue to **Bootstrap (install + setup)** below.

---

## Path B: GitHub Desktop (recommended for updates)

1. Install GitHub Desktop: https://desktop.github.com/
2. (Optional) Create a GitHub account on https://github.com/  
   You can still *download* without an account, but Desktop works best with one.
3. In GitHub Desktop: **File → Clone repository…**
4. Paste the repository URL and choose a local folder (e.g., `Documents/HUF`).

Continue to **Bootstrap**.

---

## Bootstrap (install + setup)

### Easiest (one click)

**Windows:** double‑click:
- `START_HERE_WINDOWS.bat`

**Mac:** right‑click then **Open**:
- `START_HERE_MAC.command`

**Linux:** run:
- `./start_here_linux.sh`

These scripts:
1) create a `.venv` virtual environment  
2) install dependencies  
3) print the next commands

### Manual fallback (if you prefer typing)

From the repository folder:

```bash
python scripts/bootstrap.py
```

If `python` does not work on Mac/Linux, try:

```bash
python3 scripts/bootstrap.py
```

---

## Fetch the real public data (Markham + Toronto)

### One command

```bash
make fetch-data
```

or:

```bash
python scripts/fetch_data.py --markham --toronto
```

### Toronto non‑interactive (best for demos)

```bash
make fetch-toronto-yes
```

or:

```bash
python scripts/fetch_data.py --toronto --yes
```

If the Toronto file chosen is not the one you want, rerun **without** `--yes` and pick from the menu.

---

## Planck (large file: guided/manual)

Planck FITS files are very large, so HUF does **not** download them automatically.

Run:

```bash
make planck-guide
```

or:

```bash
python scripts/fetch_data.py --planck-guide
```

This prints:
- where to download Planck data (PLA / IRSA)
- the expected local file path under `cases/planck70/inputs/`

---

## Run your first HUF demos

### Markham

```bash
huf markham --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out/markham2018
```

### Toronto traffic

```bash
huf traffic --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv --out out/traffic_phase
```

Outputs and artifacts are written under the `out/` folder.

---

## Documentation

All docs are kept in **Markdown (`.md`)** for easy reading on GitHub.

Recommended:
- [Learning Path](learning_path.md)
- [Get Started (Zero GitHub)](get_started_zero_github.md)

---

## Troubleshooting

- **“python not found”**: install Python 3.10+ from python.org (Windows: check “Add to PATH”)
- **Mac won’t run `.command`**: right-click → Open (first time only)
- **Toronto fetch picked the wrong dataset**: rerun without `--yes`

