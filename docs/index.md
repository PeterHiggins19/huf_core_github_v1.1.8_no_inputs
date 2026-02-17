# HUF Core

## If you prefer GUI tools
Start with **GUI Quickstart**: `gui_quickstart.md` (GitHub Desktop workflow + step-by-step setup).
> Record copies: DOCX versions of the Handbook, Reference Manual, and Data Sources are included in this release under `docs/*.docx`.

HUF Core is a contract-first library for **auditable reduction under a unity budget**.

## The HUF system (three parts)

1) **Handbook** (`docs/handbook.md`): the contract + invariants + mandatory artifacts  
2) **Reference Manual** (`docs/reference_manual.md`): worked examples (real runs)  
3) **GitHub package** (this repo): library + CLI + tests + cases + example artifacts

**Data statement:** all Markham data is real, all Planck data is real, and all Toronto traffic data is real.

## Quickstart

```bash
pip install -e ".[dev]"
pytest -q
huf --help
```

## Real-data demos (inputs not bundled)

Inputs are excluded to keep downloads small. See `data_sources.md` for where to download them and the expected paths.

### Fetch Markham + Toronto inputs (automatic)

```bash
make fetch-data
# or: python scripts/fetch_data.py --markham --toronto
```

(Planck remains manual due to size; run `make planck-guide` for download instructions.)

### Markham 2018 budget (real workbook)

```bash
huf markham   --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx   --out out/markham2018
```

### Toronto traffic phase-band compression (real CSV snapshot)

```bash
huf traffic   --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv   --out out/traffic_phase
```

### Toronto traffic anomaly diagnostic

```bash
huf traffic-anomaly   --csv cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv   --out out/traffic_anomaly   --status "Green Termination"
```

Planck uses a real FITS map. The input is large (~480–500 MB) and is **not included**. Download it from public sources (ESA PLA or NASA/IPAC IRSA; see `data_sources.md`), place it under `cases/planck70/inputs/`, then install optional dependencies:

```bash
pip install -e ".[planck]"
huf planck --fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits --out out/planck70
```