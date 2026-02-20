# Vector DB coherence (from retrieval results)

This adapter turns **vector retrieval results** into a HUF run so you can audit:

- which groups / “regimes” dominate the result set,
- which items are retained vs discarded (and why),
- how much probability mass lives in the long tail.

It does **not** require a live vector database. You provide a **JSONL export** of retrieval results.

---

## When to use this

Use this when you want to answer questions like:

- “Are my search results dominated by one namespace / one source?”
- “Do I have a few regimes that explain most of the mass (concentration)?”
- “What’s in the long tail after I apply a threshold or retained target?”
- “If I filter to an exception (one namespace), does the ranking change?”

This pairs naturally with the **long tail (accounting lens)** idea: baseline result-set → filtered/exception result-set → ranked variance review.

---

## Input format (JSONL)

One JSON object per line.

### Required fields

- `id` (string): unique item id (document id, chunk id, ticket id, etc.)
- `score` (number): similarity / relevance score (**higher = better**)

### Optional fields

You can include any grouping fields you want to treat as regimes, e.g.:

- `namespace`
- `collection`
- `source`
- `tenant`
- `index`

Example (`cases/vector_db/inputs/retrieval.jsonl`):

```json
{"id":"doc_001","score":0.82,"namespace":"kb","source":"handbook"}
{"id":"doc_002","score":0.63,"namespace":"kb","source":"manual"}
{"id":"doc_101","score":0.77,"namespace":"tickets","source":"ops"}
{"id":"doc_102","score":0.12,"namespace":"tickets","source":"ops"}
```

---

## Run (Windows PowerShell)

