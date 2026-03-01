HUF-DOC: HUF.REL.DOCS.PAGE.DATA_SOURCES | HUF:1.1.8 | DOC:v0.1.0 | STATUS:release | LANE:release | RO:Peter Higgins
CODES: DOCS, DATA | ART: CM, AS, TR, EB | EVID:E2 | POSTURE:OP | WEIGHTS: OP=0.80 TOOL=0.20 PEER=0.00 | CAP: OP_MIN=0.51 TOOL_MAX=0.49 | CANON:docs/data_sources.md

# Data sources (real, public)

HUF reference cases ship **artifacts** (CSV/JSONL/plots) but **do not bundle large upstream datasets**.

- Keeps downloads small.
- Avoids redistributing large binaries.
- Lets you pull the freshest copy directly from the public source.

## What is (and isn’t) synthetic
- **Worked cases (Planck / Markham / Toronto)**: **real** public data.
- **Toy examples** (if any): small synthetic vectors strictly for smoke-testing core logic, always labeled.

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

---

## Automation helper (GitHub package)

If you are using the separate **GitHub package** distribution, it includes a fetch helper:

```bash
python scripts/fetch_data.py (from the GitHub package) --markham --toronto
python scripts/fetch_data.py (from the GitHub package) --planck-guide
```

The docs-only bundle does not include that script, but the inputs and paths are identical.

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


### Non-interactive Toronto fetch (`--yes`)

If you want a **non-interactive** run (e.g., CI or scripted demos), use `--yes` to auto-select the top matching Toronto resource:

```bash
python scripts/fetch_data.py (from the GitHub package) --toronto --yes
```

If the auto-selected resource isn’t the dataset you want, rerun without `--yes` to pick from the list interactively.

