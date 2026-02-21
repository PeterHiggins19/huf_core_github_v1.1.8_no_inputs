# Weaviate × HUF — the full picture

This is a *technical explainer you can link in an email* alongside the PR.  
It answers four questions in order:

1) **What Weaviate is** (what a vector database actually does)  
2) **The gap** (what retrieval metrics miss in multi‑source deployments)  
3) **Why HUF** (audit layer: dominance + concentration + declared discards)  
4) **The export** (what to export, the one transform, and what artifacts mean)

---

## Read the visual one‑pager (HTML)

If you want the “diagram + bars + story” version:

- `partnerships/weaviate_full_picture.html`

(That file is included in the repo and served by MkDocs as a static asset.)

---

## Part 1 — What Weaviate actually is

Vector DBs store **objects and vectors together** and retrieve by semantic similarity.  
In RAG, the top‑k retrieved chunks become the LLM context window.

In real deployments, retrieval often spans multiple *sources* (collections, namespaces, tenants, “indexes”, etc.).  
That’s where audits matter.

---

## Part 2 — The gap (silent dominance)

Weaviate (and most vector DBs) return item scores, and you can track latency and ranking metrics.

But they don’t natively answer:

- **Which source dominated** after retrieval ran?
- **How concentrated** is the result mass (one number)?
- **What got dropped** below a boundary — explicitly, as a ledger?

It’s possible for headline metrics to look “green” while one namespace supplies most results.

---

## Part 3 — Why HUF (audit layer)

HUF is **not** a replacement for Weaviate.

HUF takes an offline export of retrieval output and writes **contract artifacts**:

- **artifact_1_coherence_map.csv** — regime ranking (`rho_global_post`)
- **artifact_2_active_set.csv** — ranked review list (global + within‑regime)
- **artifact_3_trace_report.jsonl** — “workpapers” / provenance trace
- **artifact_4_error_budget.json** — explicit discard ledger

One headline users remember:

> `items_to_cover_90pct = k`  
> The top **k** retained items explain **90%** of post‑normalized mass.

---

## Part 4 — The export (what HUF needs)

HUF input is JSONL:

- One JSON object per line
- Required fields: `id`, `score` (higher = better)
- Optional: grouping fields like `namespace`, `collection`, `tenant`, `source`

Distance metrics? Convert once:

- `score = 1 / (1 + distance)`

---

## Two‑command demo (Windows / PowerShell)

```powershell
$py = ".\.venv\Scripts\python.exe"
$in = "cases/vector_db/inputs/retrieval.jsonl"
$out = "out/vector_db_demo"

& $py examples/run_vector_db_demo.py `
  --in $in `
  --out $out `
  --tau-global 0.02 `
  --regime-field namespace

& $py scripts/inspect_huf_artifacts.py --out $out
```

Expected shape:

```text
[tail] items_to_cover_90pct=3

Top regimes by rho_global_post:
  1. kb       rho_post=0.619658
  2. tickets  rho_post=0.380342
```

---

## Optional: plots (if you want visuals)

If you installed the plotting helper, you can generate:

- coherence bar chart by regime
- concentration curve

```powershell
& $py -m pip install matplotlib
& $py scripts/plot_huf_artifacts.py --out $out
```

Outputs land under:

- `out/vector_db_demo/plots/`
