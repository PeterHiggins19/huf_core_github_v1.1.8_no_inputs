# Vector DB coherence (from retrieval results)

This adapter turns **retrieval results** into a HUF run so you can audit **composition** (not just “quality”):

- **Regime dominance:** which namespace / collection / tenant / source dominates the kept set
- **Concentration:** do a few items explain most of the kept mass?
- **Declared discards:** what fell below threshold, and how much mass was discarded (no silent drops)
- **Trace:** why an item is retained (provenance + reasoning)

> No live vector DB required. You provide a JSONL/CSV/TSV export of retrieval results.

**Disambiguation:** this is *not* “ML class imbalance.”  
Here “long tail” means **mass distribution + exception reweighting** — the accounting move: baseline P&L → exception-only P&L → ranked variance review.

!!! warning "PowerShell vs Python: run commands in the shell"
    If your prompt looks like `>>>`, you are **inside Python**.  
    Exit back to PowerShell with **`exit()`** (or **Ctrl+Z then Enter**), then run the commands below.

---

## Start here

- **One-page brief:** `vector_db_coherence_one_pager.md`
- **This page:** full walkthrough + “what to look for” + future extension patterns

---

## Concepts

### Regimes

A **regime** is the grouping you care about: `namespace`, `collection`, `tenant`, `source`, etc.

You choose it via `--regime-field`.

### Tau (global threshold)

`--tau-global` sets the discard boundary in the **mass** frame.

- Larger `tau` = stricter threshold = more discards (often *more concentration*)
- Smaller `tau` = looser threshold = fewer discards (often *less concentration*)

### The proof line: items_to_cover_90pct

`items_to_cover_90pct = k` means:

> The **top k retained items** explain **90%** of the post-normalized mass.

Smaller `k` ⇒ more concentrated ⇒ a tiny set dominates retrieval.

---

## Input format (JSONL)

One JSON object per line.

### Required fields

- `id` (string): unique item id (document id, chunk id, ticket id, etc.)
- `score` (number): similarity / relevance score (**higher = better**)

### Optional fields (regimes)

Include any grouping fields you want to audit by, e.g.:

- `namespace`
- `collection`
- `source`
- `tenant`
- `index`

Example:

```json
{"id":"doc_001","score":0.82,"namespace":"kb","source":"handbook"}
{"id":"doc_002","score":0.63,"namespace":"kb","source":"manual"}
{"id":"doc_101","score":0.77,"namespace":"tickets","source":"ops"}
{"id":"doc_102","score":0.12,"namespace":"tickets","source":"ops"}
```

---

## 60-second run (Windows PowerShell)

PowerShell note: use **backticks** for line continuation (not `\`).

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

& $py scripts/inspect_huf_artifacts.py --out $out
```

---

## Two-tau delta (the repeatable headline)

Sometimes you want one line a teammate can repeat:

> **Concentration increased: items_to_cover_90pct X -> Y**

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

Example:

```text
Concentration increased: items_to_cover_90pct 37 -> 12
```

---

## Artifacts (the contract)

A valid run folder should contain at least:

- `artifact_1_coherence_map.csv` (regime ranking)
- `artifact_2_active_set.csv` (retained items)
- `artifact_4_error_budget.json` (declared discards)

Optional but strongly recommended:

- `artifact_3_trace_report.jsonl` (why retained)
- `meta.json`, `run_stamp.json`

---

## Example output interpretation (screenshot-style)

Think of this as “what you would circle in a screenshot.”

### 1) artifact_1_coherence_map.csv (regime ranking)

Open in Excel and sort **descending** by `rho_global_post`.

Look for:

- Top regime > 0.50 (dominance)
- Top 2–3 regimes cover most of the mass (regime concentration)

### 2) artifact_2_active_set.csv (ranked review list)

Sort **descending** by `rho_global_post`:

- This is your global “review list” (what actually matters).

Then filter by `regime_id` and sort by `rho_local_post`:

- Top items inside a regime.

### 3) artifact_4_error_budget.json (declared discards)

Look for:

- `discarded_budget_global` (or similarly named key)

Large discard means tau is aggressively pruning.

---

## Patterns you’ll care about later (future interest)

### Regime drift over time

Run the same query daily and watch:

- top regimes change
- `items_to_cover_90pct` trend down (concentration risk) or up (dispersion)

### Multi-tenant isolation checks

Use `--regime-field tenant` and look for:

- one tenant dominating another tenant’s query output

### CI guardrails

After any retrieval pipeline change:

- run coherence on a fixed set of queries
- fail if concentration spikes or a regime monopolizes results

### Accounting mapping

Treat regimes like cost centers:

- baseline P&L = full retrieval results
- exception-only P&L = tighter tau
- ranked variance review = active set sorted by `rho_global_post`

---

## Common issues

### “I typed `huf ...` and got SyntaxError”

If you see `>>>`, you’re inside Python. Exit with `exit()` and run in PowerShell.
