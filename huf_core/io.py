from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json
import pandas as pd

def write_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def write_artifacts(out_dir: Path, artifacts: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Coherence map
    cm = artifacts["coherence_map"]
    if isinstance(cm, pd.DataFrame):
        cm.to_csv(out_dir / "artifact_1_coherence_map.csv", index=False)
    else:
        pd.DataFrame(cm).to_csv(out_dir / "artifact_1_coherence_map.csv", index=False)

    # Active set
    pd.DataFrame(artifacts["active_set"]).to_csv(out_dir / "artifact_2_active_set.csv", index=False)

    # Trace report
    write_jsonl(out_dir / "artifact_3_trace_report.jsonl", artifacts["trace_report"])

    # Error/budget
    (out_dir / "artifact_4_error_budget.json").write_text(
        json.dumps(artifacts["error_budget"], indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Run stamp
    (out_dir / "run_stamp.json").write_text(
        json.dumps(artifacts["run_stamp"], indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def validate_trace_line_min(obj: dict) -> None:
    """Minimal runtime validation for required trace fields.

    Accepts both legacy keys (rho_global, discarded_budget) and the current HUF schema
    (rho_global_post, discarded_budget_global).
    """
    required = ["item_id", "regime_path", "inputs_ref", "method_ref"]
    missing = [k for k in required if k not in obj]
    if missing:
        raise ValueError(f"Trace line missing required fields: {missing}")

    if ("rho_global" not in obj) and ("rho_global_post" not in obj):
        raise ValueError("Trace line missing required field: rho_global_post (or legacy rho_global)")

    if ("discarded_budget" not in obj) and ("discarded_budget_global" not in obj):
        raise ValueError("Trace line missing required field: discarded_budget_global (or legacy discarded_budget)")
