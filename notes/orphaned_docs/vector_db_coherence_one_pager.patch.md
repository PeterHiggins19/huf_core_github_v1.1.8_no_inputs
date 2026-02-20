## Two-tau concentration delta (proof line)

Sometimes you want one headline a teammate can repeat: *did concentration increase when we tightened tau?*

Run the coherence adapter twice and print the delta:

```powershell
$py  = ".\.venv\Scripts\python.exe"
$in  = "cases/vector_db/inputs/retrieval.jsonl"
$out = "out/vector_db_delta"

& $py scripts/run_vector_db_concentration_delta.py `
  --in $in `
  --out $out `
  --tau-a 0.005 `
  --tau-b 0.02 `
  --regime-field namespace
```

Example headline output:

```text
Concentration increased: items_to_cover_90pct 37 -> 12
```

Interpretation: fewer retained items explain 90% of the post-normalized mass (**more concentrated**).
