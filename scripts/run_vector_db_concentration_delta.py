"""scripts/run_vector_db_concentration_delta.py

Run the Vector DB coherence adapter twice (tau A and tau B) and print a one-line
concentration delta:

  Concentration increased: items_to_cover_90pct X -> Y
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from huf_core.core import HUFCore, HUFConfig
from huf_core.io import write_artifacts
from huf_core.vector_db_adapter import VectorDBAdapterConfig, vector_db_results_to_elements


def _read_csv(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _to_float(x: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if x is None:
            return default
        s = str(x).strip()
        if not s:
            return default
        return float(s)
    except Exception:
        return default


def items_to_cover_90pct(active_set_csv: Path) -> int:
    """How many retained items (sorted by rho_global_post desc) cover 90% mass?"""
    rows = _read_csv(active_set_csv)
    rhos = sorted([_to_float(r.get("rho_global_post"), 0.0) or 0.0 for r in rows], reverse=True)

    total = 0.0
    for i, v in enumerate(rhos, start=1):
        total += float(v)
        if total >= 0.90:
            return i
    return len(rhos)


def run_once(in_path: Path, out_dir: Path, tau_global: float, cfg: VectorDBAdapterConfig, query_label: str) -> None:
    elements, meta = vector_db_results_to_elements(in_path, cfg=cfg, query_label=query_label)

    core = HUFCore(elements, dataset_id=meta["dataset_id"])
    hcfg = HUFConfig(budget_type="mass", exclusion="global", tau=float(tau_global))

    artifacts = core.cycle(hcfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_artifacts(out_dir, artifacts)

    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


def _fmt_tau(t: float) -> str:
    s = f"{t:.6g}"
    return s.replace(".", "p")


def main() -> int:
    ap = argparse.ArgumentParser(description="Run vector-db coherence twice and print concentration delta.")
    ap.add_argument("--in", dest="in_path", required=True, type=Path, help="JSONL/CSV/TSV export (id+score).")
    ap.add_argument("--out", required=True, type=Path, help="Output folder root (will create tau subfolders).")
    ap.add_argument("--tau-a", required=True, type=float, help="Baseline tau (A).")
    ap.add_argument("--tau-b", required=True, type=float, help="Comparison tau (B).")
    ap.add_argument("--regime-field", type=str, default="namespace",
                    help="Grouping field (namespace/collection/tenant/source).")
    ap.add_argument("--query-label", type=str, default="query", help="Recorded in meta/trace.")
    ap.add_argument("--nonneg-mode", type=str, default="clip", choices=["clip", "shift"],
                    help="How to handle negative scores.")
    ap.add_argument("--top-k", type=int, default=200, help="Optional truncate before HUF.")
    args = ap.parse_args()

    cfg = VectorDBAdapterConfig(
        regime_field=args.regime_field,
        nonneg_mode=args.nonneg_mode,
        top_k=args.top_k,
        trace_include_fields=["source", "cluster", "collection", "tenant"],
    )

    out_a = args.out / f"tau_{_fmt_tau(args.tau_a)}"
    out_b = args.out / f"tau_{_fmt_tau(args.tau_b)}"

    run_once(args.in_path, out_a, args.tau_a, cfg=cfg, query_label=args.query_label)
    run_once(args.in_path, out_b, args.tau_b, cfg=cfg, query_label=args.query_label)

    k_a = items_to_cover_90pct(out_a / "artifact_2_active_set.csv")
    k_b = items_to_cover_90pct(out_b / "artifact_2_active_set.csv")

    if k_b < k_a:
        msg = "Concentration increased"
    elif k_b > k_a:
        msg = "Concentration decreased"
    else:
        msg = "Concentration unchanged"

    print(f"[out] {args.out.resolve()}")
    print(f"{msg}: items_to_cover_90pct {k_a} -> {k_b}")
    print(f"  tau_a={args.tau_a}  tau_b={args.tau_b}  regime_field={args.regime_field}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
