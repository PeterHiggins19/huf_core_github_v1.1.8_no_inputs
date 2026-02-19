# Planck (LFI 70 GHz) demo

This case demonstrates HUF on a very large **HEALPix all‑sky map** (Planck PR3, LFI 70 GHz). The demo produces the standard HUF artifacts (coherence map, active set, trace report, error budget) so you can inspect **what HUF retained vs. discarded** at the chosen retained‑target.

!!! note "Why this is not auto-downloaded"
    The Planck FITS file is large (~480–500 MB) and some users prefer downloading from ESA’s Planck Legacy Archive vs NASA/IPAC IRSA.

## 1) Get the FITS input

Expected path in this repo:

```
cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits
```

### Option A (recommended on Windows): BITS download

```powershell
$dest = Join-Path $PWD "cases\planck70\inputs\LFI_SkyMap_070_1024_R3.00_full.fits"
New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
$src  = "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/LFI_SkyMap_070_1024_R3.00_full.fits"
Start-BitsTransfer -Source $src -Destination $dest
```

### Option B: curl/wget

```bash
curl -L -o "cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits"   "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/LFI_SkyMap_070_1024_R3.00_full.fits"
```

!!! warning "Windows PowerShell curl alias"
    In **Windows PowerShell**, `curl` is an alias for `Invoke-WebRequest`.
    Use `curl.exe` (or use BITS above):

    ```powershell
    curl.exe -L -o "cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits"       "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/LFI_SkyMap_070_1024_R3.00_full.fits"
    ```

Preview page (manual download button):

- https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/previews/LFI_SkyMap_070_1024_R3.00_full/index.html

## 2) Install Planck extras

If you are using the repo venv:

```powershell
.\.venv\Scripts\python -m pip install astropy
```

## 3) Run the demo

```powershell
.\.venv\Scripts\huf planck `
  --fits cases\planck70\inputs\LFI_SkyMap_070_1024_R3.00_full.fits `
  --out out\planck70 `
  --retained-target 0.97 `
  --nside-out 64
```

## 4) Read the artifacts

The output folder contains:

- `artifact_1_coherence_map.csv` — regimes and their retained mass/energy (post‑filter)
- `artifact_2_active_set.csv` — the retained items (ranked)
- `artifact_3_trace_report.jsonl` — what changed across the pass (debug/audit)
- `artifact_4_error_budget.json` — global + local discard summary
- `run_stamp.json`, `meta.json`

### Quick inspection (no notebooks required)

```powershell
.\.venv\Scripts\python - <<'PY'
import pandas as pd
coh = pd.read_csv('out/planck70/artifact_1_coherence_map.csv')
act = pd.read_csv('out/planck70/artifact_2_active_set.csv').sort_values('rank')
print('
Top regimes by rho_global_post:')
print(coh.sort_values('rho_global_post', ascending=False).head(10).to_string(index=False))
print('
Top 10 retained items:')
print(act[['rank','regime_id','item_id','value','rho_global_post','rho_local_post']].head(10).to_string(index=False))
PY
```

!!! tip "What to look for"
    * If **one regime dominates** the coherence map, it’s a sign the retained budget is concentrated.
    * If you want more/less sparsity, adjust `--retained-target` or `--nside-out`.
