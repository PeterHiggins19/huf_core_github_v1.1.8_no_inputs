#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HUF helper: inspect Markham artifacts (coherence map + active set).

PowerShell-friendly usage (repo root):
  .\.venv\Scripts\python scripts\inspect_markham_artifacts.py --out out\markham2018

It prints a few high-signal summaries to help you read:
- artifact_1_coherence_map.csv
- artifact_2_active_set.csv
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


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect HUF Markham artifacts (console summaries).")
    ap.add_argument("--out", default=r"out\markham2018", help="Output directory from `huf markham`.")
    ap.add_argument("--top", type=int, default=12, help="How many top rows to print.")
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

    pd.set_option("display.width", 140)
    pd.set_option("display.max_columns", 50)

    coh = pd.read_csv(coh_path)
    active = pd.read_csv(act_path)

    # Column discovery (tolerant across versions)
    regime_col = _first_col(coh, ["regime_id", "regime", "fund", "group_id"])
    rho_col = _first_col(coh, ["rho_global_post", "rho_post", "rho_global"])
    disc_col = None
    for cand in ["rho_discarded_pre", "rho_discarded", "discarded_pre", "discarded_frac", "rho_discarded_global_pre"]:
        if cand in coh.columns:
            disc_col = cand
            break

    rank_col = _first_col(active, ["rank", "global_rank"])
    item_col = _first_col(active, ["item_id", "item", "account", "element_id"])
    reg2_col = _first_col(active, ["regime_id", "regime", "fund", "group_id"])
    rho_act = _first_col(active, ["rho_global_post", "rho_post", "rho_global"])
    rho_loc = None
    for cand in ["rho_local_post", "rho_local", "local_share_post"]:
        if cand in active.columns:
            rho_loc = cand
            break
    value_col = None
    for cand in ["value", "value_post", "mass", "count", "retained_value"]:
        if cand in active.columns:
            value_col = cand
            break

    print("\n=== Markham: fund dominance (artifact_1_coherence_map.csv) ===")
    cols = [regime_col, rho_col]
    if disc_col:
        cols.append(disc_col)
    print(coh[cols].sort_values(rho_col, ascending=False).head(args.top).to_string(index=False))

    # Active-set concentration
    active_sorted = active.sort_values(rank_col, ascending=True).reset_index(drop=True)
    active_sorted["cum"] = active_sorted[rho_act].cumsum()

    def _coverage(thresh: float) -> int:
        hit = active_sorted.index[active_sorted["cum"] >= thresh]
        return int(hit[0] + 1) if len(hit) else len(active_sorted)

    print("\n=== Markham: concentration (artifact_2_active_set.csv) ===")
    print(f"Items to reach 90% of retained: {_coverage(0.90)}")
    print(f"Items to reach 97% of retained: {_coverage(0.97)}")

    print("\nTop retained line-items:")
    show_cols = [rank_col, reg2_col, item_col]
    if value_col:
        show_cols.append(value_col)
    show_cols.append(rho_act)
    if rho_loc:
        show_cols.append(rho_loc)
    print(active_sorted[show_cols].head(args.top).to_string(index=False))

    if disc_col:
        print("\nFunds with most discarded share (pre):")
        print(coh[[regime_col, disc_col]].sort_values(disc_col, ascending=False).head(args.top).to_string(index=False))

    print("\nTip: open the CSVs in Excel and filter/sort by the columns printed above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
