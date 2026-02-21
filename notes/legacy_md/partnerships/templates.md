# Outreach templates

These are intentionally short. The PR is the proof artifact; the message just points to it.

---

## PR title

`feat: HUF coherence adapter — retrieval audit for <Partner> exports (dominance + concentration + declared discards)`

---

## PR description

- Adds a minimal example showing how to run a **HUF coherence audit** on exports  
- Answers: *dominant regimes*, *concentration (`items_to_cover_90pct`)*, *declared discards (error budget)*  
- No live connection required — JSONL in, HUF artifacts out  

Two-command demo (Windows-safe):

```powershell
$py = ".\.venv\Scripts\python.exe"

& $py examples/run_vector_db_demo.py `
  --in cases/vector_db/inputs/retrieval.jsonl `
  --out out/vector_db_demo `
  --tau-global 0.02 `
  --regime-field namespace

& $py scripts/inspect_huf_artifacts.py --out out/vector_db_demo
```

Expected output shape:

```text
[tail] items_to_cover_90pct=3
Top regimes by rho_global_post:
  1. kb       rho_post=0.619658
  2. tickets  rho_post=0.380342
```

---

## Email (send after PR exists)

Subject: `HUF coherence audit for <Partner> exports — PR open`

Body:

```text
Hi <Name>,

I'm Peter Higgins, author of HUF Core — an artifact-first audit tool for long-tail distributions in retrieval outputs.

I opened a PR that adds a HUF coherence audit example for <Partner> exports: <PR link>.

It runs in two commands and outputs:
- a regime ranking (rho_global_post)
- a concentration number (items_to_cover_90pct)
- an explicit discard ledger (error budget) + trace report

This surfaces silent regime dominance that retrieval metrics can miss.

Docs: <docs link>

Peter Higgins
```

---

## Community post (Slack / Discord / GitHub Discussion)

One-liner:

`Opened a PR adding a HUF coherence audit example for <Partner> exports — dominance + concentration + declared discards. Feedback welcome: <PR link>`
