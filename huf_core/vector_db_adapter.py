from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import json

import numpy as np
import pandas as pd


def _file_fingerprint(path: Path) -> str:
    stat = path.stat()
    return f"{path.name}|{stat.st_size}|{int(stat.st_mtime)}"


@dataclass(frozen=True)
class VectorDBAdapterConfig:
    """
    Interpret a vector database retrieval dump as HUF finite elements.

    Supported inputs:
      - JSONL: one object per line
      - CSV / TSV

    Required fields:
      - id (string)
      - score (float)

    Optional fields:
      - namespace / collection / cluster / source -> used to form regimes

    Notes:
      - HUF expects nonnegative values. If your retrieval scores can be negative,
        choose a nonneg_mode:
          * "clip": negatives become 0
          * "shift": subtract the minimum so everything becomes >= 0
    """

    id_field: str = "id"
    score_field: str = "score"
    regime_field: str = "namespace"
    nonneg_mode: str = "clip"  # "clip" or "shift"
    top_k: Optional[int] = None
    trace_include_fields: Optional[List[str]] = None


def vector_db_results_to_elements(
    path: Path,
    cfg: VectorDBAdapterConfig = VectorDBAdapterConfig(),
    query_label: str = "query",
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convert a retrieval dump (JSONL/CSV/TSV) into a HUF elements DataFrame.

    Returns:
      elements DataFrame with required columns:
        - element_id, regime_id, value, trace_path, inputs_ref, method_ref
      meta dict suitable for `meta.json`
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".jsonl":
        rows: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.lstrip("\ufeff").strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        df = pd.DataFrame(rows)
    elif path.suffix.lower() in (".csv", ".tsv"):
        sep = "\t" if path.suffix.lower() == ".tsv" else ","
        df = pd.read_csv(path, sep=sep)
    else:
        raise ValueError("Supported inputs: .jsonl, .csv, .tsv")

    for col in (cfg.id_field, cfg.score_field):
        if col not in df.columns:
            raise ValueError(f"Missing required field '{col}' in {path.name}")

    df = df.copy()
    df[cfg.id_field] = df[cfg.id_field].astype(str)
    df[cfg.score_field] = pd.to_numeric(df[cfg.score_field], errors="coerce")
    df = df.dropna(subset=[cfg.score_field])

    if cfg.top_k is not None:
        df = df.sort_values(cfg.score_field, ascending=False).head(int(cfg.top_k))

    scores = df[cfg.score_field].astype(float).to_numpy()
    min_score = float(np.min(scores)) if scores.size else 0.0

    # Enforce nonnegative values for HUF
    if min_score < 0:
        if cfg.nonneg_mode == "clip":
            scores = np.clip(scores, 0.0, None)
        elif cfg.nonneg_mode == "shift":
            scores = scores - min_score
        else:
            raise ValueError("nonneg_mode must be 'clip' or 'shift'")

    df["_score_nonneg"] = scores

    # Regime assignment
    if cfg.regime_field in df.columns:
        regimes = df[cfg.regime_field].fillna("Global").astype(str)
    else:
        regimes = pd.Series(["Global"] * len(df), index=df.index)

    df["_reg"] = regimes

    def make_element_id(r: pd.Series) -> str:
        rid = str(r[cfg.id_field]).replace(" ", "_")
        reg = str(r["_reg"]).replace(" ", "_")
        return f"{reg}/id={rid}"

    elements = pd.DataFrame(
        {
            "element_id": df.apply(make_element_id, axis=1),
            "regime_id": df["_reg"].astype(str),
            "value": df["_score_nonneg"].astype(float),
        }
    )

    # Trace points back to the retrieval record (and optional extra fields)
    extras = cfg.trace_include_fields or []
    kept_extras = [
        c
        for c in extras
        if c in df.columns and c not in (cfg.id_field, cfg.score_field)
    ]

    trace: List[str] = []
    for _, r in df.iterrows():
        t = [
            "VectorDBResults",
            f"query={query_label}",
            f"id={r[cfg.id_field]}",
            f"score={float(r[cfg.score_field])}",
        ]
        if cfg.regime_field in df.columns:
            t.append(f"{cfg.regime_field}={r[cfg.regime_field]}")
        for c in kept_extras:
            try:
                t.append(f"{c}={r[c]}")
            except Exception:
                pass
        trace.append(json.dumps(t))
    elements["trace_path"] = trace

    inputs_ref = _file_fingerprint(path)
    elements["inputs_ref"] = inputs_ref
    elements[
        "method_ref"
    ] = (
        "vector_db_results_to_elements("
        f"id_field={cfg.id_field},"
        f"score_field={cfg.score_field},"
        f"regime_field={cfg.regime_field},"
        f"nonneg_mode={cfg.nonneg_mode})"
    )

    dataset_id = hashlib.sha256((inputs_ref + "|" + query_label).encode("utf-8")).hexdigest()[
        :16
    ]
    meta: Dict[str, Any] = {
        "dataset_id": dataset_id,
        "query_label": query_label,
        "source_file": path.name,
        "rows_loaded": int(df.shape[0]),
        "regimes": int(elements["regime_id"].nunique()),
        "nonneg_mode": cfg.nonneg_mode,
        "min_score_original": float(min_score),
        "note": (
            "Interpret vector DB retrieval scores as a unity budget for auditability. "
            "HUF normalizes internally and emits artifacts explaining dominance and exclusions."
        ),
    }
    return elements, meta
