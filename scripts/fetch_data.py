from __future__ import annotations

"""scripts/fetch_data.py

Small helper to download public input datasets used by HUF demo cases.

Targets (as of 2026-02-17):
- Markham budget XLSX (used in cases/municipal_budget)
- Toronto traffic signals phase-status CSV (used in traffic_phase / traffic_anomaly)
- Planck 70GHz guide (manual download instructions)

Notes:
- The Toronto Open Data portal is CKAN-backed, but the stable Action API base is:
    https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action
  You can override it via:
    * --toronto-ckan <URL>
    * env var HUF_TORONTO_CKAN=<URL>
"""

import argparse
import csv
import datetime as _dt
import json
import os
import shutil
import sys
import tempfile
import textwrap
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Optional: use OS trust store on Windows/macOS if installed.
try:
    import truststore  # type: ignore

    truststore.inject_into_ssl()
except Exception:
    truststore = None  # noqa: F841


# ----------------------------- Repo paths -----------------------------

REPO_MARKERS = (".git", "pyproject.toml", "setup.cfg", "cases")


def _repo_root(start: Optional[Path] = None) -> Path:
    """Best-effort repo root discovery.

    We walk upward from this script (or provided path) until we find a marker.
    This makes the script work both inside a git checkout and in unpacked snapshots.
    """
    here = (start or Path(__file__)).resolve()
    for p in [here.parent] + list(here.parents):
        for m in REPO_MARKERS:
            if (p / m).exists():
                return p
    # Fallback: scripts/.. (common layout)
    return here.parent.parent


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


# ----------------------------- Defaults -----------------------------

DEFAULT_MARKHAM_XLSX_URL = (
    "https://www.markham.ca/wps/wcm/connect/markham/8e2d0d17-6a80-4c7d-bb7c-4d7f6dc7f4b8/2018+Budget.xlsx"
)

# Toronto CKAN Action API base
DEFAULT_TORONTO_CKAN_BASE = os.environ.get(
    "HUF_TORONTO_CKAN", "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action"
)

# Known stable IDs (used as defaults; the script will fall back to search if they stop working)
DEFAULT_TORONTO_PACKAGE_ID = "7dda2235-999e-4a17-b228-abd0961e045d"
DEFAULT_TORONTO_RESOURCE_ID = "02c90a3a-d754-4023-a283-ed5687e87f1f"

# Search fallback (only used if the known IDs don't work and the user didn't provide ids)
DEFAULT_TORONTO_QUERY = "traffic signals timing"

# Destinations in-repo
MARKHAM_DEST = Path("cases/municipal_budget/inputs/markham_2018_budget.xlsx")

TORONTO_DEST = Path("cases/traffic_phase/inputs/toronto_traffic_signals_phase_status.csv")
TORONTO_DEST_2 = Path("cases/traffic_anomaly/inputs/toronto_traffic_signals_phase_status.csv")

PLANCK_DEST = Path("cases/planck/inputs/planck_pr3_70ghz_nside2048.fits")

IRSA_PLANCK70_FITS_URL = (
    "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/"
    "LFI_SkyMap_070_2048_R3.01_full.fits"
)
IRSA_PLANCK_PR3_ALLSKY_URL = "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/"
ESA_PLA_URL = "https://pla.esac.esa.int/"


# ----------------------------- HTTP helpers -----------------------------

def _normalize_ckan_base(base: str) -> str:
    base = (base or "").strip().rstrip("/")
    if not base:
        return DEFAULT_TORONTO_CKAN_BASE

    # If already includes /api/3/action anywhere, keep up to that segment.
    needle = "/api/3/action"
    if needle in base:
        return base[: base.index(needle) + len(needle)]

    if base.endswith("/api/3/action"):
        return base
    if base.endswith("/api/3"):
        return base + "/action"
    if base.endswith("/api"):
        return base + "/3/action"

    # If someone passes a host like https://ckan0... , add the standard suffix.
    return base + "/api/3/action"


def _urlopen(req: Request, timeout: int) -> Any:
    return urlopen(req, timeout=timeout)


