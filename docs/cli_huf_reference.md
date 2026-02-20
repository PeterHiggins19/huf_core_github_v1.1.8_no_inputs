# CLI: HUF command lists, labels, terminology

This page is a “single place” to answer:
- what commands exist,
- what files they expect,
- what artifacts they emit,
- and what words mean (regime, τ, active set…).

## Run commands in the shell (PowerShell), not inside Python

If your prompt looks like this:

- `>>>`

…you are inside the Python REPL. Shell commands like `huf ...` will fail with `SyntaxError`.

Exit back to PowerShell:

- type `exit()` **or**
- press **Ctrl+Z** then **Enter**

Then run commands like:

```powershell
.\.venv\Scripts\huf --help
```

## Windows/Conda rule (copy/paste reliability)

After the repo venv exists, **always** run tools via the repo executables:

```powershell
.\.venv\Scripts\python -V
.\.venv\Scripts\huf --help
.\.venv\Scripts\python -m mkdocs serve
```

For file paths inside commands and docs, prefer **forward slashes**:
- ✅ `scripts/fetch_data.py`
- ✅ `cases/traffic_phase/inputs/...`
- Only use backslashes for the venv executables: `.\.venv\Scripts\python`

## Discover commands (don’t guess)

Canonical command lists come from `--help`:

```powershell
.\.venv\Scripts\huf --help
.\.venv\Scripts\huf traffic --help
.\.venv\Scripts\huf traffic-anomaly --help
```

If a flag name differs between versions, **trust `--help`** over any doc page.

## Planck guide (Windows)

There is no `make` on Windows. Print the Planck download guide like this:

```powershell
.\.venv\Scripts\python scripts/fetch_data.py --planck-guide
```

Then run Planck after placing the FITS and installing `astropy` in the **same venv**:

```powershell
.\.venv\Scripts\python -m pip install astropy
.\.venv\Scripts\huf planck --fits "cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits" --out out/planck70 --retained-target 0.97 --nside-out 64
```

## Output artifacts (the contract)

Every valid HUF run emits the “contract artifacts” in the run output folder:

- `artifact_1_coherence_map.csv` — “Where the budget went” by regime (ranked)
- `artifact_2_active_set.csv` — retained items with global + local shares
- `artifact_3_trace_report.jsonl` — line-by-line trace records (provenance)
- `artifact_4_error_budget.json` — explicit discarded budget + diagnostics

If any of these are missing, treat the run as **non-auditable**.
