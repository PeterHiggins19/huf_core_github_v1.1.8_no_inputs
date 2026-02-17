from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import hashlib
import json
import math
import numpy as np
import pandas as pd

try:
    from astropy.io import fits
except Exception:  # pragma: no cover
    fits = None

def _file_fingerprint(path: Path) -> str:
    stat = path.stat()
    return f"{path.name}|{stat.st_size}|{int(stat.st_mtime)}"

def planck_lfi70_pixel_energy_elements(
    fits_path: Path,
    nside_in: int = 1024,
    nside_out: int = 64,
    stokes_field: str = "I_STOKES"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Builds elements for the Planck LFI 70GHz map using pixel-basis energy and NESTED degrade.
    Finite elements (raw): fine pixels (nside_in)
    Aggregated elements: coarse pixels (nside_out) with value = sum(I^2) over the corresponding fine pixels
    Regimes: 12 HEALPix faces (coarse)
    """
    if fits is None:
        raise RuntimeError("astropy is required for FITS adapter")

    fits_path = Path(fits_path)
    with fits.open(fits_path, memmap=True) as hdul:
        h = hdul["FREQ-MAP"].header
        nside_hdr = int(h.get("NSIDE", nside_in))
        ordering = str(h.get("ORDERING", "NESTED"))
        data = hdul["FREQ-MAP"].data[stokes_field].astype(np.float64)

    if nside_hdr != nside_in:
        raise ValueError(f"Expected NSIDE={nside_in}, got {nside_hdr}")
    if ordering.upper() != "NESTED":
        raise ValueError("This adapter assumes NESTED ordering for exact power-of-two degrade.")

    ratio = nside_in // nside_out
    if ratio <= 0 or (ratio & (ratio - 1)) != 0:
        raise ValueError("nside_out must be a power-of-two divisor of nside_in.")
    group = ratio * ratio
    if data.size % group != 0:
        raise ValueError("Unexpected map length for the given NSIDE ratio.")
    coarse_npix = data.size // group

    I2 = data * data
    # In NESTED ordering, power-of-two degrade groups fine indices in contiguous blocks.
    coarse_energy = I2.reshape(coarse_npix, group).sum(axis=1)

    face_size = nside_out * nside_out
    faces = np.arange(coarse_npix) // face_size

    elements = pd.DataFrame({
        "element_id": [f"face{int(f):02d}/pix{int(i)%face_size:04d}" for i, f in enumerate(faces)],
        "regime_id": [f"face{int(f):02d}" for f in faces],
        "value": coarse_energy
    })
    # Useful refs for trace and audit
    elements["trace_path"] = [json.dumps([f"face{int(f):02d}", f"pix{int(i)%face_size:04d}", f"fine[{int(i)*group}:{int(i)*group+group-1}]"]) for i, f in enumerate(faces)]
    elements["inputs_ref"] = _file_fingerprint(fits_path)
    elements["method_ref"] = f"pixel_energy_nested_degrade(nside_in={nside_in},nside_out={nside_out},field={stokes_field})"

    meta = {
        "dataset_id": hashlib.sha256(_file_fingerprint(fits_path).encode("utf-8")).hexdigest()[:16],
        "nside_in": nside_in,
        "nside_out": nside_out,
        "ordering": ordering,
        "field": stokes_field,
        "fine_npix": int(data.size),
        "coarse_npix": int(coarse_npix),
        "group_size": int(group),
        "total_energy": float(I2.sum())
    }
    return elements, meta

def planck_error_metric_from_budget(meta: Dict[str, Any], discarded_budget_global: float) -> Dict[str, Any]:
    """
    For pixel-basis energy with exclusion implemented as zeroing excluded blocks,
    L2 error squared fraction equals discarded_budget_global exactly.
    """
    total_energy = float(meta["total_energy"])
    fine_npix = int(meta["fine_npix"])
    excluded_energy = total_energy * float(discarded_budget_global)
    rmse = math.sqrt(excluded_energy / fine_npix)
    return {
        "metric": "L2_RMSE_pixel_basis",
        "rmse": float(rmse),
        "excluded_energy": float(excluded_energy),
        "total_energy": float(total_energy),
        "note": "Exact equality: discarded_budget_global == ||Δf||_2^2 / ||f||_2^2 (pixel basis, energy budget)."
    }

def traffic_phase_band_elements(csv_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Compressed phase activity distribution.
    Finite elements: TCS x PHASE_BAND counts
    Regimes: TCS
    """
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    df["PHASE_BAND"] = df["PHASE"].apply(_phase_band)
    counts = df.groupby(["TCS", "PHASE_BAND"]).size().reset_index(name="count")
    elements = pd.DataFrame({
        "element_id": counts.apply(lambda r: f"TCS={int(r['TCS'])}/band={r['PHASE_BAND']}", axis=1),
        "regime_id": counts["TCS"].apply(lambda t: f"TCS={int(t)}"),
        "value": counts["count"].astype(float),
    })
    # trace points back to filter rules, not individual row ids by default
    elements["trace_path"] = counts.apply(lambda r: json.dumps(["Global", f"TCS={int(r['TCS'])}", f"PHASE_BAND={r['PHASE_BAND']}"]), axis=1)
    elements["inputs_ref"] = _file_fingerprint(csv_path)
    elements["method_ref"] = "counts(TCS x PHASE_BAND); PHASE_BAND={MajorEven(2,4,6,8),MinorOdd(1,3,5,7),Other(9-12)}"

    meta = {
        "dataset_id": hashlib.sha256(_file_fingerprint(csv_path).encode("utf-8")).hexdigest()[:16],
        "rows": int(df.shape[0]),
        "elements": int(elements.shape[0]),
        "regimes": int(elements["regime_id"].nunique()),
        "note": "Real dataset snapshot (City of Toronto traffic signal phase status). HUF requires schema fidelity and verifiable finite-element mapping."
    }
    return elements, meta

def traffic_anomaly_elements(csv_path: Path, anomaly_status: Optional[List[str]] = None, include_call_text: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Diagnostic adapter: identify intersections/phases that dominate declared anomaly statuses.
    Finite elements: TCS x PHASE x PHASE_STATUS_TEXT (+ optionally PHASE_CALL_TEXT)
    Regimes: TCS
    Budget: counts within the anomaly subset (conditional mass budget).
    """
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    df["PHASE_STATUS_TEXT"] = df["PHASE_STATUS_TEXT"].fillna("Unknown")

    if anomaly_status is None:
        anomaly_status = ["Green Termination"]

    dfa = df[df["PHASE_STATUS_TEXT"].isin(anomaly_status)].copy()

    group_cols = ["TCS", "PHASE", "PHASE_STATUS_TEXT"]
    if include_call_text and "PHASE_CALL_TEXT" in dfa.columns:
        dfa["PHASE_CALL_TEXT"] = dfa["PHASE_CALL_TEXT"].fillna("Unknown")
        group_cols.append("PHASE_CALL_TEXT")

    counts = dfa.groupby(group_cols).size().reset_index(name="count")

    def _id(r) -> str:
        base = f"TCS={int(r['TCS'])}/phase={int(r['PHASE'])}/status={r['PHASE_STATUS_TEXT']}"
        if include_call_text and "PHASE_CALL_TEXT" in counts.columns:
            base += f"/call={r['PHASE_CALL_TEXT']}"
        return base

    elements = pd.DataFrame({
        "element_id": counts.apply(_id, axis=1),
        "regime_id": counts["TCS"].apply(lambda t: f"TCS={int(t)}"),
        "value": counts["count"].astype(float),
    })

    elements["trace_path"] = counts.apply(lambda r: json.dumps([
        "AnomalySubset",
        f"TCS={int(r['TCS'])}",
        f"PHASE={int(r['PHASE'])}",
        f"PHASE_STATUS_TEXT={r['PHASE_STATUS_TEXT']}"
    ] + ([f"PHASE_CALL_TEXT={r['PHASE_CALL_TEXT']}"] if include_call_text and "PHASE_CALL_TEXT" in counts.columns else [])), axis=1)

    elements["inputs_ref"] = _file_fingerprint(csv_path)
    elements["method_ref"] = f"counts(TCS x PHASE x PHASE_STATUS_TEXT{' x PHASE_CALL_TEXT' if include_call_text else ''}) over anomaly subset={anomaly_status}"

    meta = {
        "dataset_id": hashlib.sha256((_file_fingerprint(csv_path) + str(anomaly_status)).encode("utf-8")).hexdigest()[:16],
        "anomaly_status": anomaly_status,
        "include_call_text": include_call_text,
        "rows_in_subset": int(dfa.shape[0]),
        "elements": int(elements.shape[0]),
        "regimes": int(elements['regime_id'].nunique()),
        "note": "Conditional budget: unity is over the anomaly subset only (diagnostic regime)."
    }
    return elements, meta


def markham_2018_fund_expenditure_elements(
    xlsx_path: Path,
    sheet: "str | int" = 0,
    units: str = "k$",
    section_label: str = "EXPENDITURES",
    start_row: int = 18,
    end_row_exclusive: int = 38,
    account_col: int = 0,
    fund_cols: Optional[List[int]] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Markham (city budget) adapter.

    Source file (as provided): 2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx
    We treat the EXPENDITURES block as a mass/weight budget.

    Finite element: Fund × ExpenditureAccount (line item)
    Regime: Fund
    Value: Amount in units (default k$)

    This adapter is intentionally explicit and reproducible:
    - All row/column coordinates are parameters.
    - Each element carries a source cell reference in trace_path.
    """
    xlsx_path = Path(xlsx_path)
    raw = pd.read_excel(xlsx_path, sheet_name=sheet, header=None)

    if fund_cols is None:
        # As in the provided sheet: columns 1..6 are funds; column 7 is total.
        fund_cols = list(range(1, 7))

    fund_names = {c: str(raw.iloc[0, c]).strip() for c in fund_cols}

    block = raw.iloc[start_row:end_row_exclusive, [account_col] + fund_cols].copy()
    block.columns = ["Account"] + [fund_names[c] for c in fund_cols]
    block = block[~block["Account"].isna()]

    long = block.melt(id_vars=["Account"], var_name="Fund", value_name="Amount")
    long = long.dropna()
    long["Amount"] = pd.to_numeric(long["Amount"], errors="coerce")
    long = long.dropna()
    long = long[long["Amount"] != 0]

    def _eid(r) -> str:
        a = str(r["Account"]).strip().replace(" ", "_")
        f = str(r["Fund"]).strip().replace(" ", "_")
        return f"Fund={f}/Account={a}"

    elements = pd.DataFrame({
        "element_id": long.apply(_eid, axis=1),
        "regime_id": long["Fund"].apply(lambda x: f"Fund={str(x).strip()}"),
        "value": long["Amount"].astype(float),
    })

    def _cell(account: str, fund: str) -> str:
        ridx = int(block.index[block["Account"] == account][0])
        fund_names_list = [fund_names[c] for c in fund_cols]
        cidx = (["Account"] + fund_names_list).index(fund)
        excel_col = chr(ord("A") + cidx)
        excel_row = ridx + 1
        return f"{excel_col}{excel_row}"

    elements["trace_path"] = [
        json.dumps([
            "CityBudget2018",
            section_label,
            f"Fund={f}",
            f"Account={a}",
            f"source_cell={_cell(a, f)}",
        ])
        for a, f in zip(long["Account"], long["Fund"])
    ]

    elements["inputs_ref"] = _file_fingerprint(xlsx_path)
    elements["method_ref"] = (
        f"markham_2018_fund_expenditure_elements(sheet={sheet},rows={start_row}:{end_row_exclusive},"
        f"fund_cols={fund_cols},units={units})"
    )

    total = float(elements["value"].sum())
    meta = {
        "dataset_id": hashlib.sha256(_file_fingerprint(xlsx_path).encode("utf-8")).hexdigest()[:16],
        "units": units,
        "section": section_label,
        "rows_block": [start_row, end_row_exclusive],
        "funds": [fund_names[c] for c in fund_cols],
        "elements": int(elements.shape[0]),
        "regimes": int(elements["regime_id"].nunique()),
        "total_value": total,
        "note": "Unity uses the line-item sum across funds. If the sheet TOTAL differs by 1–2 units, treat as rounding.",
    }
    return elements, meta

def _phase_band(ph) -> str:
    try:
        p = int(ph)
    except Exception:
        return "Other(9-12)"
    if p in (2, 4, 6, 8):
        return "MajorEven(2,4,6,8)"
    if p in (1, 3, 5, 7):
        return "MinorOdd(1,3,5,7)"
    return "Other(9-12)"