def _http_get_json(url: str, timeout: int = 30) -> Dict[str, Any]:
    req = Request(
        url,
        headers={
            "User-Agent": "huf-fetch-data/1.1 (+https://github.com/)",
            "Accept": "application/json",
        },
    )
    try:
        with _urlopen(req, timeout=timeout) as r:
            raw = r.read()
    except HTTPError as e:
        # Include URL to make debugging CKAN base issues obvious.
        raise HTTPError(e.url, e.code, f"{e.msg} (while fetching {url})", e.hdrs, e.fp) from e
    except URLError as e:
        raise RuntimeError(f"Network error while fetching {url}: {e}") from e

    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        snippet = raw[:200]
        raise RuntimeError(f"Invalid JSON from {url}. First bytes: {snippet!r}") from e


def _ckan_action(base: str, action: str, **params: Any) -> Dict[str, Any]:
    base = _normalize_ckan_base(base)
    qs = urlencode({k: v for k, v in params.items() if v is not None}, doseq=True)
    url = f"{base}/{action}"
    if qs:
        url += f"?{qs}"
    payload = _http_get_json(url)
    if not payload.get("success", False):
        err = payload.get("error") or payload
        raise RuntimeError(f"CKAN action failed: {action}: {err}")
    return payload


# ----------------------------- Download helpers -----------------------------

def _download(url: str, dest: Path, overwrite: bool = False) -> None:
    dest = Path(dest)
    if dest.exists() and not overwrite:
        print(f"[skip] {dest} already exists")
        return

    _ensure_parent(dest)
    print(f"[get] {url}")

    req = Request(url, headers={"User-Agent": "huf-fetch-data/1.1"})
    with _urlopen(req, timeout=60) as r, tempfile.NamedTemporaryFile(delete=False) as tf:
        shutil.copyfileobj(r, tf)
        tmp = Path(tf.name)

    dest_tmp = dest.with_suffix(dest.suffix + ".tmp")
    try:
        shutil.move(str(tmp), str(dest_tmp))
        shutil.move(str(dest_tmp), str(dest))
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass
        try:
            if dest_tmp.exists():
                dest_tmp.unlink()
        except Exception:
            pass

    print(f"[ok ] wrote {dest}")


def _pick_best_csv_from_zip(z: zipfile.ZipFile) -> str:
    """Heuristic: prefer filenames that look like phase-status, otherwise largest CSV."""
    csv_names = [n for n in z.namelist() if n.lower().endswith(".csv")]
    if not csv_names:
        raise RuntimeError("Zip contains no CSV files.")

    def score(name: str) -> Tuple[int, int]:
        ln = name.lower()
        s = 0
        for token in ("phase", "status", "signal", "timing"):
            if token in ln:
                s += 1
        try:
            size = z.getinfo(name).file_size
        except Exception:
            size = 0
        return (s, size)

    csv_names.sort(key=score, reverse=True)
    return csv_names[0]


def _validate_toronto_schema(csv_path: Path) -> None:
    required = {"TCS", "PHASE"}
    optional = {"PHASE_STATUS_TEXT", "PHASE_CALL_TEXT"}

    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = {c.strip() for c in (reader.fieldnames or []) if c}

    missing = required - cols
    if missing:
        raise RuntimeError(
            "Toronto CSV missing required columns: "
            + ", ".join(sorted(missing))
            + f". Found: {', '.join(sorted(cols))}"
        )

    print("\nToronto schema expected by HUF traffic adapters:")
    print("  required columns: TCS, PHASE")
    if cols & optional:
        print("  optional columns: " + ", ".join(sorted(cols & optional)))
    else:
        print("  optional columns: PHASE_STATUS_TEXT, PHASE_CALL_TEXT")
    print()


