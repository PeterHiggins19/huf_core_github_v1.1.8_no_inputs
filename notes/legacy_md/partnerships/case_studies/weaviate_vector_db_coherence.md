# Weaviate — Vector DB coherence case study

This case study is designed as a **linkable context page** for a PR/email.

!!! note "Time sensitivity"
    Names, partner programs, and priorities can change. Treat contact details as examples and verify current contacts.

---

## Read the full HTML case study

- `partnerships/case_studies/weaviate_vector_db_coherence_full.html`

---

## The runnable demo (two commands)

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

What to expect:

- a regime ranking (`artifact_1_coherence_map.csv`)
- a ranked review list (`artifact_2_active_set.csv`)
- a trace report (`artifact_3_trace_report.jsonl`)
- an error budget (`artifact_4_error_budget.json`)
- plus `items_to_cover_90pct` printed to console

---

## What this proves

1) **Dominance**: which namespace/collection supplies most mass  
2) **Concentration**: how many items explain 90% of mass (`items_to_cover_90pct`)  
3) **Declared discards**: what got dropped, explicitly (error budget + trace)

This is “retrieval observability” in artifact form.
