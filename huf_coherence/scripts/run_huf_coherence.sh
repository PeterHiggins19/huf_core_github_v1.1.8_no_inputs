\
    #!/usr/bin/env bash
    set -euo pipefail

    python3 -m venv .venv
    PY="./.venv/bin/python"
    "$PY" -m pip install --upgrade pip
    "$PY" -m pip install -r requirements.txt

    "$PY" -m pip install "git+https://github.com/PeterHiggins19/huf_core_github_v1.1.8_no_inputs.git"

    OUT="out/demo"
    mkdir -p "$OUT"

    "$PY" scripts/run_huf_coherence.py --in data/retrieval.jsonl --out "$OUT" --tau-global 0.02 --regime-field namespace
    "$PY" scripts/inspect_huf_run.py --out "$OUT"
