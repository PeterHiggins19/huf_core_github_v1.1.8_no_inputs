# Higgins Unity Framework (HUF)

Normalization-invariant audit layer for hierarchical mixtures (regimes/tenants/sources).

**PROOF (fast intuition):** `items_to_cover_90pct 37 -> 12` when switching **baseline -> exception view** on the same dataset (see the 2-minute demo below).

Docs: https://peterhiggins19.github.io/huf_core/  
Repo: https://github.com/PeterHiggins19/huf_core

---

## What HUF outputs (artifact-first)

Every run writes review-first artifacts you can diff, email, and audit:

- **Coherence map** (`artifact_1_coherence_map.csv`) -- where the mass is (ranked regimes)
- **Active set** (`artifact_2_active_set.csv`) -- retained items + global/local shares
- **Trace report** (`artifact_3_trace_report.jsonl`) -- provenance + "why it stayed"
- **Error budget** (`artifact_4_error_budget.json`) -- accounting of discards

Key intuition: if you discard tail mass and then re-normalize, the retained portion is scaled up. That can make "retained looks stronger" feel counter-intuitive until you read it as a conditional mixture.

---

## 2-minute long-tail demo (Windows / Conda copy-paste)

**What this demonstrates:** the same dataset can look "stable" in the baseline view, but become **more concentrated** in an exception-only view.

You will run:

1) **Traffic Phase** (baseline) -> writes to `out/traffic_phase_demo/`  
2) **Traffic Anomaly** (exception-only) -> writes to `out/traffic_anomaly_demo/`  
3) A console summary that prints:
   - top regimes changed (top 10 by `rho_global_post`)
   - **PROOF line**: `items_to_cover_90pct baseline -> exception`
   - discarded budget (if present)

Run these three commands from the repo root:

```powershell
python scripts/bootstrap.py
.\.venv\Scripts\python scripts/fetch_data.py --toronto --yes
.\.venv\Scripts\python scripts/run_long_tail_demo.py --status "Green Termination"
```

After it finishes, look for a line like:

- `PROOF: items_to_cover_90pct 37 -> 12`

Want a quick dashboard on any output folder?

```powershell
.\.venv\Scripts\python scripts/inspect_huf_artifacts.py --out out/traffic_anomaly_demo
```

Why this works (accounting mapping): baseline P&L -> exception-only P&L -> ranked variance review.  
See: `docs/long_tail_accounting_lens.md`

---

## Docs (local)

Always run MkDocs via the repo venv:

```powershell
.\.venv\Scripts\python -m mkdocs serve
```

Strict check:

```powershell
.\.venv\Scripts\python -m mkdocs build --strict
```

Pinned versions (in `pyproject.toml`):

- `mkdocs==1.6.1`
- `mkdocs-material==9.7.2`

If you see a warning about MkDocs 2.0, re-install the pinned versions:

```powershell
.\.venv\Scripts\python -m pip install "mkdocs==1.6.1" "mkdocs-material==9.7.2"
```

---

## Notes

- Partner-facing HTML lives under `notes/partner_html/` for email attachments and is not part of the MkDocs site.
- Canonical public docs are Markdown-only under `docs/`.
