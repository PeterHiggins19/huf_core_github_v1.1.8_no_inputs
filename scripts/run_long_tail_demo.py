\
#!/usr/bin/env python3
"""Run Traffic Phase + Traffic Anomaly and print a long-tail comparison."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# ✅ Make `import scripts.*` work when running: python scripts/run_long_tail_demo.py
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.inspect_huf_artifacts import summarize, print_dashboard  # noqa: E402


def _find_huf_argv() -> List[str]:
    scripts_dir = Path(sys.executable).resolve().parent
    for name in ["huf.exe", "huf", "huf.cmd", "huf-script.py"]:
        p = scripts_dir / name
        if p.exists():
            if p.suffix == ".py":
                return [sys.executable, str(p)]
            return [str(p)]
    return [sys.executable, "-m", "huf_core"]


def _run(cmd: List[str]) -> None:
    print(f"[run] {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def _compare_top_regimes(a: List[Tuple[str, float]], b: List[Tuple[str, float]]) -> Tuple[List[str], List[str], List[str]]:
    a_ids = [x[0] for x in a]
    b_ids = [x[0] for x in b]
    entered = [rid for rid in b_ids if rid not in a_ids]
    exited = [rid for rid in a_ids if rid not in b_ids]
    stayed = [rid for rid in b_ids if rid in a_ids]
    return entered, exited, stayed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="Green Termination")
    ap.add_argument("--phase-csv", default="cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv")
    ap.add_argument("--anomaly-csv", default="cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv")
    ap.add_argument("--out-phase", default="out/traffic_phase_demo")
    ap.add_argument("--out-anomaly", default="out/traffic_anomaly_demo")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    phase_csv = Path(args.phase_csv)
    anomaly_csv = Path(args.anomaly_csv)

    if not phase_csv.exists() or not anomaly_csv.exists():
        print("[error] Toronto CSV inputs not found.")
        print("Fetch them with:")
        print(r"  .\.venv\Scripts\python scripts/fetch_data.py --toronto --yes")
        return 2

    out_phase = Path(args.out_phase)
    out_anom = Path(args.out_anomaly)
    out_phase.mkdir(parents=True, exist_ok=True)
    out_anom.mkdir(parents=True, exist_ok=True)

    huf = _find_huf_argv()

    _run(huf + ["traffic", "--csv", str(phase_csv), "--out", str(out_phase)])
    _run(huf + ["traffic-anomaly", "--csv", str(anomaly_csv), "--out", str(out_anom), "--status", args.status])

    s_base = summarize(out_phase, top_regimes=args.top)
    s_anom = summarize(out_anom, top_regimes=args.top)

    print()
    print("=== BASELINE: Traffic Phase ===")
    print_dashboard(s_base)

    print()
    print("=== EXCEPTION: Traffic Anomaly ===")
    print_dashboard(s_anom)

    base_top = s_base.get("top_regimes", [])
    anom_top = s_anom.get("top_regimes", [])
    entered, exited, stayed = _compare_top_regimes(base_top, anom_top)

    base_items90 = s_base.get("items_to_cover_90pct", None)
    anom_items90 = s_anom.get("items_to_cover_90pct", None)

    print()
    print("=== LONG-TAIL HEADLINE ===")
    print(f"Top-{args.top} regimes changed: entered={len(entered)} exited={len(exited)} stayed={len(stayed)}")

    if base_items90 is not None and anom_items90 is not None:
        print(f"PROOF: items_to_cover_90pct {base_items90} -> {anom_items90}")
        if anom_items90 < base_items90:
            print(f"Concentration increased: items_to_cover_90pct {base_items90} -> {anom_items90}")
        elif anom_items90 > base_items90:
            print(f"Concentration decreased: items_to_cover_90pct {base_items90} -> {anom_items90}")
        else:
            print(f"Concentration unchanged: items_to_cover_90pct {base_items90} -> {anom_items90}")
    else:
        print("PROOF: items_to_cover_90pct (could not compute for one or both runs)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