PowerShell note: use **backticks** for line continuation (not `\`).

This example uses `namespace` as the regime field.

```powershell
$py  = ".\.venv\Scripts\python.exe"
$in  = "cases/vector_db/inputs/retrieval.jsonl"
$out = "out/vector_db_demo"

New-Item -ItemType Directory -Force (Split-Path $in) | Out-Null
New-Item -ItemType Directory -Force $out | Out-Null

@'
{"id":"doc_001","score":0.82,"namespace":"kb","source":"handbook"}
{"id":"doc_002","score":0.63,"namespace":"kb","source":"manual"}
{"id":"doc_101","score":0.77,"namespace":"tickets","source":"ops"}
{"id":"doc_102","score":0.12,"namespace":"tickets","source":"ops"}
'@ | Set-Content -Encoding utf8 $in

& $py examples/run_vector_db_demo.py `
  --in $in `
  --out $out `
  --tau-global 0.02 `
  --regime-field namespace

dir $out
```

If your repo uses a different adapter entrypoint, run:

```powershell
.\.venv\Scripts\python -m pip show huf_core
.\.venv\Scripts\huf --help
```

…and use the adapter that matches your install.

---

## Run (macOS / Linux)

```bash
./.venv/bin/python examples/run_vector_db_demo.py --in cases/vector_db/inputs/retrieval.jsonl --out out/vector_db_demo --tau-global 0.02 --regime-field namespace
```

---

## What to open first (artifacts)

In `out/vector_db_demo/`:

1) `artifact_1_coherence_map.csv` — **Which regimes dominate?** (sorted by `rho_global_post`)
2) `artifact_2_active_set.csv` — retained items with global + local shares (`rho_*`)
3) `artifact_3_trace_report.jsonl` — per-item reasoning: pre/post mass, exclusions, ranks
4) `artifact_4_error_budget.json` — how much mass you discarded globally

A good first question:

- “How many items explain 90% of the retained mass?”

That’s the same concentration headline used in the long-tail demo.

---

## Example output interpretation (screenshot-style walkthrough)

Think of this as “what you’d point at on a screenshot” when teaching someone how to read the artifacts.

### Step 0 — sanity check (folder has the contract)
In File Explorer (or `dir`), confirm you see at least:

- `artifact_1_coherence_map.csv`
- `artifact_2_active_set.csv`
- `artifact_4_error_budget.json`

If any are missing, treat the run as **not comparable**.

### Step 1 — open `artifact_1_coherence_map.csv` (the regime ranking)

Open the CSV in Excel. You’re looking for a table that feels like:

```
regime_id          rho_global_post   rho_global_pre   ... (discard columns)
namespace=kb       0.61              0.58
namespace=tickets  0.39              0.42
...
```

**What to do (Excel “screenshot steps”):**

1. Click the header row.
2. Turn on a filter (Data → Filter).
3. Sort **descending** by `rho_global_post`.

**What that means:**

- `regime_id` (or `regime_label`) is the group you chose (e.g., `namespace=...`).
- `rho_global_post` is **share after pruning + renormalization**.
- `rho_global_pre` (if present) is **share before pruning**.

**What to look for (the “aha” moments):**

- **Dominance:** does the top regime have >0.50 share?
  - If yes, your retrieval results are heavily dominated by that group.
- **Concentration:** do the top 3 regimes cover most of the mass?
  - Add a temporary Excel column: cumulative sum of `rho_global_post`.
- **Tail cut:** if you have a discarded column (names vary), does one regime lose much more than others?
  - That regime is where the “borderline” results live.

**If you only read one artifact first, read this one.**
It answers: “Who dominated my result set?”

### Step 2 — open `artifact_2_active_set.csv` (the retained items)

Now open the active set. It will feel like:

```
item_id   regime_id           rho_global_post  rho_local_post  score  ...
doc_001   namespace=kb        0.092            0.151           0.82
doc_101   namespace=tickets   0.087            0.224           0.77
...
```

**What to do (Excel “screenshot steps”):**

1. Filter/sort descending by `rho_global_post`.
2. Then sort descending by `rho_local_post` (within the top regime).

**What those columns mean:**

- `rho_global_post` → “How important is this item overall (after pruning)?”
- `rho_local_post` → “How dominant is this item inside its regime?”
  - This is the “top hits inside namespace=kb”.

**Two useful reads:**

- **Global triage list:** sort by `rho_global_post` and take the top 20.
  - That’s your “review list” across all namespaces.
- **Within-regime triage:** filter to one `regime_id` and sort by `rho_local_post`.
  - That’s “what dominates inside this namespace.”

### Step 3 — the “90% coverage” headline (concentration in one number)

This is the same “proof line” used in the long-tail demo.

In Excel:

1. Sort active set by `rho_global_post` descending.
2. Add a cumulative sum column.
3. Find the first row where cumulative sum ≥ 0.90.

That row number is **items_to_cover_90pct**.

Interpretation:

- smaller number → more concentrated (fewer items explain most mass)
- bigger number → more diffuse (mass spread across many results)

### Step 4 — cross-check discarded budget (`artifact_4_error_budget.json`)

Open the JSON. Look for a key like:

- `discarded_budget_global`

Interpretation:

- near 0.00 → you retained almost everything (little pruning)
- larger → pruning is doing real work (be deliberate about `tau` / targets)

---

## Quick dashboard (no notebooks)

Inspect any output folder:

```powershell
.\.venv\Scripts\python scripts/inspect_huf_artifacts.py --out out/vector_db_demo
```

Backward-compatible alias (older docs links):

```powershell
.\.venv\Scripts\python scripts/inspect_vector_db_artifacts.py --out out/vector_db_demo
```

The inspector prints:

- top regimes by `rho_global_post` (top 10)
- items-to-cover-90%
- discarded budget (if present)

---

## Common issues

### “Unexpected UTF-8 BOM …” (Windows)

Some editors save JSONL/CSV with a UTF-8 BOM. Prefer BOM-tolerant readers (recommended),
or rewrite without BOM:

```powershell
$content = Get-Content $in -Raw
[System.IO.File]::WriteAllText($in, $content, (New-Object System.Text.UTF8Encoding($false)))
```

### “My scores are distances (lower is better)”

HUF assumes higher score = better. If your tool emits distance where lower is better, transform it first, e.g.:

- `score = 1 / (1 + distance)`
- or `score = -distance` (if negative values are acceptable for your adapter)

Keep the transform explicit so your audit trail stays honest.

### “My regimes are too coarse / too fine”

Try a different `--regime-field`:

- coarse: `tenant`
- medium: `namespace`
- fine: `namespace + source` (if your adapter supports multi-field regime labels)

A good rule: choose the regime label that matches *how you’d triage the results*.

---

## Why this fits the HUF model

Vector retrieval results are inherently long-tailed:

- a few results get most of the score mass,
- many results sit near a “maybe” boundary,
- filtering (namespace, tenant) can reweight the distribution non-linearly.

HUF makes that auditable by forcing:

- a declared unity budget,
- explicit discards (error budget),
- and a trace report (provenance).
