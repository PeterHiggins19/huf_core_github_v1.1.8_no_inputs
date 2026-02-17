"""Run the Planck LFI 70 GHz demo (real FITS input included in this system package).

Usage:
  python examples/run_planck.py --fits cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits --out out/planck70
"""

import argparse
from pathlib import Path
from huf_core.cli import main as huf_main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fits", type=Path, default=Path("cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits"))
    ap.add_argument("--out", type=Path, default=Path("out/planck70"))
    ap.add_argument("--retained-target", type=float, default=0.97)
    ap.add_argument("--nside-out", type=int, default=64)
    args = ap.parse_args()

    argv = [
        "planck",
        "--fits", str(args.fits),
        "--out", str(args.out),
        "--retained-target", str(args.retained_target),
        "--nside-out", str(args.nside_out),
    ]
    raise SystemExit(huf_main(argv))

if __name__ == "__main__":
    main()
