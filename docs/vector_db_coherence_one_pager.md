# Vector DB coherence (one-page brief)

> **No live vector DB required:** export retrieval results (JSONL/CSV/TSV) and audit **composition**.

## What you get

A repeatable audit that shows:

- which regimes dominate (`rho_global_post`)
- how concentrated the kept set is (`items_to_cover_90pct`)
- what was discarded (error budget)

## Artifacts (open in this order)

1) `artifact_1_coherence_map.csv` — regime ranking  
   Sort by `rho_global_post` ⇒ which regimes dominate
2) `artifact_2_active_set.csv` — ranked review list  
   Sort by `rho_global_post` ⇒ which items matter most overall
3) `artifact_4_error_budget.json` — declared discards  
   Look for `discarded_budget_global`

## 60-second run (Windows / repo venv)

```powershell
$py  = ".\.venv\Scripts\python.exe"
$in  = "cases/vector_db/inputs/retrieval.jsonl"
$out = "out/vector_db_demo"

& $py examples/run_vector_db_demo.py `
  --in $in `
  --out $out `
  --tau-global 0.02 `
  --regime-field namespace

& $py scripts/inspect_huf_artifacts.py --out $out
```

## Two-tau headline (optional)

```powershell
$out = "out/vector_db_delta"
& $py scripts/run_vector_db_concentration_delta.py `
  --in $in `
  --out $out `
  --tau-a 0.005 `
  --tau-b 0.02 `
  --regime-field namespace
```

Example:

```text
Concentration increased: items_to_cover_90pct 37 -> 12
```
