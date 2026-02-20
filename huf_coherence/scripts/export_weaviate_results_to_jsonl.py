\
    from __future__ import annotations

    import argparse
    import json
    from pathlib import Path
    from typing import Any, Dict, List, Optional


    def _iter_dicts(obj: Any) -> List[Dict[str, Any]]:
        # Walk a JSON object and return all dict nodes.
        out: List[Dict[str, Any]] = []

        def walk(x: Any) -> None:
            if isinstance(x, dict):
                out.append(x)
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)

        walk(obj)
        return out


    def _to_float(v: Any) -> Optional[float]:
        try:
            if v is None:
                return None
            return float(v)
        except Exception:
            return None


    def _pick_score(rec: Dict[str, Any], prefer: str = "score", distance_to_score: str = "inv1p") -> Optional[float]:
        # Choose a numeric score from a record.
        # Priority:
        #   1) rec[prefer]
        #   2) rec["_additional"][prefer]
        #   3) rec["_additional"]["certainty"]
        #   4) rec["_additional"]["distance"] -> converted to score
        #
        # distance_to_score:
        #   - inv1p: 1/(1+distance)
        #   - neg:  -distance

        if prefer in rec:
            v = _to_float(rec.get(prefer))
            if v is not None:
                return v

        add = rec.get("_additional")
        if isinstance(add, dict):
            if prefer in add:
                v = _to_float(add.get(prefer))
                if v is not None:
                    return v
            v = _to_float(add.get("certainty"))
            if v is not None:
                return v
            d = _to_float(add.get("distance"))
            if d is not None:
                return (-d) if distance_to_score == "neg" else (1.0 / (1.0 + d))

        d = _to_float(rec.get("distance"))
        if d is not None:
            return (-d) if distance_to_score == "neg" else (1.0 / (1.0 + d))

        return None


    def main() -> int:
        ap = argparse.ArgumentParser(description="Convert saved Weaviate JSON -> JSONL (id, score, regime field).")
        ap.add_argument("--in", dest="in_path", required=True, type=Path, help="Saved Weaviate JSON response file.")
        ap.add_argument("--out", dest="out_path", required=True, type=Path, help="Output .jsonl path.")
        ap.add_argument("--prefer-score-field", type=str, default="score",
                        help="Prefer this numeric key if present (score/certainty/etc).")
        ap.add_argument("--distance-to-score", choices=["inv1p", "neg"], default="inv1p",
                        help="If only distance is available: inv1p => 1/(1+distance); neg => -distance.")
        ap.add_argument("--regime-field", type=str, default="collection",
                        help="If present, copied as this field (used later as --regime-field).")
        ap.add_argument("--regime-default", type=str, default="Global", help="Fallback regime value.")
        args = ap.parse_args()

        obj = json.loads(args.in_path.read_text(encoding="utf-8"))
        nodes = _iter_dicts(obj)

        rows: List[Dict[str, Any]] = []
        for rec in nodes:
            add = rec.get("_additional") if isinstance(rec.get("_additional"), dict) else {}
            rid = rec.get("id") or add.get("id")
            if rid is None:
                continue

            score = _pick_score(rec, prefer=args.prefer_score_field, distance_to_score=args.distance_to_score)
            if score is None:
                continue

            regime_val = rec.get(args.regime_field)
            if regime_val is None and isinstance(rec.get("properties"), dict):
                regime_val = rec["properties"].get(args.regime_field)
            if regime_val is None:
                regime_val = args.regime_default

            rows.append({"id": str(rid), "score": float(score), args.regime_field: str(regime_val)})

        args.out_path.parent.mkdir(parents=True, exist_ok=True)
        with args.out_path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        print(f"[OK] wrote {len(rows)} lines -> {args.out_path}")
        return 0


    if __name__ == "__main__":
        raise SystemExit(main())
