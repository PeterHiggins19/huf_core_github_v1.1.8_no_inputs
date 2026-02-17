from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Any
import json
import math
import hashlib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timezone

REQUIRED_TRACE_FIELDS = ("item_id", "regime_path", "rho_global_post", "inputs_ref", "method_ref", "discarded_budget_global")

@dataclass(frozen=True)
class HUFConfig:
    """Core configuration for a single HUF cycle."""
    budget_type: str  # "mass" or "energy"
    exclusion: str    # "global" or "local"
    tau: float        # threshold in the chosen frame
    tau_local: Optional[float] = None  # optional second threshold for dual exclusion
    regime_local_unity: bool = True
    seed: int = 0

@dataclass(frozen=True)
class RunStamp:
    dataset_id: str
    code_hash: str
    param_hash: str
    created_utc: str
    run_id: str

def _hash_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def make_run_stamp(dataset_id: str, config: HUFConfig, code_fingerprint: str) -> RunStamp:
    created = datetime.now(timezone.utc).isoformat()
    param_hash = _hash_text(json.dumps(config.__dict__, sort_keys=True))
    run_id = _hash_text(dataset_id + "|" + param_hash + "|" + created)
    return RunStamp(
        dataset_id=dataset_id,
        code_hash=_hash_text(code_fingerprint),
        param_hash=param_hash,
        created_utc=created,
        run_id=run_id
    )

def normalize_series(x: pd.Series) -> pd.Series:
    s = float(x.sum())
    if s <= 0:
        raise ValueError("Cannot normalize: sum <= 0")
    return x / s

def jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    A, B = set(a), set(b)
    if not A and not B:
        return 1.0
    return len(A & B) / max(1, len(A | B))

def spearman_rank_corr(x: pd.Series, y: pd.Series) -> float:
    # Spearman = Pearson of ranks
    rx = x.rank(method="average")
    ry = y.rank(method="average")
    vx = rx - rx.mean()
    vy = ry - ry.mean()
    denom = math.sqrt(float((vx * vx).sum()) * float((vy * vy).sum()))
    if denom == 0:
        return 0.0
    return float((vx * vy).sum() / denom)

