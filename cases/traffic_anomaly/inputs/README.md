# Inputs (Toronto traffic anomaly subset)

This case uses the same Toronto phase-status CSV as `traffic_phase`, then filters to specific `PHASE_STATUS_TEXT` values.

In this repo snapshot, the CSV is already included at:

- `cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv`

(It is identical to the file in `cases/traffic_phase/inputs/`.)

## Run
From the repo root:

```bash
huf traffic-anomaly \
  --csv cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv \
  --out out/traffic_anomaly \
  --status "Green Termination" \
  --tau-global 0.0005
```

Notes:
- The anomaly subset typically spreads mass across many elements; **0.005 can exclude everything** on the bundled CSV.
- Add `--status "<value>"` multiple times to include multiple status texts.
