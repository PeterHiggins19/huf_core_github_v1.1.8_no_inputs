"""Inspect Vector DB demo artifacts (human-readable summary).

This is intentionally dependency-light (stdlib only).

Usage (PowerShell):
  .\\.venv\\Scripts\\python scripts\\inspect_vector_db_artifacts.py --out out\\vector_db_demo
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List


def _read_csv(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(dict(r))
    return rows


def _to_float(x: Any, default: float = 0.0) -> float:
    if x is None:
        return default
    try:
        return float(x)
    except Exception:
        return default


def _fmt(x: float, nd: int = 6) -> str:
    # compact-ish formatting for rho values
    return f"{x:.{nd}g}" if x != 0 else "0"


def main() -> int:
    ap = argparse.ArgumentParser(description="Print a concise summary of vector DB HUF artifacts")
    ap.add_argument("--out", required=True, help="Artifact output folder (e.g., out/vector_db_demo)")
    ap.add_argument("--top", type=int, default=10, help="How many top items to print")
    ap.add_argument("--cover", type=float, default=0.90, help="Coverage threshold for cumulative rho (default 0.90)")
    args = ap.parse_args()

    out_dir = Path(args.out)
    if not out_dir.exists():
        raise FileNotFoundError(out_dir)

    meta_path = out_dir / "meta.json"
    eb_path = out_dir / "artifact_4_error_budget.json"
    coh_path = out_dir / "artifact_1_coherence_map.csv"
    act_path = out_dir / "artifact_2_active_set.csv"

    # ---- meta
    meta = {}
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

    print("\n=== Vector DB artifacts ===")
    if meta:
        print(f"dataset_id: {meta.get('dataset_id', '(none)')}")
        q = meta.get("query") or meta.get("query_label")
        if q:
            print(f"query: {q}")
        if meta.get("regime_field"):
            print(f"regime_field: {meta['regime_field']}")
        if meta.get("tau_global") is not None:
            print(f"tau_global: {_fmt(_to_float(meta.get('tau_global')))}")

    # ---- error budget
    if eb_path.exists():
        eb = json.loads(eb_path.read_text(encoding="utf-8"))
        disc = _to_float(eb.get("rho_discarded_global", 0.0))
        kept = 1.0 - disc
        print(f"kept_global: {_fmt(kept)} | discarded_global: {_fmt(disc)}")

    # ---- coherence map (regimes)
    if coh_path.exists():
        coh = _read_csv(coh_path)
        for r in coh:
            # normalize typical numeric columns
            for k in ("rho_global_post", "rho_discarded_pre", "rho_global_pre", "rho_local_post"):
                if k in r:
                    r[k] = _to_float(r[k])
        coh.sort(key=lambda r: _to_float(r.get("rho_global_post")), reverse=True)

        print("\n-- Top regimes (coherence map) --")
        cols = [
            ("regime_id", "regime"),
            ("rho_global_post", "rho_post"),
            ("rho_discarded_pre", "rho_discarded_pre"),
        ]
        header = " | ".join([c[1] for c in cols])
        print(header)
        print("-" * len(header))
        for r in coh[: max(1, min(len(coh), args.top))]:
            rid = r.get("regime_id")
            rp = _fmt(_to_float(r.get("rho_global_post")))
            rd = _fmt(_to_float(r.get("rho_discarded_pre")))
            print(f"{rid} | {rp} | {rd}")

    # ---- active set (items)
    if act_path.exists():
        act = _read_csv(act_path)
        for r in act:
            for k in ("rank", "value", "rho_global_post", "rho_local_post"):
                if k in r:
                    r[k] = _to_float(r[k])
        act.sort(key=lambda r: _to_float(r.get("rank")))

        # cumulative coverage
        cum = 0.0
        cutoff_rank = None
        for r in act:
            cum += _to_float(r.get("rho_global_post"))
            if cutoff_rank is None and cum >= float(args.cover):
                cutoff_rank = int(_to_float(r.get("rank"), 0.0))
                break

        print("\n-- Top items (active set) --")
        cols = [
            ("rank", "rank"),
            ("regime_id", "regime"),
            ("item_id", "item_id"),
            ("value", "value"),
            ("rho_global_post", "rho_post"),
            ("rho_local_post", "rho_local"),
        ]
        header = " | ".join([c[1] for c in cols])
        print(header)
        print("-" * len(header))
        for r in act[: max(1, min(len(act), args.top))]:
            print(
                f"{int(_to_float(r.get('rank')))} | {r.get('regime_id')} | {r.get('item_id')} | "
                f"{_fmt(_to_float(r.get('value')))} | {_fmt(_to_float(r.get('rho_global_post')))} | {_fmt(_to_float(r.get('rho_local_post')))}"
            )

        if cutoff_rank is not None:
            print(f"\ncoverage: first {cutoff_rank} items reach ≥ {args.cover:.0%} of global rho")

    print("\nTip: open artifact_3_trace_report.jsonl to audit why items were kept/discarded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
