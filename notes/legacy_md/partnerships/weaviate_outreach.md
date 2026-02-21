# Weaviate outreach package

This page packages two “ready-to-send” assets:

1) **GitHub PR text** (for Weaviate’s `partner-integration-examples` repo)  
2) **A short email** to the partner manager — sent **after** the PR exists, so the email includes proof (a link)

Why this exists: integrations land faster when there is something reviewable (a PR) before anyone has to take a meeting.

!!! note "Time sensitivity"
    Partner roles and names can change. Verify the current partner contact first.
    Keep the message the same; just address the right person.

---

## Use this if you want to do outreach

### Step 1 — Open the PR first

The PR is the “proof artifact”. It makes the follow‑up email feel like:  
“Here is something real you can review” instead of “Here is an idea”.

### Step 2 — Send the email after the PR link exists

Put the PR link in the first paragraph.

---

## Plain-text fallback (copy/paste)

### PR title

`feat: HUF coherence adapter — retrieval audit for Weaviate exports (namespace dominance + long-tail concentration)`

### PR description (short)

- Adds a minimal example showing how to run a **HUF coherence audit** on retrieval exports  
- Answers: *dominant namespaces/collections*, *concentration (items_to_cover_90pct)*, and *declared discards (error budget)*  
- No live Weaviate connection required — JSONL in, HUF artifacts out  

### Two-command demo (Windows-safe)

```powershell
$py = ".\.venv\Scripts\python.exe"

& $py examples/run_vector_db_demo.py `
  --in cases/vector_db/inputs/retrieval.jsonl `
  --out out/vector_db_demo `
  --tau-global 0.02 `
  --regime-field namespace

& $py scripts/inspect_huf_artifacts.py --out out/vector_db_demo
```

Expected shape:

```text
[tail] items_to_cover_90pct=3

Top regimes by rho_global_post:
  1. kb       rho_post=0.619658
  2. tickets  rho_post=0.380342
```

### Email (template)

Subject: `HUF coherence adapter for Weaviate exports — retrieval audit integration (PR open)`

Body:

```text
Hi <Name>,

I'm Peter Higgins, the author of HUF Core (Higgins Unity Framework) — an artifact-first audit tool for long-tail distributions in retrieval outputs.

I opened a PR to weaviate/partner-integration-examples that adds a HUF coherence adapter for Weaviate retrieval exports: <link to PR>.

It runs in two commands and outputs:
- a regime ranking by collection/namespace (rho_global_post)
- a concentration score (items_to_cover_90pct)
- an explicit discard ledger (error budget)

This surfaces something retrieval metrics miss: silent namespace dominance in multi-collection deployments.

Happy to do a quick walkthrough, contribute a short co-authored blog draft, or just let the PR speak for itself.

Docs: https://peterhiggins19.github.io/huf_core_github_v1.1.8_no_inputs/vector_db_coherence_one_pager/

Peter Higgins
https://github.com/PeterHiggins19/huf_core_github_v1.1.8_no_inputs
```
