# Inputs (not bundled)

This case uses **real City of Toronto** traffic-signal phase status data from the City's Open Data portal.

The full CSV can be several MB+ depending on the export window, so it is **not included** here.

## Required file
Place the CSV at:

- `cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv`

## Fast path (recommended)
From the repo root:

```bash
# downloads from the Toronto Open Data portal (you may be prompted to choose a resource)
python scripts/fetch_data.py --toronto
# or: make fetch-toronto
```

## Manual path
1. Go to the City of Toronto Open Data portal.
2. Search the catalogue for **Traffic Signal Phase Status** (or similar wording).
3. Download/export as CSV.
4. Rename to match the required filename above (or pass your path via `--csv`).

See `DATA_SOURCES.md` (repo root) for links and notes.

## After download
Run:

```bash
huf traffic-anomaly --csv cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv --out out/traffic_anomaly --status "Green Termination"
```
