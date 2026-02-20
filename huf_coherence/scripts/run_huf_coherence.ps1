\
    # HUF coherence demo (Windows PowerShell)
    # - script-first, no notebook required
    # - creates a local venv and runs the audit on the sample JSONL

    $ErrorActionPreference = "Stop"

    $py = ".\.venv\Scripts\python.exe"
    if (-not (Test-Path $py)) {
      python -m venv .venv
    }

    & $py -m pip install --upgrade pip
    & $py -m pip install -r requirements.txt

    # Install HUF Core directly from GitHub (public repo).
    # NOTE: owner string includes a capital 'I' after the H: PeterHIggins19
    & $py -m pip install "git+https://github.com/PeterHIggins19/huf_core_github_v1.1.8_no_inputs.git"

    $out = "out\demo"
    New-Item -ItemType Directory -Force $out | Out-Null

    & $py scripts/run_huf_coherence.py --in data/retrieval.jsonl --out $out --tau-global 0.02 --regime-field namespace
    & $py scripts/inspect_huf_run.py --out $out
