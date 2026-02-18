# Inputs (Planck LFI 70 GHz)

This case uses **real Planck mission data**. The input FITS file is large (~480–500 MB) and is **not included** in this distribution.

## Required file
Place the following file at:

- `cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits`

## Where to download
See `DATA_SOURCES.md` (repo root) for links and notes. (The IRSA preview page is usually the easiest path to the direct FITS download.)

## Run
From the repo root:

```bash
huf planck \
  --fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits \
  --out out/planck70
```

Optional knobs (defaults shown):

```bash
huf planck --fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits --out out/planck70 --retained-target 0.97 --nside-out 64
```

If the file is missing, the run should fail fast with an explicit “input not found” error.
