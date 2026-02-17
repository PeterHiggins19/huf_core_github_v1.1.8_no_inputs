"""Run the Markham 2018 demo using the built-in CLI.

Defaults expect the real input workbook at the default path (not bundled; see DATA_SOURCES.md).

Usage:
  python examples/run_markham.py --out out/markham2018
  python examples/run_markham.py --xlsx <path> --out <folder> --tau-global 0.005 --tau-local 0.02
"""

import argparse
from pathlib import Path
from huf_core.cli import main as huf_main

DEFAULT_XLSX = Path("cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    ap.add_argument("--out", type=Path, default=Path("out/markham2018"))
    ap.add_argument("--tau-global", type=float, default=0.005)
    ap.add_argument("--tau-local", type=float, default=0.02)
    args = ap.parse_args()

    argv = [
        "markham",
        "--xlsx", str(args.xlsx),
        "--out", str(args.out),
        "--tau-global", str(args.tau_global),
        "--tau-local", str(args.tau_local),
    ]
    raise SystemExit(huf_main(argv))

if __name__ == "__main__":
    main()
