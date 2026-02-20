\
    from __future__ import annotations

    import argparse
    import json
    from pathlib import Path

    from huf_core.core import HUFCore, HUFConfig
    from huf_core.io import write_artifacts
    from huf_core.vector_db_adapter import VectorDBAdapterConfig, vector_db_results_to_elements


    def main() -> int:
        ap = argparse.ArgumentParser(description="Run HUF coherence audit over exported retrieval results.")
        ap.add_argument("--in", dest="in_path", required=True, type=Path, help="JSONL/CSV/TSV retrieval dump (id+score).")
        ap.add_argument("--out", required=True, type=Path, help="Output folder for HUF artifacts.")
        ap.add_argument("--tau-global", type=float, default=0.02, help="Global exclusion threshold (mass frame).")
        ap.add_argument("--query-label", type=str, default="query", help="Label recorded in trace/meta.")
        ap.add_argument("--regime-field", type=str, default="namespace", help="Column used to define regimes.")
        ap.add_argument(
            "--nonneg-mode",
            type=str,
            default="clip",
            choices=["clip", "shift"],
            help="How to handle negative scores (HUF requires nonnegative values).",
        )
        ap.add_argument("--top-k", type=int, default=200, help="Optional truncate of retrieval list before HUF.")
        args = ap.parse_args()

        cfg = VectorDBAdapterConfig(
            regime_field=args.regime_field,
            nonneg_mode=args.nonneg_mode,
            top_k=args.top_k,
            trace_include_fields=["source", "cluster", "collection", "tenant"],
        )

        elements, meta = vector_db_results_to_elements(args.in_path, cfg=cfg, query_label=args.query_label)

        core = HUFCore(elements, dataset_id=meta["dataset_id"])
        hcfg = HUFConfig(budget_type="mass", exclusion="global", tau=float(args.tau_global))

        artifacts = core.cycle(hcfg)
        write_artifacts(args.out, artifacts)

        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] Wrote artifacts to: {args.out}")
        return 0


    if __name__ == "__main__":
        raise SystemExit(main())
