# GUI Quickstart (non‑GitHub‑native users)

This page is for people who prefer **GUI workflows** (e.g., GitHub Desktop, file explorers, Word/Excel) but still want to **run HUF** and keep **record copies**.

## Note
This docs-only package does not include the code/CLI. To **run HUF**, download the **GitHub package** release as well.

## What you can do without Git
If you don’t want Git at all:

1. Download the latest **release ZIP** from GitHub (look for **Releases** on the right side of the repo page).
2. Unzip it to a folder like `Documents/HUF/`.
3. Open the Markdown record copies in `docs/`:
   - `docs/handbook.md`
   - `docs/reference_manual.md`
   - `docs/data_sources.md`

You can still run the CLI from this unzipped folder (see below).

## Using GitHub Desktop (recommended for updates)
If you want one-click updates:

1. Install **GitHub Desktop**.
2. In GitHub Desktop: **File → Clone repository…**
3. Pick a local folder (e.g., `Documents/GitHub/huf-core`).
4. To update later: press **Fetch origin** then **Pull origin**.

## One-time setup to run HUF
You need **Python 3.10+** installed.

### Step 1 — Open a terminal in the repo folder
- **Windows**: open File Explorer → go to the repo folder → right‑click → **Open in Terminal** (or PowerShell).
- **macOS**: Finder → repo folder → right‑click → **New Terminal at Folder** (or open Terminal and `cd`).
- **Linux**: open Terminal and `cd` into the folder.

### Step 2 — Run the bootstrap (cross‑platform)
From the repo root:

```bash
python scripts/bootstrap.py
```

This creates `.venv/` and installs everything you need.

> If you’re on macOS/Linux you can also use: `make bootstrap`

## Download the real input data (no big inputs are bundled)
### Markham + Toronto (automatic)
After bootstrap, run one of these:

```bash
make fetch-data
# or:
python scripts/fetch_data.py --markham --toronto
```

### Toronto non-interactive (`--yes`)
For scripted demos (no prompts):

```bash
make fetch-toronto-yes
# or:
python scripts/fetch_data.py --toronto --yes
```

### Planck (guided/manual)
Planck files are large, so HUF prints the steps instead of downloading by default:

```bash
make planck-guide
# or:
python scripts/fetch_data.py --planck-guide
```

## Run the demos
### Markham
```bash
huf markham --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out/markham2018 --tau-global 0.005 --tau-local 0.02
```

### Toronto traffic
```bash
huf traffic --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv --out out/traffic_phase --tau-local 0.05
```

## Where outputs go
Each run writes a folder like `out/markham2018/` or `out/traffic_phase/` containing the **mandatory artifacts**:

- `artifact_1_coherence_map.csv`
- `artifact_2_active_set.csv`
- `artifact_3_trace_report.jsonl`
- `artifact_4_error_budget.json`

You can open the CSVs in **Excel** and keep them with your meeting notes.