class HUFCore:
    """
    Minimal, enforceable HUF cycle runner.
    Input is an 'elements' table with:
      - element_id (str)
      - regime_id  (str)
      - value      (nonnegative float)  (count, energy, etc.)
      - trace_path (json list[str]) OPTIONAL
      - inputs_ref (str) OPTIONAL
      - method_ref (str) OPTIONAL
    """

    def __init__(self, elements: pd.DataFrame, dataset_id: str, code_fingerprint: str = "huf_core_v1"):
        required = {"element_id", "regime_id", "value"}
        missing = required - set(elements.columns)
        if missing:
            raise ValueError(f"elements missing columns: {sorted(missing)}")
        if (elements["value"] < 0).any():
            raise ValueError("value must be nonnegative")
        self.elements = elements.copy()
        self.dataset_id = dataset_id
        self.code_fingerprint = code_fingerprint

    def cycle(
        self,
        config: HUFConfig,
        error_metric: Optional[Callable[[pd.DataFrame], Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Runs: Normalize -> (Propagate placeholder) -> Aggregate placeholder -> Exclusion -> Renormalize
        NOTE: Propagate and Aggregate are extension points; in core they are identity.
        Returns the four required artifacts + stamp.
        """
        df = self.elements.copy()

        # Normalize globally (pre)
        df["rho_global_pre"] = normalize_series(df["value"])

        # Local unity (pre)
        df["regime_total"] = df.groupby("regime_id")["value"].transform("sum")
        df["rho_local_pre"] = np.where(df["regime_total"] > 0, df["value"] / df["regime_total"], 0.0)

        # Propagate (core = identity). Aggregate (core = identity).

        # Exclusion
        if config.exclusion == "global":
            df["excluded"] = df["rho_global_pre"] < config.tau
        elif config.exclusion == "local":
            df["excluded"] = df["rho_local_pre"] < config.tau
        elif config.exclusion == "dual":
            if config.tau_local is None:
                raise ValueError("dual exclusion requires tau_local")
            df["excluded"] = (df["rho_global_pre"] < config.tau) & (df["rho_local_pre"] < float(config.tau_local))
        else:
            raise ValueError("exclusion must be 'global', 'local', or 'dual'")

        discarded_value = float(df.loc[df["excluded"], "value"].sum())
        total_value = float(df["value"].sum())
        discarded_budget_global = (discarded_value / total_value) if total_value > 0 else 0.0

        # Renormalize kept set globally
        kept = df.loc[~df["excluded"]].copy()
        if kept.empty:
            raise ValueError("Exclusion removed all elements; invalid run")
        kept["rho_global_post"] = normalize_series(kept["value"])

        # Renormalize kept set locally if requested
        kept["regime_kept_total"] = kept.groupby("regime_id")["value"].transform("sum")
        kept["rho_local_post"] = np.where(kept["regime_kept_total"] > 0, kept["value"] / kept["regime_kept_total"], 0.0)

        # Build artifacts
        coherence_map = self._artifact_coherence_map(df, kept, discarded_budget_global, config)
        active_set = self._artifact_active_set(kept, config)
        trace_report = self._artifact_trace(kept, discarded_budget_global, config)
        error_budget = self._artifact_error_budget(discarded_budget_global, config, error_metric, kept)

        stamp = make_run_stamp(self.dataset_id, config, self.code_fingerprint)

        artifacts = {
            "coherence_map": coherence_map,
            "active_set": active_set,
            "trace_report": trace_report,
            "error_budget": error_budget,
            "run_stamp": stamp.__dict__
        }

        self._validate_artifacts(artifacts)
        return artifacts

    def stability_packet(
        self,
        base_config: HUFConfig,
        tau_values: List[float],
        topk_regimes: int = 25
    ) -> pd.DataFrame:
        """
        Minimum stability packet:
          - 5-point threshold sweep
          - Active-set Jaccard vs baseline
          - Spearman rank correlation of top regime contributions vs baseline
          - Near-threshold band size (|rho - tau| <= 0.1*tau) on the relevant frame
        """
        if len(tau_values) < 3:
            raise ValueError("Provide at least 3 tau values")
        base = self.cycle(HUFConfig(**{**base_config.__dict__, "tau": tau_values[0]}))
        base_active = [r["item_id"] for r in base["active_set"]]
        base_reg = base["coherence_map"].set_index("regime_id")["rho_global_pre"].sort_values(ascending=False).head(topk_regimes)

        rows = []
        for tau in tau_values:
            cfg = HUFConfig(**{**base_config.__dict__, "tau": tau})
            try:
                art = self.cycle(cfg)
                active = [r["item_id"] for r in art["active_set"]]
                jac = jaccard(base_active, active)

                reg = art["coherence_map"].set_index("regime_id")["rho_global_pre"].sort_values(ascending=False).head(topk_regimes)
                # align
                reg_aligned = reg.reindex(base_reg.index).fillna(0.0)
                rho_corr = spearman_rank_corr(base_reg, reg_aligned)

                discarded = art["error_budget"]["discarded_budget_global"]
                active_count = len(active)
                invalid = False
            except ValueError:
                # Threshold too aggressive (removed all). Record as invalid point.
                active = []
                jac = 0.0
                rho_corr = 0.0
                discarded = 1.0
                active_count = 0
                invalid = True

            frame = "rho_global_pre" if cfg.exclusion in ("global","dual") else "rho_local_pre"
            df = self.elements.copy()
            df["rho_global_pre"] = normalize_series(df["value"])
            df["regime_total"] = df.groupby("regime_id")["value"].transform("sum")
            df["rho_local_pre"] = np.where(df["regime_total"] > 0, df["value"] / df["regime_total"], 0.0)
            near = df[(df[frame] >= 0.9 * tau) & (df[frame] <= 1.1 * tau)].shape[0]

            rows.append({
                "tau": tau,
                "active_count": active_count,
                "discarded_budget_global": discarded,
                "jaccard_vs_baseline": jac,
                "spearman_regime_rho_vs_baseline": rho_corr,
                "near_threshold_count": int(near),
                "invalid": bool(invalid)
            })
        return pd.DataFrame(rows)

    def _artifact_coherence_map(self, df_all: pd.DataFrame, kept: pd.DataFrame, discarded_budget_global: float, config: HUFConfig) -> pd.DataFrame:
        # Global regime shares are computed on PRE frame for interpretability
        reg_pre = df_all.groupby("regime_id")["rho_global_pre"].sum().rename("rho_global_pre")
        # Local unity checks (post)
        reg_post = kept.groupby("regime_id").apply(lambda g: float(g["rho_local_post"].sum())).rename("local_unity_post")
        reg_kept_share = kept.groupby("regime_id")["rho_global_post"].sum().rename("rho_global_post")
        reg_discard = df_all.groupby("regime_id").apply(lambda g: float(g.loc[g["excluded"], "rho_global_pre"].sum())).rename("rho_discarded_pre")
        out = pd.concat([reg_pre, reg_kept_share, reg_discard, reg_post], axis=1).fillna(0.0).reset_index()
        out["local_unity_ok_post"] = (out["local_unity_post"].abs() - 1.0).abs() < 1e-9
        out["global_discarded_budget"] = discarded_budget_global
        return out.sort_values("rho_global_pre", ascending=False).reset_index(drop=True)

    def _artifact_active_set(self, kept: pd.DataFrame, config: HUFConfig) -> List[Dict[str, Any]]:
        out = kept.sort_values("rho_global_post", ascending=False).copy()
        records = []
        for rank, row in enumerate(out.itertuples(index=False), start=1):
            records.append({
                "rank": rank,
                "item_id": str(row.element_id),
                "regime_id": str(row.regime_id),
                "rho_global_post": float(row.rho_global_post),
                "rho_global_pre": float(row.rho_global_pre),
                "rho_local_pre": float(row.rho_local_pre),
                "rho_local_post": float(row.rho_local_post),
                "value": float(row.value),
                "tau": float(config.tau),
                "exclusion": config.exclusion
            })
        return records

    def _artifact_trace(self, kept: pd.DataFrame, discarded_budget_global: float, config: HUFConfig) -> List[Dict[str, Any]]:
        # Minimal 6-field trace schema (+ optional extras)
        out = kept.sort_values("rho_global_post", ascending=False).copy()
        traces = []
        for row in out.itertuples(index=False):
            path = None
            if hasattr(row, "trace_path") and isinstance(row.trace_path, str) and row.trace_path.strip():
                try:
                    path = json.loads(row.trace_path)
                except Exception:
                    path = [str(row.regime_id), str(row.element_id)]
            else:
                path = [str(row.regime_id), str(row.element_id)]

            inputs_ref = getattr(row, "inputs_ref", "") if hasattr(row, "inputs_ref") else ""
            method_ref = getattr(row, "method_ref", "") if hasattr(row, "method_ref") else ""

            traces.append({
                "item_id": str(row.element_id),
                "regime_path": path,
                "rho_global_post": float(row.rho_global_post),
                "inputs_ref": str(inputs_ref),
                "method_ref": str(method_ref),
                "discarded_budget_global": float(discarded_budget_global)
            })
        return traces

    def _artifact_error_budget(
        self,
        discarded_budget_global: float,
        config: HUFConfig,
        error_metric: Optional[Callable[[pd.DataFrame], Dict[str, Any]]],
        kept: pd.DataFrame
    ) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "budget_type": config.budget_type,
            "discarded_budget_global": float(discarded_budget_global),
            "frame": "energy" if config.budget_type == "energy" else "mass",
        }
        if error_metric is not None:
            out.update(error_metric(kept))
        else:
            out["measured_error"] = None
            out["measured_error_note"] = "No error metric callback provided (empirical error is domain-specific)."
        return out

    def _validate_artifacts(self, artifacts: Dict[str, Any]) -> None:
        for key in ("coherence_map", "active_set", "trace_report", "error_budget", "run_stamp"):
            if key not in artifacts:
                raise ValueError(f"Missing required artifact: {key}")
        # trace schema
        for rec in artifacts["trace_report"]:
            for f in REQUIRED_TRACE_FIELDS:
                if f not in rec:
                    raise ValueError(f"Trace record missing field: {f}")


class HUFRun:
    """Compatibility wrapper for the older HUFRun API used in early drafts/tests.

    It builds a finite-element table from:
      - rho: dict[str, float] mapping element_id -> weight
      - regimes: dict[str, list[str]] mapping regime_id -> element_ids
    and runs a single HUF cycle.

    New code should prefer: HUFCore + HUFConfig.
    """

    def __init__(self, rho: Any, regimes: Dict[str, List[str]], budget_type: str = "mass", meta: Optional[Dict[str, Any]] = None):
        self.rho = rho
        self.regimes = regimes
        self.budget_type = budget_type
        self.meta = meta or {}

        # Build elements DataFrame
        rows = []
        if isinstance(rho, dict):
            # reverse lookup element -> regime (first match wins)
            elem_to_reg = {}
            for rid, elems in regimes.items():
                for e in elems:
                    elem_to_reg[e] = rid
            for eid, w in rho.items():
                rid = elem_to_reg.get(eid, next(iter(regimes.keys())))
                rows.append({"element_id": str(eid), "regime_id": str(rid), "value": float(w)})
        else:
            raise TypeError("HUFRun expects rho as dict[str, float] in this compatibility wrapper.")

        self.elements = pd.DataFrame(rows)
        self.dataset_id = self.meta.get("dataset_id", "hufrun")

    def cycle(self, tau_global: float = 0.0, tau_local: float = 0.0) -> Dict[str, Any]:
        core = HUFCore(self.elements, dataset_id=self.dataset_id)
        cfg = HUFConfig(budget_type=self.budget_type, exclusion="dual", tau=float(tau_global), tau_local=float(tau_local))
        art = core.cycle(cfg)
        art["meta"] = self.meta
        return art

    def write_artifacts(self, out_dir: Path, artifacts: Dict[str, Any]) -> None:
        from .io import write_artifacts
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        write_artifacts(out_dir, artifacts)
