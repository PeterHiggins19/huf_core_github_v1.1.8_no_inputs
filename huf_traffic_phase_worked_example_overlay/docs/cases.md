# Included cases

These cases are **ready-to-run** from a fresh clone.

**Inputs**
- ✅ Markham XLSX: shipped in `cases/markham2018/inputs/`
- ✅ Toronto traffic CSVs: shipped in `cases/traffic_phase/inputs/` and `cases/traffic_anomaly/inputs/`
- ❌ Planck FITS: **not shipped** (large). Use `python scripts/fetch_data.py --planck-guide` for a copy/paste download guide.

**Outputs**
- New runs write to `out/<case_name>/` (recommended).
- Each run produces the same core artifacts:
  `artifact_1_coherence_map.csv`, `artifact_2_active_set.csv`,
  `artifact_3_trace_report.jsonl`, `artifact_4_error_budget.json`,
  plus `meta.json` and `run_stamp.json`.

---

## Quick commands (Windows PowerShell)

> Tip: run `START_HERE_WINDOWS.bat` first (it prepends `.\.venv\Scripts` to `PATH`).

Fetch (optional refresh of shipped inputs):
```powershell
.\.venv\Scripts\python scripts\fetch_data.py --markham --toronto --yes
```

Run Markham:
```powershell
huf markham --xlsx cases\markham2018\inputs\2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out\markham2018
```

Run Traffic Phase:
```powershell
huf traffic --csv cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_phase
```

Run Traffic Anomaly:
```powershell
huf traffic-anomaly --csv cases\traffic_anomaly\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_anomaly --status "Green Termination"
```

Planck guide (prints download steps, does **not** download automatically):
```powershell
.\.venv\Scripts\python scripts\fetch_data.py --planck-guide
```

---

## What each case demonstrates

### Markham 2018 budget (XLSX)
- Adapter: `huf markham ...`
- Shows: **multi-fund budget compression** + **cell-level provenance** from a public workbook.
- Best next page: 👉 [Markham worked example](markham_worked_example.md)

### Toronto traffic phase (CSV)
- Adapter: `huf traffic ...`
- Shows: **phase-band compression** (lots of rows → fewer coherent regimes) for operational signals.
- Best next page: 👉 [Traffic Phase worked example](traffic_phase_worked_example.md)

### Toronto traffic anomaly (CSV)
- Adapter: `huf traffic-anomaly ...`
- Shows: **diagnostic filtering** for a named status (e.g., `"Green Termination"`) with global discard reporting.

### Planck LFI 70 GHz (FITS)
- Adapter: `huf planck ...`
- Shows: **pixel-energy compression** on a sky map (requires `astropy`; FITS not bundled).

---

## Verify a run quickly

After any run, check the output folder has at least:
- `run_stamp.json`
- `artifact_1_coherence_map.csv`
- `artifact_2_active_set.csv`

Example:
```powershell
Test-Path out\markham2018\run_stamp.json
Test-Path out\markham2018\artifact_1_coherence_map.csv
```

---

## Links

- Repo case folders (inputs + example artifacts):  
  `cases/markham2018/`, `cases/traffic_phase/`, `cases/traffic_anomaly/`, `cases/planck70/`


- GitHub (browse raw files):
  - Markham: https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/tree/main/cases/markham2018
  - Traffic phase: https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/tree/main/cases/traffic_phase
  - Traffic anomaly: https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/tree/main/cases/traffic_anomaly
  - Planck: https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/tree/main/cases/planck70
