\
    # HUF coherence audit for Weaviate retrieval exports

    This example turns a **saved retrieval export** (Weaviate or any vector DB) into a **HUF audit**:

    - **Dominance:** which namespace / collection / tenant dominates (`artifact_1_coherence_map.csv`)
    - **Concentration:** one “proof line” (`items_to_cover_90pct`)
    - **Declared discards:** how much mass fell below threshold (`artifact_4_error_budget.json`)
    - **Trace:** why items are retained (`artifact_3_trace_report.jsonl`)

    > No live DB connection required — you run it on a JSONL/CSV/TSV dump.

    ## Quickstart (Windows PowerShell)

    ```powershell
    .\scripts\run_huf_coherence.ps1
    ```

    ## Quickstart (macOS/Linux)

    ```bash
    bash scripts/run_huf_coherence.sh
    ```

    ## Canonical HUF repo used by this example

    - https://github.com/PeterHiggins19/huf_core_github_v1.1.8_no_inputs
