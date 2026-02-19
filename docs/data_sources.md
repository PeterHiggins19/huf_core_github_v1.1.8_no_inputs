\
# Data Sources & Fetching

This repo ships **small** inputs for Markham and Toronto examples via `scripts/fetch_data.py`.

Planck is intentionally **guide-only** because the file is ~480–500MB.

---

## Fetch the small inputs (recommended path)

```powershell
.\.venv\Scripts\python scripts/fetch_data.py --markham --toronto --yes
```

If you haven't created the venv yet, run:

```powershell
python scripts/bootstrap.py
```

---

## Markham (2018 budget)

Source: Markham Open Data / ArcGIS (the public portal link may change over time).

Expected local path in this repo:

`cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx`

Run:

```powershell
.\.venv\Scripts\huf markham --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out/markham2018
```

---

## Toronto traffic signals (phase status)

Expected local path:

`cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv`

Run:

```powershell
.\.venv\Scripts\huf traffic --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv --out out/traffic_phase
```

---

## Planck LFI 70 GHz (PR3) — guide only

Print the guide:

```powershell
.\.venv\Scripts\python scripts/fetch_data.py --planck-guide
```

The IRSA direct download URL referenced in the guide is:

`https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/LFI_SkyMap_070_1024_R3.00_full.fits`

### PowerShell note about `curl`

In **Windows PowerShell**, `curl` is an alias for `Invoke-WebRequest`, so `curl -L` fails.

Use `curl.exe`:

```powershell
curl.exe -L -o "cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits" "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/LFI_SkyMap_070_1024_R3.00_full.fits"
```

Or use BITS (recommended on Windows):

```powershell
$dest = Join-Path $PWD "cases\planck70\inputs\LFI_SkyMap_070_1024_R3.00_full.fits"
New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
$src  = "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/LFI_SkyMap_070_1024_R3.00_full.fits"
Start-BitsTransfer -Source $src -Destination $dest
```

---

## Docs preview

```powershell
.\.venv\Scripts\python -m mkdocs serve
```
