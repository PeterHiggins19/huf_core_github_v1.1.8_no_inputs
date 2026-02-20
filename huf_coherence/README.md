\
    # HUF coherence audit for Weaviate retrieval exports

    This example turns a **saved Weaviate retrieval result** (or any vector DB export) into a **HUF audit**:

    - **Dominance:** which namespace / collection / tenant dominates (`artifact_1_coherence_map.csv`)
    - **Concentration:** one “proof line” (`items_to_cover_90pct`)
    - **Declared discards:** how much mass fell below threshold (`artifact_4_error_budget.json`)
    - **Trace:** why items are retained (`artifact_3_trace_report.jsonl`)

    > No live DB connection required — you run it on a JSONL/CSV/TSV dump.

    ## Quickstart (Windows PowerShell)

    From this folder:

    ```powershell
    .\scripts\run_huf_coherence.ps1
    ```

    Expected output (see `expected/console_output.txt`):

    ```text
    [tail] items_to_cover_90pct=3
    Top regimes by rho_global_post:
      1. kb  rho_post=0.619658
      2. tickets  rho_post=0.380342
    ```

    ## Quickstart (macOS/Linux)

    ```bash
    bash scripts/run_huf_coherence.sh
    ```

    ## Run it on your own Weaviate results

    ### Option A — You already have a JSONL/CSV/TSV dump

    Your file must contain at least:

    - `id` (string)
    - `score` (number; **higher is better**)

    Optional fields you can audit “by” (regimes):

    - `namespace`
    - `collection`
    - `tenant`
    - `source`

    Run:

    ```powershell
    .\.venv\Scripts\python scripts/run_huf_coherence.py --in <your_dump.jsonl> --out out/my_run --tau-global 0.02 --regime-field namespace
    .\.venv\Scripts\python scripts/inspect_huf_run.py --out out/my_run
    ```

    ### Option B — You saved a Weaviate JSON response

    Convert it to JSONL:

    ```powershell
    .\.venv\Scripts\python scripts/export_weaviate_results_to_jsonl.py --in saved_weaviate_response.json --out data/weaviate_export.jsonl --regime-field collection
    ```

    Then run:

    ```powershell
    .\.venv\Scripts\python scripts/run_huf_coherence.py --in data/weaviate_export.jsonl --out out/weaviate_run --tau-global 0.02 --regime-field collection
    .\.venv\Scripts\python scripts/inspect_huf_run.py --out out/weaviate_run
    ```

    ## How to read the artifacts (30 seconds)

    - **`artifact_1_coherence_map.csv`** (regime ranking)  
      Sort by `rho_global_post` → “which regime dominates the kept set?”

    - **`artifact_2_active_set.csv`** (review list)  
      Sort by `rho_global_post` → “which items matter most overall?”

    - **Proof line: `items_to_cover_90pct`**  
      “How many retained items explain **90%** of mass?”  
      Low number ⇒ high concentration (a few chunks dominate retrieval).

    - **`artifact_4_error_budget.json`**  
      Look for `discarded_budget_global` → “how much did we discard?”

    - **`artifact_3_trace_report.jsonl`**  
      Use when someone asks: “Why is this item here?”

    ## Why this matters (one sentence)

    If `items_to_cover_90pct` is very small, **your retrieval quality is dominated by a tiny set of chunks** — so staleness or mis-indexing in those chunks can compromise most results.

    ## HUF reference

    - HUF docs site: https://peterhiggins19.github.io/huf_core_github_v1.1.8_no_inputs/
    - HUF source repo: https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs
