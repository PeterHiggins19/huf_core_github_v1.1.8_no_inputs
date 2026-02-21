# Partner playbook

This is the repeatable process to “disseminate HUF” in partner ecosystems without relying on meetings.

---

## 1) Pick the regime field

Your partner will already have a natural grouping field:

- `namespace` (multi-tenant VDB)
- `collection` (collection-based VDB)
- `tenant` (explicit tenant isolation)
- `source` / `connector` (enterprise search)

HUF uses this as `--regime-field`.

---

## 2) Export retrieval (or events) to JSONL

HUF input is JSONL:

- one JSON object per line
- required: `id`, `score` (higher = better)
- optional: `namespace`/`collection`/`tenant`/`source` + any metadata you want in the trace

Distance metrics? Convert once:

`score = 1 / (1 + distance)`

---

## 3) Run in two commands (Windows-safe)

```powershell
$py  = ".\.venv\Scripts\python.exe"
$in  = "cases/vector_db/inputs/retrieval.jsonl"
$out = "out/partner_demo"

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

## 4) Produce the “proof line”

People repeat a single number.

Run two tau settings and print:

`Concentration increased: items_to_cover_90pct X -> Y`

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

---

## 5) Publish the case study

A partner-ready page should always contain:

- the problem (dominance + concentration + discards)
- the two commands
- the four artifacts and how to interpret them
- what changed after adjusting tau (proof line)
- links to the repo + docs

---

## 6) Outreach sequence

1) **Open PR**
2) Post PR link to partner community channel
3) Send short email (PR link first paragraph)
4) Follow up once after 5–7 business days

Keep everything “artifact-first”.
