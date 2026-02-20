\
    from __future__ import annotations

    import argparse
    import csv
    import json
    from pathlib import Path
    from typing import List, Dict, Any, Optional


    def _read_csv(path: Path) -> List[Dict[str, Any]]:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rdr = csv.DictReader(f)
            return list(rdr)


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


    def items_to_cover(rhos: List[float], target: float = 0.90) -> int:
        if not rhos:
            return 0
        total = 0.0
        for i, v in enumerate(rhos, start=1):
            total += float(v)
            if total >= target:
                return i
        return len(rhos)


    def main() -> int:
        ap = argparse.ArgumentParser(description="Inspect HUF artifacts (prints proof line + top regimes).")
        ap.add_argument("--out", required=True, type=Path, help="Run output folder containing artifact_*.{csv,json}.")
        ap.add_argument("--top-regimes", type=int, default=10, help="How many regimes to print.")
        args = ap.parse_args()

        out = args.out
        cm_path = out / "artifact_1_coherence_map.csv"
        as_path = out / "artifact_2_active_set.csv"
        eb_path = out / "artifact_4_error_budget.json"

        if not cm_path.exists():
            raise FileNotFoundError(cm_path)
        if not as_path.exists():
            raise FileNotFoundError(as_path)

        cm = _read_csv(cm_path)
        active = _read_csv(as_path)

        rhos = sorted(
            [_to_float(r.get("rho_global_post"), 0.0) or 0.0 for r in active],
            reverse=True,
        )
        k90 = items_to_cover(rhos, 0.90)

        print(f"[out] {out.resolve()}")
        print(f"[tail] items_to_cover_90pct={k90}")

        def _cm_key(r: Dict[str, Any]) -> float:
            v = _to_float(r.get("rho_global_post"), None)
            if v is None:
                v = _to_float(r.get("rho_global_pre"), 0.0)
            return float(v or 0.0)

        cm_sorted = sorted(cm, key=_cm_key, reverse=True)

        print("\nTop regimes by rho_global_post:")
        for i, r in enumerate(cm_sorted[: int(args.top_regimes)], start=1):
            rid = str(r.get("regime_id", ""))
            rho = _to_float(r.get("rho_global_post"), None)
            if rho is None:
                rho = _to_float(r.get("rho_global_pre"), 0.0)
            print(f"  {i}. {rid}  rho_post={float(rho or 0.0):.6f}")

        if eb_path.exists():
            try:
                eb = json.loads(eb_path.read_text(encoding="utf-8"))
                disc = eb.get("discarded_budget_global", eb.get("discarded_budget"))
                if disc is not None:
                    print(f"\n[budget] discarded_budget_global={float(disc):.6g}")
            except Exception:
                pass

        return 0


    if __name__ == "__main__":
        raise SystemExit(main())
