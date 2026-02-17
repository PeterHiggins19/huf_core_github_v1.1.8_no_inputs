# Inputs (not bundled)

This case uses **real Planck mission data**. The input FITS file is large (~480–500 MB) and is **not included** in this distribution.

## Required file
Place the following file at:

- `cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits`

## Where to download
Use either source (same data product):

- **ESA Planck Legacy Archive (PLA)**: browse/select the PR3 LFI 70 GHz all-sky map and download the FITS.
- **NASA/IPAC IRSA Planck Release 3**: direct download page for `LFI_SkyMap_070_1024_R3.00_full.fits`.

See `DATA_SOURCES.md` (repo root) for links and notes.

## After download
Run:

```bash
huf planck70 --input cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits
```

If the file is missing, the run should fail fast with an explicit “input not found” error.