def _download_toronto_csv(
    ckan_base: str,
    dests: Sequence[Path],
    *,
    query: str,
    package_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    assume_yes: bool = False,
    overwrite: bool = False,
) -> None:
    base = _normalize_ckan_base(ckan_base)

    # If user didn't provide ids, use known stable defaults.
    if package_id is None:
        package_id = DEFAULT_TORONTO_PACKAGE_ID
    if resource_id is None:
        resource_id = DEFAULT_TORONTO_RESOURCE_ID

    download_url: Optional[str] = None

    # 1) Try direct resource_show first (fast + stable).
    if resource_id:
        try:
            rs = _ckan_action(base, "resource_show", id=resource_id)
            download_url = rs["result"].get("url") or rs["result"].get("download_url")
        except Exception as e:
            print(f"[warn] resource_show failed for {resource_id}: {e}")

    # 2) If that failed, try package_show and pick a resource.
    if download_url is None and package_id:
        try:
            pkg = _ckan_action(base, "package_show", id=package_id)["result"]
            resources = pkg.get("resources") or []
            # Prefer resources that look like the timing zip / phase status.
            best = None
            best_score = -1
            for r in resources:
                name = (r.get("name") or "") + " " + (r.get("description") or "")
                url = (r.get("url") or "")
                ln = (name + " " + url).lower()
                s = 0
                for token in ("timing", "traffic", "signal", "phase", "status", ".zip", "csv"):
                    if token in ln:
                        s += 1
                if s > best_score:
                    best_score = s
                    best = r
            if best:
                download_url = best.get("url") or best.get("download_url")
        except Exception as e:
            print(f"[warn] package_show failed for {package_id}: {e}")

    # 3) If still no URL, fall back to search.
    if download_url is None:
        # Try a couple of queries if needed.
        queries = [query, "traffic-signals-timing", "traffic signal phase status"]
        pkg_candidates: List[Dict[str, Any]] = []
        for q in queries:
            try:
                sr = _ckan_action(base, "package_search", q=q, rows=10)["result"]
                pkg_candidates = sr.get("results") or []
                if pkg_candidates:
                    break
            except Exception as e:
                print(f"[warn] package_search failed for q={q!r}: {e}")

        if not pkg_candidates:
            raise RuntimeError(
                "Could not find Toronto dataset via CKAN search. "
                f"Check --toronto-ckan (currently {base!r})."
            )

        # Pick package.
        pkg = pkg_candidates[0]
        if not assume_yes and len(pkg_candidates) > 1:
            print("Toronto CKAN search results:")
            for i, p in enumerate(pkg_candidates[:5], start=1):
                print(f"  {i}. {p.get('title') or p.get('name')} ({p.get('name')})")
            try:
                choice = input("Pick a dataset [1]: ").strip() or "1"
                idx = max(1, min(int(choice), len(pkg_candidates))) - 1
                pkg = pkg_candidates[idx]
            except Exception:
                pkg = pkg_candidates[0]

        pkg = _ckan_action(base, "package_show", id=pkg.get("name") or pkg.get("id"))["result"]
        resources = pkg.get("resources") or []
        if not resources:
            raise RuntimeError("Selected Toronto package has no resources.")

        # Prefer zip resources then csv.
        def r_score(r: Dict[str, Any]) -> Tuple[int, int]:
            url = (r.get("url") or "").lower()
            name = ((r.get("name") or "") + " " + (r.get("description") or "")).lower()
            s = 0
            for token in ("timing", "traffic", "signal", "phase", "status"):
                if token in name or token in url:
                    s += 1
            ext_bonus = 2 if url.endswith(".zip") else (1 if url.endswith(".csv") else 0)
            return (s + ext_bonus, 0)

        resources.sort(key=r_score, reverse=True)
        chosen = resources[0]
        if not assume_yes and len(resources) > 1:
            print("\nResources:")
            for i, r in enumerate(resources[:10], start=1):
                fmt = (r.get("format") or "").strip()
                print(f"  {i}. {r.get('name') or r.get('id')} [{fmt}]\n     {r.get('url')}")
            try:
                choice = input("Pick a resource [1]: ").strip() or "1"
                idx = max(1, min(int(choice), len(resources))) - 1
                chosen = resources[idx]
            except Exception:
                chosen = resources[0]

        download_url = chosen.get("url") or chosen.get("download_url")

    if not download_url:
        raise RuntimeError("Could not determine a download URL for Toronto resource.")

    # Download (usually a .zip) to temp, then extract best CSV.
    with tempfile.TemporaryDirectory() as td:
        tmp_dir = Path(td)
        tmp_file = tmp_dir / "toronto_download"
        _download(download_url, tmp_file, overwrite=True)

        csv_src: Optional[Path] = None
        if zipfile.is_zipfile(tmp_file):
            with zipfile.ZipFile(tmp_file, "r") as z:
                best_csv = _pick_best_csv_from_zip(z)
                csv_src = tmp_dir / Path(best_csv).name
                with z.open(best_csv, "r") as rf, csv_src.open("wb") as wf:
                    shutil.copyfileobj(rf, wf)
        else:
            # If it's already CSV, keep it.
            csv_src = tmp_file

        assert csv_src is not None and csv_src.exists()

        _validate_toronto_schema(csv_src)

        for dest in dests:
            dest = Path(dest)
            if dest.exists() and not overwrite:
                print(f"[skip] {dest} already exists")
                continue
            _ensure_parent(dest)
            shutil.copyfile(csv_src, dest)
            print(f"[ok ] wrote {dest}")


