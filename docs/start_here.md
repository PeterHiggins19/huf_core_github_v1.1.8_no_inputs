HUF-DOC: HUF.REL.DOCS.PAGE.START_HERE | HUF:1.1.8 | DOC:v0.1.0 | STATUS:release | LANE:release | RO:Peter Higgins
CODES: DOCS, START_HERE | ART: CM, AS, TR, EB | EVID:E2 | POSTURE:OP | WEIGHTS: OP=0.80 TOOL=0.20 PEER=0.00 | CAP: OP_MIN=0.51 TOOL_MAX=0.49 | CANON:docs/start_here.md

# HUF: Start Here (Windows)

This guide is written for “old-school” users: you want to **run the demos** and **see the artifacts** without learning Git on day one.

## 1) Download the release ZIP

1. Go to the HUF Core GitHub page.
2. Click **Releases**.
3. Download the latest ZIP asset.

Unzip it to a simple folder, e.g.:
`C:\Users\peter\Desktop\huf_core\`

## 2) Run the Windows starter

Double-click:

- `START_HERE_WINDOWS.bat`

It will:
- create a local virtual environment in `.venv`
- install HUF
- fetch the **Markham** and **Toronto** example inputs

When it finishes, it prints the next commands to run.

## 3) Run a demo

### Markham (budget)
```powershell
.\.venv\Scripts\huf markham --xlsx cases\markham2018\inputs\2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out\markham2018
```

### Toronto (traffic)
```powershell
.\.venv\Scripts\huf traffic --csv cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_phase
```

## 4) Where do outputs go?

Everything goes under `out\...`:

- `out\markham2018\...`
- `out\traffic_phase\...`

Open the PNGs and CSVs with the tools you already know (Windows Photos, Excel).

## 5) Planck (large data — guided)

Planck FITS maps are very large. Use the built-in guide:

```powershell
.\.venv\Scripts\python scripts\fetch_data.py --planck-guide
```

Then run:

```powershell
.\.venv\Scripts\huf planck --fits cases\planck70\inputs\LFI_SkyMap_070_1024_R3.00_full.fits --out out\planck70
```

## 6) If something breaks

See the Troubleshooting section in the full docs on GitHub Pages:
`https://peterhiggins19.github.io/huf_core/`

