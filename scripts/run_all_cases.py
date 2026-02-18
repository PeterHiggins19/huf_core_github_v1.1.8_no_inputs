#!/usr/bin/env python3
"""Run all HUF demo cases end-to-end + basic output checks.

Runs:
- pytest (optional)
- Markham
- Traffic Phase
- Traffic Anomaly
- Planck (optional; pass --planck-fits)

Usage (Windows PowerShell):
  .\.venv\Scripts\python scripts\run_all_cases.py
  .\.venv\Scripts\python scripts\run_all_cases.py --skip-tests
  .\.venv\Scripts\python scripts\run_all_cases.py --planck-fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits

Usage (macOS/Linux):
  ./.venv/bin/python scripts/run_all_cases.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path
from typing import List, Optional

ARTIFACT_FILES = (
    "artifact_1_coherence_map.csv",
    "artifact_2_active_set.csv",
    "artifact_3_trace_report.jsonl",
    "artifact_4_error_budget.json",
    "run_stamp.json",
    "meta.json",
    "stability_packet.csv",
)

DEFAULT_MARKHAM_XLSX = Path("cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx")
DEFAULT_TORONTO_CSV_PHASE = Path("cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv")
DEFAULT_TORONTO_CSV_ANOM = Path("cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _check_outputs(case_out: Path) -> None:
    missing = [f for f in ARTIFACT_FILES if not (case_out / f).exists()]
    if missing:
        raise SystemExit(f"[FAIL] Missing outputs in {case_out}:\n  - " + "\n  - ".join(missing))
    print(f"[OK] Outputs present: {case_out}")


def _maybe_fetch_inputs(no_fetch: bool) -> None:
    """Fetch external inputs *only if* missing."""
    if no_fetch:
        return

    repo = _repo_root()
    need_markham = not (repo / DEFAULT_MARKHAM_XLSX).exists()
    need_toronto = not (repo / DEFAULT_TORONTO_CSV_PHASE).exists()

    if not (need_markham or need_toronto):
        return

    print("[INFO] Some inputs are missing; attempting fetch (Markham + Toronto).")
    sys.path.insert(0, str(repo))
    from scripts.fetch_data import main as fetch_main  # type: ignore

    rc = fetch_main(["--markham", "--toronto", "--yes"])
    if rc != 0:
        raise SystemExit(rc)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", default="out/smoke", help="Root output folder (relative to repo root).")
    ap.add_argument("--skip-tests", action="store_true", help="Skip pytest.")
    ap.add_argument("--no-fetch", action="store_true", help="Do not attempt to fetch missing inputs.")
    ap.add_argument("--anomaly-tau-global", type=float, default=0.0005,
                    help="tau for traffic-anomaly (0.005 can exclude all elements on the bundled CSV).")
    ap.add_argument("--status", action="append", default=["Green Termination"],
                    help="Repeatable PHASE_STATUS_TEXT filter for anomaly.")
    ap.add_argument("--planck-fits", type=str, default="", help="Optional path to Planck LFI 70 FITS.")
    args = ap.parse_args(argv)

    repo = _repo_root()
    os.chdir(repo)
    sys.path.insert(0, str(repo))

    if not args.skip_tests:
        import pytest
        print("== pytest ==")
        rc = pytest.main(["-q"])
        if rc != 0:
            return int(rc)

    _maybe_fetch_inputs(no_fetch=args.no_fetch)

    from huf_core.cli import main as huf_main

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = (repo / args.out_root / stamp).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    print(f"\nOutputs will be written under:\n  {out_root}\n")

    # Markham
    print("== markham2018 ==")
    xlsx = (repo / DEFAULT_MARKHAM_XLSX).resolve()
    rc = huf_main(["markham", "--xlsx", str(xlsx), "--out", str(out_root / "markham2018")])
    if rc != 0:
        return rc
    _check_outputs(out_root / "markham2018")

    # Traffic phase
    print("== traffic_phase ==")
    csv_phase = (repo / DEFAULT_TORONTO_CSV_PHASE).resolve()
    rc = huf_main(["traffic", "--csv", str(csv_phase), "--out", str(out_root / "traffic_phase")])
    if rc != 0:
        return rc
    _check_outputs(out_root / "traffic_phase")

    # Traffic anomaly
    print("== traffic_anomaly ==")
    csv_anom = (repo / DEFAULT_TORONTO_CSV_ANOM).resolve()
    argv2 = [
        "traffic-anomaly",
        "--csv", str(csv_anom),
        "--out", str(out_root / "traffic_anomaly"),
        "--tau-global", str(args.anomaly_tau_global),
    ]
    for s in args.status:
        argv2 += ["--status", s]
    rc = huf_main(argv2)
    if rc != 0:
        return rc
    _check_outputs(out_root / "traffic_anomaly")

    # Optional: Planck
    if args.planck_fits.strip():
        print("== planck70 ==")
        fits = Path(args.planck_fits).expanduser().resolve()
        rc = huf_main(["planck", "--fits", str(fits), "--out", str(out_root / "planck70")])
        if rc != 0:
            return rc
        _check_outputs(out_root / "planck70")
    else:
        print("[SKIP] planck70 (no --planck-fits provided)")

    print("\n[DONE] All selected cases ran successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
