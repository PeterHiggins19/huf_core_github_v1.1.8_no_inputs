# HUF Core Snapshot (v1.1.8)

This repo is a **runnable snapshot** of the Higgins Unity Framework (HUF) with:
- working demo cases (Markham, Toronto traffic, Planck),
- auditable artifacts (`out/*`),
- a MkDocs site (Material theme).

## Windows PowerShell quickstart (copy/paste)

From the repo root:

```powershell
# 1) Create + activate repo venv (recommended)
python -m venv .venv
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\python -m pip install -e .

# 2) Fetch bundled public datasets (Markham + Toronto)
.\.venv\Scripts\python scripts\fetch_data.py --markham --toronto --yes

# 3) Run cases
.\.venv\Scripts\huf markham --xlsx cases\markham2018\inputs\2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx --out out\markham2018
.\.venv\Scripts\huf traffic --csv cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_phase
.\.venv\Scripts\huf traffic-anomaly --csv cases\traffic_anomaly\inputs\toronto_traffic_signals_phase_status.csv --out out\traffic_anomaly --status "Green Termination" --tau-global 0.0005

# 4) Planck (manual download guide)
.\.venv\Scripts\python scripts\fetch_data.py --planck-guide
```

## Docs site (local)

```powershell
.\.venv\Scripts\python -m pip install mkdocs mkdocs-material
.\.venv\Scripts\python -m mkdocs serve
```

Open: http://127.0.0.1:8000/

## Read the artifacts

Start with:
- `artifact_1_coherence_map.csv` (who dominates)
- `artifact_2_active_set.csv` (retained items + shares)
- `artifact_3_trace_report.jsonl` (why)

## Vector DB coherence (optional)

See: `docs/vector_db_coherence.md`
