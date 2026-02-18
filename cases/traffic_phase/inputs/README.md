# Inputs (Toronto traffic phase status)

This case uses City of Toronto traffic-signal **phase status** data.

In this repo snapshot, a representative CSV is already included at:

- `cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv`

You can replace it with your own export (just keep the same filename, or point `--csv` at your file).

See `DATA_SOURCES.md` (repo root) for catalogue links.

## Run
From the repo root:

```bash
huf traffic \
  --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv \
  --out out/traffic_phase
```

Optional threshold (default shown):

```bash
huf traffic --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv --out out/traffic_phase --tau-local 0.05
```
