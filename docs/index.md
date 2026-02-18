# HUF Core

## Start here (GUI-friendly)

- **Download the latest release ZIP (recommended):**
  https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/releases/tag/HUF_v1.1.8

- **GUI Quickstart (read online):**
  https://raw.githubusercontent.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/main/docs/gui_quickstart.md

- **DOCX record copies (download):**
  - Handbook (DOCX): https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/raw/main/docs/handbook.docx
  - Reference Manual (DOCX): https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/raw/main/docs/reference_manual.docx
  - Data Sources (DOCX): https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/raw/main/docs/data_sources.docx
  - Start Here (DOCX): https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs/raw/main/docs/start_here.docx

---

## New to GitHub?

If you want **zero GitHub knowledge** and just want to run HUF:
1) Download the Release ZIP
2) Unzip it
3) Run `START_HERE_WINDOWS.bat`

# HUF Core (GUI-friendly)

Welcome. This repo is meant to be usable even if you’re **not GitHub-native**.

## Start here (Windows / GUI users)

**Option A — easiest (no Git required):**
- Go to **Releases** and download the latest ZIP.
- Unzip it.
- Double-click: `START_HERE_WINDOWS.bat`

**Option B — GitHub Desktop (recommended for updates):**
- Install GitHub Desktop
- Clone the repo
- Use **Fetch / Pull** to update, and **Commit / Push** to publish your edits.

➡️ **GUI Quickstart:**  
- [GUI Quickstart (read this first)](gui_quickstart.md)

## New to GitHub
- [New to GitHub (what the buttons mean)](new_to_github.md)

## Reference docs (Markdown)
- [Handbook](handbook.md)
- [Reference Manual](reference_manual.md)
- [Data sources (where the “real data” comes from)](data_sources.md)

## Record copies (DOCX for filing / compliance)
DOCX files live in the repo under `docs/`:
- `docs/handbook.docx`
- `docs/reference_manual.docx`
- `docs/data_sources.docx`

If you’re reading this on GitHub Pages, the easiest way to download the DOCX is:
- open the repo on GitHub → `docs/` folder → click the DOCX → download.

## Quick “I just want to run it”
After bootstrap:
- Markham:  
  `huf markham --xlsx cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out/markham2018`
- Toronto:  
  `huf traffic --csv cases/traffic_phase/inputs/totonto_traffic_signals_phase_status.csv --out out/traffic_phase`
- Planck guide:  
  `python scripts/fetch_data.py --planck-guide`
