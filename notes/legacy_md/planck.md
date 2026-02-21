# Planck 70 GHz worked example

This example runs HUF on a real scientific dataset (a Planck 70 GHz sky map in FITS format).

## Why run this

- Demonstrates the pipeline on **non‑toy data**.
- Produces artifacts you can inspect (and plot) to confirm you’re looking at real structure rather than a “demo UI”.

## What you need

- A working virtual environment (`.venv`) with HUF installed.
- The FITS input file:

  - `cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits`

- `astropy` (for FITS I/O):

=== "Windows"

    ```powershell
    & .\.venv\Scripts\python.exe -m pip install astropy
    ```

=== "macOS / Linux"

    ```bash
    ./.venv/bin/python -m pip install astropy
    ```

## Run

=== "Windows (PowerShell)"

    ```powershell
    .\.venv\Scripts\huf.exe planck `
      --fits "cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits" `
      --out "out/planck70" `
      --retained-target 0.97 `
      --nside-out 64
    ```

=== "macOS / Linux (bash/zsh)"

    ```bash
    ./.venv/bin/huf planck \
      --fits "cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits" \
      --out "out/planck70" \
      --retained-target 0.97 \
      --nside-out 64
    ```

### What you should see

A successful run prints a short summary like:

```text
[done] planck -> out\planck70 | active_set=18198 coherence_rows=12 discarded_global=0.0299995
       dataset_id: 1494a5d87d37b5b3
       tau: 1.6627253164644175e-06
       retained_target: 0.97
       nside_out: 64
```

## Inspect the artifacts

**Important:** don’t paste raw Python (`import ...`, `print(...)`) directly into PowerShell.

- In PowerShell you’re still in the shell, not Python.
- Use the inspection script instead.

=== "Windows (PowerShell)"

    ```powershell
    $py = ".\\.venv\\Scripts\\python.exe"
    & $py scripts/inspect_huf_artifacts.py --out out/planck70
    ```

=== "macOS / Linux (bash/zsh)"

    ```bash
    ./.venv/bin/python scripts/inspect_huf_artifacts.py --out out/planck70
    ```

What you should see:

- The output folder path
- A small “tail” headline (e.g., `items_to_cover_90pct=...`)
- A ranked list of regimes by `rho_global_post`

## Optional plots

If you want charts, install matplotlib and generate plots from the artifact CSVs:

=== "Windows"

    ```powershell
    & .\.venv\Scripts\python.exe -m pip install matplotlib
    & .\.venv\Scripts\python.exe scripts/plot_huf_artifacts.py --out out/planck70
    ```

=== "macOS / Linux"

    ```bash
    ./.venv/bin/python -m pip install matplotlib
    ./.venv/bin/python scripts/plot_huf_artifacts.py --out out/planck70
    ```

This writes images under:

- `out/planck70/plots/`