# ----------------------------- Planck guide -----------------------------

def _print_planck_guide() -> None:
    msg = f"""\
    Planck 70GHz PR3 file is too large / unstable for automated download in some environments.

    Option A (IRSA mirror direct link):
      1) Download:
         {IRSA_PLANCK70_FITS_URL}
      2) Save it to:
         {PLANCK_DEST.as_posix()}

       Example (PowerShell):
         curl.exe -L -o "{PLANCK_DEST.as_posix()}" "{IRSA_PLANCK70_FITS_URL}"

      IRSA PR3 all-sky maps landing page:
         {IRSA_PLANCK_PR3_ALLSKY_URL}

    Option B (ESA Planck Legacy Archive):
      1) Visit:
         {ESA_PLA_URL}
      2) Browse/select PR3 products in the Maps section.

    After placing the FITS, run:
      pip install -e ".[planck]"
      huf planck --fits "{PLANCK_DEST.as_posix()}" --out out/planck70 --retained-target 0.97 --nside-out 64
    """
    print(textwrap.dedent(msg).strip() + "\n")


# ----------------------------- CLI -----------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fetch_data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            Fetch public input datasets for HUF cases.

            By default, this script writes into the repo's cases/*/inputs/ folders.
            """
        ),
    )

    parser.add_argument("--markham", action="store_true", help="Download Markham 2018 budget XLSX.")
    parser.add_argument("--toronto", action="store_true", help="Download Toronto traffic signal phase-status CSV.")
    parser.add_argument("--planck-guide", action="store_true", help="Print guided/manual download steps for Planck.")

    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    parser.add_argument("--yes", action="store_true", help="Non-interactive: pick first/best options.")

    # Markham
    parser.add_argument("--markham-url", default=DEFAULT_MARKHAM_XLSX_URL, help="Override Markham XLSX URL.")

    # Toronto
    parser.add_argument(
        "--toronto-ckan",
        default=DEFAULT_TORONTO_CKAN_BASE,
        help="Toronto CKAN Action API base URL (or set env var HUF_TORONTO_CKAN).",
    )
    parser.add_argument("--toronto-query", default=DEFAULT_TORONTO_QUERY, help="Search query for the Toronto dataset.")
    parser.add_argument(
        "--toronto-package",
        default=DEFAULT_TORONTO_PACKAGE_ID,
        help="Toronto CKAN package id/name (default is a known stable dataset id).",
    )
    parser.add_argument(
        "--toronto-resource",
        default=DEFAULT_TORONTO_RESOURCE_ID,
        help="Toronto CKAN resource id (default is a known stable resource id).",
    )

    args = parser.parse_args(argv)

    if not (args.markham or args.toronto or args.planck_guide):
        parser.print_help()
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

    if args.markham or args.toronto:
        today = _dt.date.today().isoformat()
        print(f"\nDone. (Fetched on {today})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
