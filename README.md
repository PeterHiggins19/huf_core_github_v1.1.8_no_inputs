# HUF System (Markdown-only, docs + cases)

This package is the **HUF system without the GitHub codebase**:

## New to GitHub?

If you’re starting from **zero GitHub knowledge**, begin here:

- **Start here (Markdown):** `docs/start_here.md`
- **Start here (Markdown record copy):** `docs/start_here.md`

One‑click setup scripts (in repo root):

- Windows: `START_HERE_WINDOWS.bat`
- macOS: `START_HERE_MAC.command`
- Linux: `start_here_linux.sh`

These will create a local Python environment, install dependencies, and fetch **Markham + Toronto** inputs.
Planck is guided/manual because the FITS files are very large.

1) **Handbook**: `docs/handbook.md`
2) **Reference Manual**: `docs/reference_manual.md`
3) **Cases**: `cases/*` (reference artifacts + run stamps + meta)

## Markdown exports (record-keeping)

For users who aren’t GitHub-native, this release also includes **Markdown** copies of the key docs:

- `docs/handbook.md`
- `docs/reference_manual.md`
- `docs/data_sources.md`
- `docs/gui_quickstart.md`

These are generated from the Markdown sources and intended for record retention and offline sharing.

## GUI Quickstart

If you prefer GUI tools (Word/Excel, GitHub Desktop), start with:
- `docs/gui_quickstart.md`

## Inputs policy
Upstream inputs (Planck FITS / Markham workbook / Toronto traffic CSV) are **real public data** but are **not bundled**.

See `DATA_SOURCES.md` for where to download them and the exact expected paths.

## GitHub package (library + CLI)
The codebase is distributed separately as a “GitHub package” zip (or via the actual repo). Use it if you want to run the demos or build new adapters.
