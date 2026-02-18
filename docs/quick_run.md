# Quick run (all HUF demos)

This repo includes three runnable demos out of the box (Traffic Phase, Traffic Anomaly, Markham). Planck is optional because the FITS file is large.

## 1) Bootstrap

Windows:
- `START_HERE_WINDOWS.bat`

macOS:
- `START_HERE_MAC.command`

Linux:
- `./start_here_linux.sh`

Manual fallback (all OS):
```bash
python scripts/bootstrap.py
```

## 2) Run everything (recommended)

This runs:
- unit tests (unless skipped)
- Markham
- Traffic Phase
- Traffic Anomaly
- Planck (only if you provide `--planck-fits`)

```bash
# Windows (PowerShell)
.\.venv\Scripts\python scripts\run_all_cases.py

# macOS/Linux
./.venv/bin/python scripts/run_all_cases.py
```

Outputs land in: `out/smoke/<timestamp>/...`

### Optional: include Planck
After you download the FITS (see `cases/planck70/inputs/README.md`):

```bash
# Windows
.\.venv\Scripts\python scripts\run_all_cases.py --planck-fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits

# macOS/Linux
./.venv/bin/python scripts/run_all_cases.py --planck-fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits
```

## 3) Run individual demos

### Markham
```bash
huf markham --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out/markham2018
```

### Traffic Phase
```bash
huf traffic --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv --out out/traffic_phase
```

### Traffic Anomaly
Use a smaller default tau (0.005 can exclude all elements on the bundled CSV):

```bash
huf traffic-anomaly --csv cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv --out out/traffic_anomaly --status "Green Termination" --tau-global 0.0005
```

### Planck (optional)
```bash
huf planck --fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits --out out/planck70
```

## 4) What “success” looks like

Each output folder should contain:
- `artifact_1_coherence_map.csv`
- `artifact_2_active_set.csv`
- `artifact_3_trace_report.jsonl`
- `artifact_4_error_budget.json`
- `run_stamp.json`
- `meta.json`
- `stability_packet.csv`
