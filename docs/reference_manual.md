# HUF Reference Manual (Worked Examples)

This manual is **examples-first**: each section is a real run with real inputs, the exact command, and the exact artifacts to inspect.

> HUF rule: **If a required artifact is missing, the run is invalid.**

## What ships in this repo

- **Handbook**: `docs/handbook.md` (contract + invariants + artifact requirements)
- **This Reference Manual**: `docs/reference_manual.md` (worked runs)
- **Cases + artifacts + (some) raw inputs**: `cases/`

Artifacts are always written as:

- `artifact_1_coherence_map.csv`
- `artifact_2_active_set.csv`
- `artifact_3_trace_report.jsonl`
- `artifact_4_error_budget.json`
- `run_stamp.json`

Most demos also emit `stability_packet.csv`.

---

## Case 1 — Markham 2018 (real budget workbook)

**Goal:** reduce a public budget table while preserving unity (mass) and keeping traceability to spreadsheet cells.

**Input (not bundled):**
- `cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx`

See `DATA_SOURCES.md` for where to download this workbook.

**Run (CLI):**
```bash
huf markham   --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx   --out out/markham2018   --tau-global 0.005   --tau-local 0.02
```

**What to inspect**
- **Coherence map**: fund-level shares; confirms local unity per fund and total discarded budget.
- **Active set**: the kept line-items (ranked) + exclusion reason.
- **Trace report**: look for `source_cell=...` in `regime_path` (cell-level accountability).
- **Error budget**: discarded mass (and any domain metric additions).

**Stability**
- `stability_packet.csv` sweeps `tau_global` (local fixed) and reports active-set size, discarded budget, and Jaccard vs previous.

---

## Case 2 — Toronto Traffic Signals (real CSV snapshot)

**Goal:** compress a phase-status telemetry snapshot into interpretable contributors.

### 2A. Phase-band compression

**Input (not bundled):**
- `cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv`

See `DATA_SOURCES.md` for where to download/export this CSV from Toronto Open Data.

**Run:**
```bash
huf traffic   --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv   --out out/traffic_phase   --tau-local 0.05
```

**Finite elements**
- `TCS × PHASE_BAND` counts  
  (`PHASE_BAND ∈ {MajorEven(2,4,6,8), MinorOdd(1,3,5,7), Other(9–12)}`)

**Interpretation**
- Each `TCS` is a regime; the active set tells you *which intersections dominate which phase bands*.

### 2B. Anomaly diagnostic (by status text)

**Run:**
```bash
huf traffic-anomaly   --csv cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv   --out out/traffic_anomaly   --status "Green Termination"
```

**Interpretation**
- Conditional unity: the budget is normalized **within the anomaly subset** only.
- Active set answers: “which intersections / phases dominate this anomaly status?”

---

## Case 3 — Planck LFI 70 GHz (real mission data; input FITS not bundled due to size)

**Goal:** preserve energy (Parseval-style accounting) while keeping a bounded active set.

**Run (after downloading the Planck LFI 70 GHz FITS map; see `DATA_SOURCES.md`):**
```bash
pip install -e ".[planck]"
huf planck --fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits --out out/planck70 --retained-target 0.97 --nside-out 64
```

**What to inspect**
- `artifact_4_error_budget.json` — contains discarded energy and derived RMSE under the Planck adapter.
- `stability_packet.csv` — tau sweep around the chosen threshold.

---

## Artifact reading checklist

1) **Coherence map**
- global discarded budget
- local unity checks (per regime)

2) **Active set**
- top contributors (rank order)
- any “why excluded” fields

3) **Trace report**
- every kept item must map back to verifiable origin (cell refs, pixel ranges, row IDs, etc.)

4) **Error budget**
- discarded budget (always)
- domain metric hooks (optional but recommended)
