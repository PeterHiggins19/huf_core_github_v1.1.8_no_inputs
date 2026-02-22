# HUF Core Snapshot (v1.1.8)

**HUF is an artifact-first compression + audit framework for long-tail distributions** (budgets, logs, exceptions).

**Not ML class imbalance:** here â€œlong tailâ€ means **mass distribution + exception reweighting** (baseline vs filtered view).

It produces three â€œreview-firstâ€ artifacts on every run:

- **Coherence map** (`artifact_1_coherence_map.csv`) â€” *where the mass is* (ranked regimes)
- **Active set** (`artifact_2_active_set.csv`) â€” retained items + global/local shares
- **Trace report** (`artifact_3_trace_report.jsonl`) â€” provenance + â€œwhy it stayedâ€

Docs site: https://peterhiggins19.github.io/huf_core/

---

## 2â€‘minute long-tail demo (Windows/Conda copy/paste)

**What this demonstrates:** the same dataset can look â€œstableâ€ in the baseline view, but become **more concentrated** in an exception-only view â€” the practical long-tail story.

You will run:

1) **Traffic Phase** (baseline) â†’ writes to `out/traffic_phase_demo/`
2) **Traffic Anomaly** (exception-only) â†’ writes to `out/traffic_anomaly_demo/`
3) A console summary that prints:
   - top regimes changed (top 10 by `rho_global_post`)
   - **PROOF line**: `items_to_cover_90pct baseline -> exception`
   - discarded budget (if present)

Run these **three commands** from the repo root:

```powershell
python scripts/bootstrap.py
.\.venv\Scripts\python scripts/fetch_data.py --toronto --yes
.\.venv\Scripts\python scripts/run_long_tail_demo.py --status "Green Termination"
```

After it finishes, look for a line like:

- `PROOF: items_to_cover_90pct 37 -> 12`

Thatâ€™s the â€œrepeatable numberâ€ people cite: exception views often tighten into fewer items.

Want the quick dashboard on any folder?

```powershell
.\.venv\Scripts\python scripts/inspect_huf_artifacts.py --out out/traffic_anomaly_demo
```

**Why this works (accounting mapping):** baseline P&L â†’ exception-only P&L â†’ ranked variance review.  
See: `docs/long_tail_accounting_lens.md`

---

## Docs site (local)

Always run MkDocs via the repo venv:

```powershell
.\.venv\Scripts\python -m mkdocs serve
```

Strict check:

```powershell
.\.venv\Scripts\python -m mkdocs build --strict
```

### MkDocs versions (pinned)

This repo pins a stable docs stack in `pyproject.toml`:

- `mkdocs==1.6.1`
- `mkdocs-material==9.7.2`

If you see a warning about MkDocs 2.0, re-install the pinned versions:

```powershell
.\.venv\Scripts\python -m pip install "mkdocs==1.6.1" "mkdocs-material==9.7.2"
```
