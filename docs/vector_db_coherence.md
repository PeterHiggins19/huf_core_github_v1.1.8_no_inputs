# Vector DB coherence (from retrieval results)

This is a **small adapter** that turns *vector retrieval results* into a HUF run so you can audit:
- which groups/“regimes” dominate the result set,
- which items are retained vs discarded (and why),
- how much probability mass lives in the long tail.

It does **not** require a live vector database. You provide a JSONL export of results.

## Input format (JSONL)

One JSON object per line:

```json
{"id":"doc_001","score":0.82,"namespace":"kb","source":"handbook"}
{"id":"doc_101","score":0.77,"namespace":"tickets","source":"ops"}
```

Required fields:
- `id` (string): unique item id
- `score` (number): similarity / relevance score (higher = better)

Optional fields:
- any grouping field you want to treat as a “regime”, e.g. `namespace`, `collection`, `source`

## Run (Windows PowerShell)

PowerShell note: **use backticks** for line continuation (not `\`).

```powershell
$py  = ".\.venv\Scripts\python.exe"
$in  = "cases\vector_db\inputs\retrieval.jsonl"
$out = "out\vector_db_demo"

New-Item -ItemType Directory -Force (Split-Path $in) | Out-Null
New-Item -ItemType Directory -Force $out             | Out-Null

@'
{"id":"doc_001","score":0.82,"namespace":"kb","source":"handbook"}
{"id":"doc_002","score":0.63,"namespace":"kb","source":"manual"}
{"id":"doc_101","score":0.77,"namespace":"tickets","source":"ops"}
{"id":"doc_102","score":0.12,"namespace":"tickets","source":"ops"}
'@ | Set-Content -Encoding utf8 $in

& $py examples\run_vector_db_demo.py `
  --in  $in `
  --out $out `
  --tau-global 0.02 `
  --regime-field namespace

dir $out
```

If you see: `Unexpected UTF-8 BOM ...`  
That means the file has a UTF-8 BOM. Either:
- keep the adapter BOM-tolerant (recommended), or
- rewrite the file without BOM:

```powershell
$content = Get-Content $in -Raw
[System.IO.File]::WriteAllText($in, $content, (New-Object System.Text.UTF8Encoding($false)))
```

## Run (Mac/Linux)

```bash
python examples/run_vector_db_demo.py   --in  cases/vector_db/inputs/retrieval.jsonl   --out out/vector_db_demo   --tau-global 0.02   --regime-field namespace
```

## What to open first (artifacts)

In `out/vector_db_demo/`:

1. `artifact_1_coherence_map.csv`  
   “Which regimes dominate?” (sorted by `rho_global_post`)

2. `artifact_2_active_set.csv`  
   The retained items with global + local shares (`rho_*`)

3. `artifact_3_trace_report.jsonl`  
   Per-item reasoning: pre/post mass, exclusions, ranks

Tip: For quick inspection without notebooks, use the helper script (if present):

```powershell
.\.venv\Scripts\python scripts\inspect_vector_db_artifacts.py --out out\vector_db_demo
```

!!! note "Windows JSONL + BOM"
    If you generate `retrieval.jsonl` using Windows PowerShell `Set-Content`, it may include a UTF‑8 BOM.
    HUF’s vector DB adapter reads JSONL using `utf-8-sig` so a BOM won’t break parsing.
