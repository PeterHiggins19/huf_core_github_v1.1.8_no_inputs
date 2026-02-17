#!/usr/bin/env python3
"""Fetch public input datasets for HUF reference cases.

This repo ships artifacts and code, but **does not bundle large upstream inputs**.
This helper pulls the two civic datasets automatically and prints guided steps for Planck.

What it can do automatically:
- Markham (Ontario): 2018 corporate-wide budget workbook (XLSX)
- Toronto (Ontario): traffic-signal phase status (CSV) via the Open Data Portal (CKAN Action API)

What it does *not* download by default:
- Planck LFI 70 GHz PR3 map (FITS) — large binary (~480–500MB). The script prints
  a guided/manual download flow for either ESA PLA or NASA/IPAC IRSA.

Usage examples:
  python scripts/fetch_data.py --markham --toronto
  python scripts/fetch_data.py --toronto --toronto-query "traffic signal phase status"
  python scripts/fetch_data.py --planck-guide

Notes:
- The Toronto portal is CKAN-backed; we use the public Action API (no key required).
- If the Toronto query returns multiple candidates, you'll be prompted to choose.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import sys
import tempfile
import textwrap
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

# ----------------------------- Defaults -----------------------------

DEFAULT_MARKHAM_XLSX_URL = (
    "https://maps.markham.ca/OpenDataSite_Tables/"
    "2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx"
)

DEFAULT_TORONTO_CKAN_BASE = "https://open.toronto.ca/api/3/action"
DEFAULT_TORONTO_QUERY = "traffic signal phase status"

# IRSA PR3 direct map file (PR3 all-sky maps, LFI 70 GHz, NSIDE 1024)
IRSA_PLANCK70_FITS_URL = (
    "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/"
    "LFI_SkyMap_070_1024_R3.00_full.fits"
)
IRSA_PLANCK70_PREVIEW_URL = (
    "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/previews/"
    "LFI_SkyMap_070_1024_R3.00_full/index.html"
)
IRSA_PLANCK_PR3_ALLSKY_URL = "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/"
ESA_PLA_URL = "https://pla.esac.esa.int/"

# Expected local paths (relative to repo root)
MARKHAM_DEST = Path("cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx")
TORONTO_DEST = Path("cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv")
TORONTO_DEST_2 = Path("cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv")
PLANCK_DEST = Path("cases/planck70/inputs/LFI_SkyMap_070_1024_R3.00_full.fits")


# ----------------------------- IO helpers -----------------------------

def _http_get_json(url: str, timeout: int = 60) -> Dict[str, Any]:
    req = Request(url, headers={"User-Agent": "huf-fetch-data/1.1"})
    with urlopen(req, timeout=timeout) as r:
        data = r.read().decode("utf-8")
    return json.loads(data)


def _download(url: str, dest: Path, *, timeout: int = 300, overwrite: bool = False) -> None:
    dest = Path(dest)
    if dest.exists() and not overwrite:
        print(f"[skip] {dest} already exists")
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "huf-fetch-data/1.1"})

    print(f"[get] {url}")
    try:
        with urlopen(req, timeout=timeout) as r, open(dest, "wb") as f:
            shutil.copyfileobj(r, f, length=1024 * 1024)
    except (HTTPError, URLError) as e:
        raise RuntimeError(f"Download failed: {url} ({e})") from e

    print(f"[ok ] wrote {dest}")


def _repo_root() -> Path:
    # script lives at repo_root/scripts/fetch_data.py
    return Path(__file__).resolve().parents[1]


# ----------------------------- CKAN helpers (Toronto) -----------------------------

def _ckan_action(base: str, action: str, **params: Any) -> Dict[str, Any]:
    base = base.rstrip("/")
    url = f"{base}/{action}"
    if params:
        url += "?" + urlencode(params)
    payload = _http_get_json(url)
    if not payload.get("success"):
        err = payload.get("error")
        raise RuntimeError(f"CKAN action failed: {action} error={err}")
    return payload["result"]


def _pick(prompt: str, items: List[str], *, assume_yes: bool = False, default: int = 0) -> int:
    if not items:
        raise ValueError("No items to pick from")
    if assume_yes:
        return default

    print("\n" + prompt)
    for i, s in enumerate(items, start=1):
        print(f"  {i:>2}. {s}")

    while True:
        raw = input(f"Choose [1-{len(items)}] (default {default+1}): ").strip()
        if raw == "":
            return default
        if raw.isdigit() and 1 <= int(raw) <= len(items):
            return int(raw) - 1
        print("Invalid selection.")


def _best_resource_index(resources: List[Dict[str, Any]]) -> int:
    # Prefer explicit CSV resources; otherwise fallback to the first.
    scored: List[Tuple[int, int]] = []
    for idx, r in enumerate(resources):
        fmt = str(r.get("format", "")).lower()
        url = str(r.get("url", "")).lower()
        score = 0
        if fmt == "csv" or url.endswith(".csv"):
            score += 100
        if fmt == "zip" or url.endswith(".zip"):
            score += 50
        if "datastore" in url:
            score += 10
        scored.append((score, idx))
    scored.sort(reverse=True)
    return scored[0][1]


def _download_toronto_csv(
    base: str,
    dest_paths: List[Path],
    *,
    query: Optional[str] = None,
    package_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    assume_yes: bool = False,
    overwrite: bool = False,
) -> None:
    """Download Toronto traffic CSV.

    Resolution order:
      1) If resource_id is provided, download that CKAN resource.
      2) Else if package_id is provided, list resources and choose one.
      3) Else run package_search(query), choose a package, then a resource.

    If the chosen resource is a ZIP, we extract the largest CSV inside.
    """

    base = base.rstrip("/")
    root = _repo_root()

    # 1) Find package/resource
    pkg: Optional[Dict[str, Any]] = None
    resources: List[Dict[str, Any]] = []

    if resource_id:
        # Need package_show to find resource URL (resource_show exists but not always enabled)
        # Try resource_show; fallback to searching packages.
        try:
            res = _ckan_action(base, "resource_show", id=resource_id)
            resources = [res]
        except Exception:
            # Fallback: brute search by resource id in a wide query
            sr = _ckan_action(base, "package_search", q=resource_id, rows=10)
            pkgs = sr.get("results", [])
            for p in pkgs:
                pfull = _ckan_action(base, "package_show", id=p.get("id") or p.get("name"))
                for r in pfull.get("resources", []):
                    if r.get("id") == resource_id:
                        pkg = pfull
                        resources = [r]
                        break
                if resources:
                    break
            if not resources:
                raise RuntimeError(f"Could not resolve resource_id={resource_id}")

    if not resources:
        if package_id:
            pkg = _ckan_action(base, "package_show", id=package_id)
            resources = list(pkg.get("resources", []))
        else:
            q = (query or DEFAULT_TORONTO_QUERY).strip()
            sr = _ckan_action(base, "package_search", q=q, rows=10)
            pkgs = sr.get("results", [])
            if not pkgs:
                raise RuntimeError(
                    f"No Toronto datasets found for query={q!r}. "
                    "Try --toronto-query with different keywords or pass --toronto-package."
                )

            labels = [f"{p.get('title','(no title)')}  (name={p.get('name')})" for p in pkgs]
            pidx = _pick("Toronto dataset candidates:", labels, assume_yes=assume_yes, default=0)
            pkg = _ckan_action(base, "package_show", id=pkgs[pidx].get("id") or pkgs[pidx].get("name"))
            resources = list(pkg.get("resources", []))

    if not resources:
        raise RuntimeError("Selected Toronto package has no resources")

    # 2) Choose resource
    if len(resources) == 1:
        ridx = 0
    else:
        labels = []
        for r in resources:
            fmt = str(r.get("format", "")).strip() or "?"
            name = str(r.get("name", "")).strip() or "(no name)"
            labels.append(f"{name}  [format={fmt}]  (id={r.get('id')})")
        ridx_default = _best_resource_index(resources)
        ridx = _pick("Resources in selected Toronto dataset:", labels, assume_yes=assume_yes, default=ridx_default)

    res = resources[ridx]
    url = str(res.get("url", "")).strip()
    if not url:
        raise RuntimeError("Chosen Toronto resource has no URL")

    # 3) Download
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        parsed = urlparse(url)
        leaf = Path(parsed.path).name or "download"
        tmp = td_path / leaf
        _download(url, tmp, overwrite=True)

        # If ZIP, extract CSV.
        final_csv: Optional[Path] = None
        if tmp.suffix.lower() == ".zip":
            with zipfile.ZipFile(tmp, "r") as z:
                members = [m for m in z.namelist() if m.lower().endswith(".csv")]
                if not members:
                    raise RuntimeError("Downloaded ZIP contains no CSV")
                # choose largest CSV inside
                members.sort(key=lambda m: z.getinfo(m).file_size, reverse=True)
                target = members[0]
                z.extract(target, td_path)
                final_csv = td_path / target
        else:
            final_csv = tmp

        assert final_csv is not None

        for rel_dest in dest_paths:
            dest = root / rel_dest
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and not overwrite:
                print(f"[skip] {dest} already exists")
                continue
            shutil.copy2(final_csv, dest)
            print(f"[ok ] wrote {dest}")

    # Print a small schema hint (what adapters expect)
    print("\nToronto schema expected by HUF traffic adapters:")
    print("  required columns: TCS, PHASE")
    print("  optional columns: PHASE_STATUS_TEXT, PHASE_CALL_TEXT")


# ----------------------------- Planck guide -----------------------------

def _print_planck_guide() -> None:
    root = _repo_root()
    dest = root / PLANCK_DEST

    msg = f"""
    Planck input is intentionally NOT downloaded automatically.

    Why: the LFI 70 GHz PR3 map FITS is large (~480–500MB) and users often choose
    between ESA PLA and NASA/IPAC IRSA (and sometimes different products/releases).

    Expected local path for this repo:
      {PLANCK_DEST.as_posix()}

    Option A (NASA/IPAC IRSA) — direct download:
      1) Open the preview page and click "Download HEALPix FITS file":
         {IRSA_PLANCK70_PREVIEW_URL}
      2) Or download directly with curl/wget (resume-friendly):

         curl -L -o "{dest.as_posix()}" "{IRSA_PLANCK70_FITS_URL}"

      IRSA PR3 all-sky maps landing page (includes a generated download script):
         {IRSA_PLANCK_PR3_ALLSKY_URL}

    Option B (ESA Planck Legacy Archive):
      1) Visit PLA and browse/select PR3 products in the Maps section:
         {ESA_PLA_URL}

    After placing the FITS, run:
      pip install -e ".[planck]"
      huf planck --fits "{PLANCK_DEST.as_posix()}" --out out/planck70 --retained-target 0.97 --nside-out 64
    """

    print(textwrap.dedent(msg).strip() + "\n")


# ----------------------------- CLI -----------------------------

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="fetch_data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            Fetch public input datasets for HUF cases.

            By default, this script writes into the repo's cases/*/inputs/ folders.
            """
        ),
    )

    ap.add_argument("--markham", action="store_true", help="Download Markham 2018 budget XLSX.")
    ap.add_argument("--toronto", action="store_true", help="Download Toronto traffic signal phase-status CSV.")
    ap.add_argument("--planck-guide", action="store_true", help="Print guided/manual download steps for Planck.")

    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    ap.add_argument("--yes", action="store_true", help="Non-interactive: pick first/best options.")

    # Markham
    ap.add_argument("--markham-url", default=DEFAULT_MARKHAM_XLSX_URL, help="Override Markham XLSX URL.")

    # Toronto
    ap.add_argument("--toronto-ckan", default=DEFAULT_TORONTO_CKAN_BASE, help="Toronto CKAN Action API base URL.")
    ap.add_argument("--toronto-query", default=DEFAULT_TORONTO_QUERY, help="Search query for the Toronto dataset.")
    ap.add_argument("--toronto-package", default=None, help="Exact Toronto CKAN package id/name.")
    ap.add_argument("--toronto-resource", default=None, help="Exact Toronto CKAN resource id.")

    args = ap.parse_args(argv)

    if not (args.markham or args.toronto or args.planck_guide):
        ap.print_help()
        return 0

    os.chdir(_repo_root())

    if args.markham:
        _download(args.markham_url, MARKHAM_DEST, overwrite=args.overwrite)

    if args.toronto:
        _download_toronto_csv(
            args.toronto_ckan,
            [TORONTO_DEST, TORONTO_DEST_2],
            query=args.toronto_query,
            package_id=args.toronto_package,
            resource_id=args.toronto_resource,
            assume_yes=args.yes,
            overwrite=args.overwrite,
        )

    if args.planck_guide:
        _print_planck_guide()

    # Helpful reminder
    if args.markham or args.toronto:
        today = _dt.date.today().isoformat()
        print(f"\nDone. (Fetched on {today})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
