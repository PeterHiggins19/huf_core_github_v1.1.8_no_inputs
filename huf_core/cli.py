from __future__ import annotations
import argparse
from pathlib import Path
import json
import pandas as pd

from .core import HUFCore, HUFConfig
from .io import write_artifacts
from .adapters import (
    planck_lfi70_pixel_energy_elements,
    planck_error_metric_from_budget,
    markham_2018_fund_expenditure_elements,
    traffic_phase_band_elements,
    traffic_anomaly_elements
)

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="huf", description="HUF Core runner (contract + artifacts).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_planck = sub.add_parser("planck", help="Run Planck LFI 70GHz pixel-energy HUF demo.")
    p_planck.add_argument("--fits", required=True, type=Path)
    p_planck.add_argument("--out", required=True, type=Path)
    p_planck.add_argument("--retained-target", type=float, default=0.97)
    p_planck.add_argument("--nside-out", type=int, default=64)

    p_tr = sub.add_parser("traffic", help="Run traffic phase-band compression demo.")
    p_tr.add_argument("--csv", required=True, type=Path)
    p_tr.add_argument("--out", required=True, type=Path)
    p_tr.add_argument("--tau-local", type=float, default=0.05)

    p_an = sub.add_parser("traffic-anomaly", help="Run traffic anomaly diagnostic adapter.")
    p_an.add_argument("--csv", required=True, type=Path)
    p_an.add_argument("--out", required=True, type=Path)
    p_an.add_argument("--tau-global", type=float, default=0.0005, help="Global exclusion threshold. Note: 0.005 can exclude all elements on the bundled Toronto CSV; 0.0005 is a safer default.")
    p_an.add_argument("--status", action="append", default=["Green Termination"])
    p_an.add_argument("--include-call-text", action="store_true")

    p_mk = sub.add_parser("markham", help="Run Markham 2018 fund×account expenditure HUF demo.")
    p_mk.add_argument("--xlsx", required=True, type=Path)
    p_mk.add_argument("--out", required=True, type=Path)
    p_mk.add_argument("--tau-global", type=float, default=0.005)
    p_mk.add_argument("--tau-local", type=float, default=0.02)

    args = ap.parse_args(argv)

    if args.cmd == "planck":
        elements, meta = planck_lfi70_pixel_energy_elements(args.fits, nside_out=args.nside_out)
        # Determine tau from retained-target (keep the smallest rho among the kept set)
        tmp = elements.copy()
        tmp["rho"] = tmp["value"] / tmp["value"].sum()
        sorted_rho = tmp["rho"].sort_values(ascending=False).to_numpy()
        cum = sorted_rho.cumsum()
        import numpy as np
        k = int(np.searchsorted(cum, args.retained_target) + 1)
        tau = float(sorted_rho[min(k-1, len(sorted_rho)-1)])

        core = HUFCore(elements, dataset_id=meta["dataset_id"])
        cfg = HUFConfig(budget_type="energy", exclusion="global", tau=tau)

        artifacts = core.cycle(cfg)  # error metric derived exactly from discarded budget (Parseval-style accounting)
        discarded = artifacts["error_budget"]["discarded_budget_global"]
        artifacts["error_budget"].update(planck_error_metric_from_budget(meta, discarded))
        write_artifacts(args.out, artifacts)

        # Stability packet sweep
        sweep = [tau * s for s in (0.8, 0.9, 1.0, 1.1, 1.2)]
        sp = core.stability_packet(cfg, sweep)
        sp.to_csv(args.out / "stability_packet.csv", index=False)
        (args.out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return 0

    if args.cmd == "traffic":
        elements, meta = traffic_phase_band_elements(args.csv)
        core = HUFCore(elements, dataset_id=meta["dataset_id"])
        cfg = HUFConfig(budget_type="mass", exclusion="local", tau=float(args.tau_local))
        # TV error metric between original and post-exclusion distribution
        def tv_metric(kept):
            import numpy as np
            # original
            full = elements.copy()
            full["rho"] = full["value"] / full["value"].sum()
            kept2 = kept.copy()
            kept2["rho"] = kept2["value"] / kept2["value"].sum()
            merged = full.merge(kept2[["element_id","rho"]], on="element_id", how="left", suffixes=("_pre", "_post"))
            merged["rho_post"] = merged["rho_post"].fillna(0.0)
            tv = 0.5 * float(np.abs(merged["rho_pre"] - merged["rho_post"]).sum())
            return {"metric": "total_variation_over_elements", "tv": tv}
        artifacts = core.cycle(cfg, error_metric=tv_metric)
        write_artifacts(args.out, artifacts)

        sweep = [0.02, 0.03, 0.05, 0.07, 0.10]
        sp = core.stability_packet(cfg, sweep)
        sp.to_csv(args.out / "stability_packet.csv", index=False)
        (args.out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return 0

    if args.cmd == "traffic-anomaly":
        elements, meta = traffic_anomaly_elements(args.csv, anomaly_status=args.status, include_call_text=args.include_call_text)
        core = HUFCore(elements, dataset_id=meta["dataset_id"])
        cfg = HUFConfig(budget_type="mass", exclusion="global", tau=float(args.tau_global))
        artifacts = core.cycle(cfg)
        write_artifacts(args.out, artifacts)
        sweep = [cfg.tau * s for s in (0.5, 0.75, 1.0, 1.25, 1.5)]
        sp = core.stability_packet(cfg, sweep)
        sp.to_csv(args.out / "stability_packet.csv", index=False)
        (args.out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return 0

    if args.cmd == "markham":
        elements, meta = markham_2018_fund_expenditure_elements(args.xlsx)
        core = HUFCore(elements, dataset_id=meta["dataset_id"])

        # Two-threshold exclusion: keep if global>=tau_global OR local>=tau_local.
        cfg = HUFConfig(budget_type="mass", exclusion="dual", tau=float(args.tau_global), tau_local=float(args.tau_local))

        # Error metric: total variation equals discarded mass under nonnegative budgets.
        def tv_metric(kept_df):
            import numpy as np
            full2 = elements.copy(); full2["rho"] = full2["value"]/full2["value"].sum()
            kept2 = kept_df.copy(); kept2["rho"] = kept2["value"]/kept2["value"].sum()
            merged = full2.merge(kept2[["element_id","rho"]], on="element_id", how="left", suffixes=("_pre","_post"))
            merged["rho_post"] = merged["rho_post"].fillna(0.0)
            tv = 0.5 * float(np.abs(merged["rho_pre"] - merged["rho_post"]).sum())
            return {"metric": "total_variation_over_elements", "tv": tv}

        artifacts = core.cycle(cfg, error_metric=tv_metric)
        artifacts["meta"] = meta
        artifacts["meta"].update({"tau_global": float(args.tau_global), "tau_local": float(args.tau_local)})
        write_artifacts(args.out, artifacts)

        # Stability packet: sweep tau_global (tau_local fixed)
        sweep = [0.0025, 0.005, 0.0075, 0.01, 0.015]
        sp = core.stability_packet(cfg, sweep)
        sp.to_csv(args.out / "stability_packet.csv", index=False)
        (args.out / "meta.json").write_text(json.dumps(artifacts["meta"], indent=2), encoding="utf-8")
        return 0



    return 2

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
