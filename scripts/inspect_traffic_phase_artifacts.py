#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HUF helper: inspect Traffic Phase artifacts (Toronto signals).

PowerShell-friendly usage (repo root):
  .\.venv\Scripts\python scripts\inspect_traffic_phase_artifacts.py --out out\traffic_phase --csv cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv

It prints:
- global band totals (MajorEven / MinorOdd / Other) from the input CSV
- top intersections by global share from artifact_1_coherence_map.csv
- most MinorOdd-heavy + Other-heavy intersections from artifact_2_active_set.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _need_pandas() -> "None":
    print("ERROR: pandas is required for this helper.")
    print("Install into the repo venv:")
    print(r"  .\.venv\Scripts\python -m pip install pandas")
    raise SystemExit(2)


def _first_col(df, names: list[str]) -> str:
    cols = set(df.columns)
    for n in names:
        if n in cols:
            return n
    raise KeyError(f"None of these columns found: {names}. Columns={list(df.columns)}")


def _phase_band(phase: int) -> str:
    if phase in (2, 4, 6, 8):
        return "MajorEven(2,4,6,8)"
    if phase in (1, 3, 5, 7):
        return "MinorOdd(1,3,5,7)"
    if 9 <= phase <= 12:
        return "Other(9-12)"
    return "Other(9-12)"


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect HUF Traffic Phase artifacts (console summaries).")
    ap.add_argument("--out", default=r"out\traffic_phase", help="Output directory from `huf traffic`.")
    ap.add_argument("--csv", default=r"cases\traffic_phase\inputs\toronto_traffic_signals_phase_status.csv",
                    help="Input CSV used for the run (for global band totals).")
    ap.add_argument("--top", type=int, default=10, help="How many top rows to print.")
    args = ap.parse_args()

    out_dir = Path(args.out)
    coh_path = out_dir / "artifact_1_coherence_map.csv"
    act_path = out_dir / "artifact_2_active_set.csv"

    if not coh_path.exists():
        print(f"Missing: {coh_path}")
        return 2
    if not act_path.exists():
        print(f"Missing: {act_path}")
        return 2

    try:
        import pandas as pd  # type: ignore
    except Exception:
        _need_pandas()

    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", 80)

    # 1) Global band totals (from the raw input)
    csv_path = Path(args.csv)
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        if "PHASE" in df.columns:
            # PHASE can be string; coerce carefully
            phase = pd.to_numeric(df["PHASE"], errors="coerce").fillna(-1).astype(int)
            band = phase.map(lambda p: _phase_band(int(p)) if p >= 0 else "Other(9-12)")
            totals = band.value_counts().rename_axis("band").reset_index(name="rows")
            totals["share"] = totals["rows"] / float(totals["rows"].sum())
            print("\n=== Traffic Phase: global band totals (from input CSV) ===")
            print(totals.sort_values("share", ascending=False).to_string(index=False))
        else:
            print("\nNOTE: input CSV missing PHASE column; skipping global band totals.")
    else:
        print(f"\nNOTE: input CSV not found: {csv_path} (skipping global band totals)")

    # 2) Top intersections (coherence map)
    coh = pd.read_csv(coh_path)
    regime_col = _first_col(coh, ["regime_id", "regime", "tcs", "group_id"])
    rho_col = _first_col(coh, ["rho_global_post", "rho_post", "rho_global"])
    top = coh[[regime_col, rho_col]].sort_values(rho_col, ascending=False).head(args.top)

    print("\n=== Traffic Phase: top intersections by global share (artifact_1_coherence_map.csv) ===")
    print(top.to_string(index=False))

    # 3) Outliers (active set)
    active = pd.read_csv(act_path)
    reg_col = _first_col(active, ["regime_id", "regime", "tcs", "group_id"])
    item_col = _first_col(active, ["item_id", "item", "element_id"])
    rho_loc_col = None
    for cand in ["rho_local_post", "rho_local", "local_share_post"]:
        if cand in active.columns:
            rho_loc_col = cand
            break
    value_col = None
    for cand in ["value", "count", "mass", "value_post", "retained_value"]:
        if cand in active.columns:
            value_col = cand
            break

    if rho_loc_col is None:
        print("\nNOTE: active set missing local share column; cannot build outlier lists.")
        return 0

    # Pivot local shares into columns by band label extracted from item_id
    # Expect item_id like "...MinorOdd..." etc. Fall back to value counts if share missing.
    def _band_from_item(s: str) -> str:
        if "MajorEven" in s:
            return "MajorEven"
        if "MinorOdd" in s:
            return "MinorOdd"
        if "Other" in s:
            return "Other"
        return "Other"

    active["band"] = active[item_col].astype(str).map(_band_from_item)
    # Total per regime (rows) from value counts if available; else approximate from shares
    if value_col:
        totals = active.groupby(reg_col)[value_col].sum().rename("total_rows")
    else:
        # if no counts, use 1.0 so sorting still works
        totals = active.groupby(reg_col)[rho_loc_col].sum().rename("total_rows")

    shares = active.pivot_table(index=reg_col, columns="band", values=rho_loc_col, aggfunc="sum").fillna(0.0)
    out = shares.join(totals, how="left").reset_index().rename(columns={reg_col: "regime"})

    # MinorOdd-heavy
    if "MinorOdd" in out.columns:
        minor = out.sort_values("MinorOdd", ascending=False).head(args.top)
        cols = ["regime", "total_rows", "MajorEven", "MinorOdd", "Other"]
        cols = [c for c in cols if c in minor.columns]
        print("\n=== Traffic Phase: most MinorOdd-heavy intersections (local share) ===")
        print(minor[cols].to_string(index=False))

    # Other-heavy
    if "Other" in out.columns:
        oth = out.sort_values("Other", ascending=False).head(args.top)
        cols = ["regime", "total_rows", "MajorEven", "MinorOdd", "Other"]
        cols = [c for c in cols if c in oth.columns]
        print("\n=== Traffic Phase: most Other-heavy intersections (local share) ===")
        print(oth[cols].to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
