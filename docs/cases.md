# Included Cases

This repo ships a small set of real-world case folders under `cases/`.

- `cases/markham2018/` — Markham 2018 budget allocation (**real** workbook; traces include spreadsheet cell refs). **Input workbook not bundled**.
- `cases/traffic_phase/` — Toronto traffic phase-band compression (**real** CSV snapshot). **Input CSV not bundled**.
- `cases/traffic_anomaly/` — Toronto traffic anomaly diagnostic (same **real** CSV snapshot, conditional budgets). **Input CSV not bundled**.
- `cases/planck70/` — Planck LFI 70 GHz (**real** mission data). **Input FITS not bundled** (large).

Each case folder contains the HUF artifacts and a `meta.json` describing provenance, expected inputs, and public data sources.

See `data_sources.md` for where to download the upstream inputs.
