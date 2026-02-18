"""Run Toronto traffic demos (phase-band + anomaly) on the real CSV (not bundled; download separately; see DATA_SOURCES.md).

Usage:
  python examples/run_traffic.py --out out/traffic
  python examples/run_traffic.py --csv <path> --out <folder> --tau-local 0.05 --anomaly-tau-global 0.0005
"""

import argparse
from pathlib import Path
from huf_core.cli import main as huf_main

DEFAULT_CSV = Path("cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--out", type=Path, default=Path("out/traffic_phase"))
    ap.add_argument("--tau-local", type=float, default=0.05)
    ap.add_argument("--anomaly-out", type=Path, default=Path("out/traffic_anomaly"))
    ap.add_argument("--anomaly-tau-global", type=float, default=0.0005, help="Global tau for traffic-anomaly. 0.005 can exclude all elements on the bundled CSV.")
    ap.add_argument("--status", action="append", default=["Green Termination"], help="PHASE_STATUS_TEXT to include (repeatable).")
    args = ap.parse_args()

    # phase-band compression
    argv1 = ["traffic", "--csv", str(args.csv), "--out", str(args.out), "--tau-local", str(args.tau_local)]
    huf_main(argv1)

    # anomaly diagnostic
    argv2 = ["traffic-anomaly", "--csv", str(args.csv), "--out", str(args.anomaly_out), "--tau-global", str(args.anomaly_tau_global)]
    for s in args.status:
        argv2.extend(["--status", s])
    huf_main(argv2)

if __name__ == "__main__":
    main()
