# Vector DB coherence (from retrieval results)

This adapter turns **vector retrieval results** into a HUF run so you can audit:

- which groups / “regimes” dominate the result set,
- which items are retained vs discarded (and why),
- how much probability mass lives in the long tail.

It does **not** require a live vector database. You provide a **JSONL export** of retrieval results.

!!! warning "PowerShell vs Python: run commands in the shell"
    If your prompt looks like `>>>`, you are **inside Python**.  
    Exit back to PowerShell with **`exit()`** or **Ctrl+Z then Enter**, then run the commands below.

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

---

## Quick dashboard (no notebooks)

Inspect the output folder:

```powershell
.\.venv\Scripts\python scripts/inspect_huf_artifacts.py --out out/vector_db_demo
```

Backward-compatible alias:

```powershell
.\.venv\Scripts\python scripts/inspect_vector_db_artifacts.py --out out/vector_db_demo
```

Expected console output looks like:

```
[tail] items_to_cover_90pct=3

Top regimes by rho_global_post:
  1. kb       rho_post=0.619658
  2. tickets  rho_post=0.380342
```

Interpretation (in plain English):

- `kb` dominates the result mass (~62%) but `tickets` is still significant (~38%).
- `items_to_cover_90pct=3` means the **top 3 retained items explain 90%** of the post-normalized mass → **high concentration**.

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
kb                 0.619658          0.????
tickets            0.380342          0.????
...
```

**What to do (Excel “screenshot steps”):**

1. Click the header row.
2. Turn on a filter (Data → Filter).
3. Sort **descending** by `rho_global_post`.

**What to look for:**

- **Dominance:** does the top regime have >0.50?
- **Concentration across regimes:** do the top 2–3 regimes cover most of the mass?
- **Tail cut:** if there’s a discarded column (names vary), did one regime lose a lot more?

This artifact answers: **“Which groups dominate my retrieval results?”**

### Step 2 — open `artifact_2_active_set.csv` (the retained items)

Now open the active set. It will feel like:

```
item_id   regime_id   rho_global_post  rho_local_post  score  ...
doc_001   kb          0.09             0.15            0.82
doc_101   tickets     0.08             0.22            0.77
...
```

**How to read it:**

- Sort by `rho_global_post` → your global “review list”
- Filter to one `regime_id` and sort by `rho_local_post` → “top hits inside this regime”

### Step 3 — the “90% coverage” headline (concentration in one number)

In Excel:

1. Sort active set by `rho_global_post` descending.
2. Add a cumulative sum column.
3. Find the first row where cumulative sum ≥ 0.90.

That row number is **items_to_cover_90pct**.

---

## Common issues

### “I typed `huf traffic ...` and got `SyntaxError`”

If you see this:

- `>>> huf traffic ...`
- `SyntaxError: invalid syntax`

…it means you typed a **shell command inside Python**.

Fix: exit Python (`exit()`), then run the command in PowerShell:

```powershell
.\.venv\Scripts\huf traffic --csv cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv --out out/traffic_phase
```

### “My scores are distances (lower is better)”

HUF assumes higher score = better. If your tool emits distance where lower is better, transform it first, e.g.:

- `score = 1 / (1 + distance)`
- or `score = -distance` (if negative values are acceptable for your adapter)

Keep the transform explicit so your audit trail stays honest.

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
