# Data sources (real, public)

HUF reference cases ship **artifacts** (CSV/JSONL/plots) but **do not bundle large upstream datasets**.

- Keeps downloads small.
- Avoids redistributing large binaries.
- Lets you pull the freshest copy directly from the public source.

## What is (and isn’t) synthetic
- **Worked cases (Planck / Markham / Toronto)**: **real** public data.
- **Unit tests / toy examples**: may generate **small synthetic** vectors strictly for smoke-testing core logic. These are always labeled as toy/test data and never presented as “real runs.”

---

## One command for civic data (Markham + Toronto)

From the repo root:

```bash
make fetch-data
# or: python scripts/fetch_data.py --markham --toronto
```
### Non-interactive Toronto fetch (`--yes`)

If you want a **non-interactive** run (e.g., CI or scripted demos), use `--yes` to auto-select the top matching Toronto resource:

```bash
make fetch-toronto-yes
# or:
python scripts/fetch_data.py --toronto --yes
```

If the auto-selected resource isn’t the dataset you want, rerun without `--yes` to pick from the list interactively.


This downloads the **Markham** workbook and a **Toronto** traffic phase-status CSV into the expected `cases/*/inputs/` paths.

Planck remains manual (see below) because the FITS file is large.

---

## Planck (ESA / NASA) — PR3 all-sky maps

**Case(s):** `cases/planck70/`

**Input expected:**
- `cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits`

**Primary source (ESA):**
- Planck Legacy Archive (PLA): https://pla.esac.esa.int/

**Convenient mirror / direct download (NASA/IPAC IRSA):**
- PR3 all-sky maps landing page: https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/
- Preview page (contains a “Download HEALPix FITS file” link): https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/previews/LFI_SkyMap_070_1024_R3.00_full/index.html
- Direct file URL (large binary): https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/LFI_SkyMap_070_1024_R3.00_full.fits

**Notes:**
- This FITS is large (~480–500 MB). It is intentionally excluded from distributions.
- The HUF Planck adapter expects **NESTED** ordering and uses the **I_STOKES** field by default.

Tip: print a guided/manual flow (including a ready-to-run `curl` command) with:

```bash
make planck-guide
# or: python scripts/fetch_data.py --planck-guide
```

---

## City of Markham (Ontario) — 2018 corporate-wide budget workbook

**Case(s):** `cases/markham2018/`

**Input expected:**
- `cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx`

**Source:**
- Direct XLSX: https://maps.markham.ca/OpenDataSite_Tables/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx
- Markham Open Data portal: https://data-markham.opendata.arcgis.com/

**Notes:**
- The Markham adapter traces retained elements back to **sheet + cell references** in the workbook.

---

## City of Toronto (Ontario) — traffic signal phase status

**Case(s):** `cases/traffic_phase/`, `cases/traffic_anomaly/`

**Input expected:**
- `cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv`
- `cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv`

**Source:**
- City of Toronto Open Data portal: https://open.toronto.ca/

**Notes:**
- This input may vary in size depending on the export window. It is intentionally excluded.
- The Traffic adapters treat **(TCS × PHASE_BAND)** as verifiable finite elements and can optionally restrict to anomaly subsets.
- The automated fetcher uses the portal’s public CKAN Action API endpoint:
  - https://open.toronto.ca/api/3/action/

---

## Recommended local layout

```text
cases/
  planck70/
    inputs/
      LFI_SkyMap_070_1024_R3.00_full.fits
  markham2018/
    inputs/
      2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx
  traffic_phase/
    inputs/
      toronto_traffic_signals_phase_status.csv
  traffic_anomaly/
    inputs/
      toronto_traffic_signals_phase_status.csv
```

If you prefer a different location or filename, pass `--csv` / `--xlsx` / `--fits` in the CLI.
