#!/usr/bin/env python
"""
Fetch external input data for the HUF-Core examples/cases.

Windows examples:
  .venv\\Scripts\\python scripts\\fetch_data.py --toronto --yes
  .venv\\Scripts\\python scripts\\fetch_data.py --markham --toronto --yes

Notes:
- Toronto fetch uses Toronto Open Data CKAN "action" API to locate the Traffic Signals Timing ZIP and
  copies the extracted CSV into both traffic cases.
- Markham fetch downloads a small 2018 budget Excel file used by the Markham demo case.
- Planck is guided/manual because the files are large.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import sys
import tempfile
import textwrap
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZipFile


# ----------------------------- Repo paths -----------------------------

def _repo_root(start: Optional[Path] = None) -> Path:
    """
    Best-effort repo root discovery, walking upward until we find a marker file.
    Works even when invoked from arbitrary CWD.
    """
    here = (start or Path(__file__).resolve()).parent
    markers = ("pyproject.toml", ".git", "cases")
    for p in [here] + list(here.parents):
        if any((p / m).exists() for m in markers):
            return p
    return Path.cwd().resolve()


# ----------------------------- Defaults -----------------------------

# Toronto CKAN "action" base. (As of 2026-02-17, this base was confirmed working by the user.)
DEFAULT_TORONTO_CKAN_BASE = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"
TORONTO_CKAN_BASE_FALLBACKS = [
    DEFAULT_TORONTO_CKAN_BASE,
    'https://open.toronto.ca/api/3/action',
]

TORONTO_ENV = "HUF_TORONTO_CKAN"

# Markham budget XLSX. The City has moved links over time, so we try a short list.
DEFAULT_MARKHAM_URLS: List[str] = [
    # Markham Open Data (often stable):
    "https://maps.markham.ca/OpenDataSite_Tables/Markham_Consolidated_Budget_By_Dept_and_Funding_Source_2018.xlsx",
    # Legacy Markham site link (may 404):
    "https://www.markham.ca/wps/wcm/connect/markham/8e2d0d17-6a80-4c7d-bb7c-4d7f6dc7f4b8/2018+Budget.xlsx",
]
MARKHAM_ENV = "HUF_MARKHAM_URL"

# Destinations (repo-relative)
MARKHAM_DEST = Path("cases/markham2018/inputs/2018-Budget-Allocation-of-Revenue-and-Expenditure-by-Fund.xlsx")

# Toronto traffic CSV is used by two example cases.
TORONTO_DESTS = [
    Path("cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv"),
    Path("cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv"),
]

# Toronto dataset search query used against CKAN.
DEFAULT_TORONTO_PACKAGE_Q = "traffic signals timing"

# Planck (manual)
PLANCK_DEST = Path("cases/planck70/inputs/HFI_SkyMap_070_2048_R3.01_full.fits")
IRSA_PLANCK_PR3_ALLSKY_URL = "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/"
IRSA_PLANCK70_PREVIEW_URL = (
    "https://irsa.ipac.caltech.edu/applications/planck/#details=imp%3DAll%20Sky%20Maps%20%28PR3%29%26sel%3D"
    "irsa.ipac.planck%21all_sky_maps%21HFI_SkyMap_070_2048_R3.01_full.fits"
)
IRSA_PLANCK70_FITS_URL = "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/HFI_SkyMap_070_2048_R3.01_full.fits"
ESA_PLA_URL = "https://pla.esac.esa.int/"


# ----------------------------- Helpers -----------------------------

def _maybe_inject_truststore() -> None:
    """
    On Windows, certificate chains can sometimes be awkward in corporate environments.
    If `truststore` is installed, inject it so urllib uses the OS trust store.
    """
    try:
        import truststore  # type: ignore
    except Exception:
        return
    try:
        truststore.inject_into_ssl()
    except Exception:
        # Non-fatal; continue with default SSL handling.
        return


def _urlopen(req: Request, timeout: int = 30):
    return urlopen(req, timeout=timeout)


def _http_get_json(url: str, timeout: int = 30) -> Dict[str, Any]:
    req = Request(url, headers={"User-Agent": "huf-core-fetch-data/1"})
    with _urlopen(req, timeout=timeout) as r:
        data = r.read()
    return json.loads(data.decode("utf-8"))


def _download(url: str, dest: Path, overwrite: bool = False, timeout: int = 60) -> bool:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists() and not overwrite:
        print(f"[skip] {dest} already exists")
        return True

    print(f"[get] {url}")
    req = Request(url, headers={"User-Agent": "huf-core-fetch-data/1"})
    try:
        with _urlopen(req, timeout=timeout) as r, tempfile.NamedTemporaryFile(delete=False) as tf:
            shutil.copyfileobj(r, tf)
            tmp_name = tf.name
        shutil.move(tmp_name, dest)
        print(f"[ok ] wrote {dest}")
        return True
    except HTTPError as e:
        print(f"[err] {e.code} {e.reason} for {url}")
        return False
    except URLError as e:
        print(f"[err] URL error for {url}: {e.reason}")
        return False
    except Exception as e:
        print(f"[err] failed to download {url}: {e}")
        return False


def _download_first(urls: Iterable[str], dest: Path, overwrite: bool = False) -> bool:
    for u in urls:
        if _download(u, dest, overwrite=overwrite):
            return True
    return False


# ----------------------------- Toronto (CKAN) -----------------------------

def _ckan_action(base: str, action: str, **params: Any) -> Dict[str, Any]:
    base = base.rstrip("/")
    action = action.lstrip("/")
    url = f"{base}/{action}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    payload = _http_get_json(url)
    if not payload.get("success", False):
        raise RuntimeError(f"CKAN action failed: {action} payload={payload!r}")
    return payload


def _download_toronto_csv(
    base: str,
    package_q: str,
    dest_paths: List[Path],
    assume_yes: bool = False,
    overwrite: bool = False,
) -> None:
    root = _repo_root()

    # 1) Find a package
    sr = _ckan_action(base, "package_search", q=package_q, rows=10)
    results = (sr.get("result") or {}).get("results") or []
    if not results:
        raise RuntimeError(f"No CKAN packages matched query: {package_q!r}")

    pkg = results[0]
    pkg_id = pkg.get("id") or pkg.get("name")
    if not pkg_id:
        raise RuntimeError("CKAN package_search result missing id/name")

    # 2) Resolve resources
    show = _ckan_action(base, "package_show", id=pkg_id)
    resources = (show.get("result") or {}).get("resources") or []
    if not resources:
        raise RuntimeError(f"CKAN package had no resources: {pkg_id}")

    # Prefer a zip (traffic signals timing), otherwise any CSV.
    chosen = None
    for r in resources:
        u = (r.get("url") or "").lower()
        fmt = (r.get("format") or "").lower()
        name = (r.get("name") or "").lower()
        if u.endswith(".zip") or fmt == "zip" or "zip" in name:
            chosen = r
            break
    if chosen is None:
        for r in resources:
            u = (r.get("url") or "").lower()
            fmt = (r.get("format") or "").lower()
            if u.endswith(".csv") or fmt == "csv":
                chosen = r
                break

    if chosen is None:
        raise RuntimeError("Could not find a ZIP/CSV resource in the CKAN package.")

    r_url = chosen.get("url")
    if not r_url:
        raise RuntimeError("Chosen CKAN resource missing url")

    # 3) Download (ZIP or CSV) to temp
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        tmp = td_path / "toronto_resource"
        if not _download(r_url, tmp, overwrite=True):
            raise RuntimeError("Toronto download failed")

        final_csv: Optional[Path] = None
        if tmp.suffix.lower() == ".zip":
            with ZipFile(tmp, "r") as z:
                members = [m for m in z.namelist() if m.lower().endswith(".csv")]
                if not members:
                    raise RuntimeError("ZIP did not contain any CSV files.")
                # choose largest CSV inside
                members.sort(key=lambda m: z.getinfo(m).file_size, reverse=True)
                target = members[0]
                z.extract(target, td_path)
                final_csv = td_path / target
        else:
            final_csv = tmp

        assert final_csv is not None

        # 4) Copy into each destination
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
    _maybe_inject_truststore()

    ap = argparse.ArgumentParser(description="Fetch external data needed by HUF-Core example cases.")
    ap.add_argument("--yes", action="store_true", help="Assume 'yes' for any prompts (non-interactive).")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")

    ap.add_argument("--markham", action="store_true", help="Fetch Markham 2018 budget Excel input.")
    ap.add_argument(
        "--markham-url",
        default=os.environ.get(MARKHAM_ENV, ""),
        help=f"Override Markham XLSX URL (or set env var {MARKHAM_ENV}).",
    )

    ap.add_argument("--toronto", action="store_true", help="Fetch Toronto traffic-signal timing/phase status CSV.")
    ap.add_argument(
        "--toronto-ckan",
        default=os.environ.get(TORONTO_ENV, DEFAULT_TORONTO_CKAN_BASE),
        help=f"Toronto CKAN action base (or set env var {TORONTO_ENV}).",
    )
    ap.add_argument(
        "--toronto-package-q",
        default=DEFAULT_TORONTO_PACKAGE_Q,
        help="CKAN package_search query string used to locate the dataset.",
    )

    ap.add_argument("--planck-guide", action="store_true", help="Print Planck manual download instructions.")

    args = ap.parse_args(argv)

    # Normalize to repo root for relative paths.
    os.chdir(_repo_root())

    wanted_any = args.markham or args.toronto or args.planck_guide
    if not wanted_any:
        ap.print_help()
        return 0

    errors: List[str] = []

    if args.planck_guide:
        _print_planck_guide()

    if args.toronto:
        try:
            _download_toronto_csv(
                args.toronto_ckan,
                args.toronto_package_q,
                dest_paths=TORONTO_DESTS,
                assume_yes=args.yes,
                overwrite=args.overwrite,
            )
        except Exception as e:
            errors.append(f"Toronto fetch failed: {e}")

    if args.markham:
        # URL selection: explicit override first, otherwise try default list.
        urls = [args.markham_url] if args.markham_url else []
        urls += DEFAULT_MARKHAM_URLS
        ok = _download_first(urls, _repo_root() / MARKHAM_DEST, overwrite=args.overwrite)
        if not ok:
            errors.append(
                "Markham fetch failed (all candidate URLs returned errors). "
                f"Provide a working URL via --markham-url or env var {MARKHAM_ENV}."
            )
            print(
                "\nManual Markham workaround:\n"
                f"  1) Download the Markham 2018 budget XLSX from Markham Open Data.\n"
                f"  2) Save it to:\n"
                f"     {MARKHAM_DEST.as_posix()}\n"
            )

    if errors:
        print("\nNOTE: data fetch reported errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"\nDone. (Fetched on {_dt.date.today().isoformat()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
