\
"""scripts/catalog_docs.py

Docs hygiene tool (MkDocs + Material).

What it does:
1) Scans docs/ for Markdown files.
2) Parses mkdocs.yml nav to find which docs are linked in the sidebar.
3) Writes a persistent catalog under notes/doc_catalog/:
   - docs_current.json      (all docs currently present)
   - docs_removed.json      (docs that used to exist, but are now missing)
   - nav_files.json         (docs referenced by nav)
   - orphans.json           (docs present but not in nav)
   - missing_in_docs.json   (docs referenced by nav but missing from docs/)

Rule the user requested:
- If a doc reappears, remove it from docs_removed.json.

Run (Windows-safe):
  .\.venv\Scripts\python scripts/catalog_docs.py

Optional:
  .\.venv\Scripts\python scripts/catalog_docs.py --print-suggested-nav

Notes:
- This does NOT auto-edit your nav; it prints suggested YAML lines.
- Files starting with "_" are treated as internal snippets and ignored for "orphan" warnings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml


def sha256_text(path: Path) -> str:
    txt = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def first_h1(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except Exception:
        pass
    return ""


def scan_docs(docs_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Return mapping relpath -> metadata for all *.md under docs/."""
    items: Dict[str, Dict[str, Any]] = {}
    for p in sorted(docs_dir.rglob("*.md")):
        if not p.is_file():
            continue
        rel = p.relative_to(docs_dir).as_posix()
        items[rel] = {
            "path": rel,
            "title": first_h1(p),
            "sha256": sha256_text(p),
        }
    return items


def walk_nav(node: Any, out: Set[str]) -> None:
    """Collect file paths referenced by MkDocs nav."""
    if node is None:
        return
    if isinstance(node, str):
        # ignore external links
        if "://" in node:
            return
        out.add(node.replace("\\", "/").lstrip("./"))
        return
    if isinstance(node, list):
        for x in node:
            walk_nav(x, out)
        return
    if isinstance(node, dict):
        for _, v in node.items():
            walk_nav(v, out)
        return


def parse_nav(mkdocs_yml: Path) -> Set[str]:
    data = yaml.safe_load(mkdocs_yml.read_text(encoding="utf-8"))
    nav = data.get("nav", [])
    out: Set[str] = set()
    walk_nav(nav, out)
    # keep only .md files (ignore directories and other assets)
    return {p for p in out if p.endswith(".md")}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--print-suggested-nav", action="store_true",
                    help="Print suggested YAML leaf lines for orphans (grouped by folder).")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    docs_dir = root / "docs"
    mkdocs_yml = root / "mkdocs.yml"
    catalog_dir = root / "notes" / "doc_catalog"
    catalog_dir.mkdir(parents=True, exist_ok=True)

    current = scan_docs(docs_dir)
    current_set = set(current.keys())

    nav_files = parse_nav(mkdocs_yml)
    nav_set = set(nav_files)

    # Ignore internal snippets from orphan reporting
    def is_ignored(rel: str) -> bool:
        name = Path(rel).name
        return name.startswith("_")

    orphans = sorted([p for p in current_set - nav_set if not is_ignored(p)])
    missing_in_docs = sorted([p for p in nav_set - current_set])

    # Persistent removed list management
    prev_current = load_json(catalog_dir / "docs_current.json", {})
    prev_removed = set(load_json(catalog_dir / "docs_removed.json", []))

    # Anything that used to exist but is now gone → removed
    for p in prev_current.keys():
        if p not in current_set:
            prev_removed.add(p)

    # Anything that reappeared → remove from removed
    for p in list(prev_removed):
        if p in current_set:
            prev_removed.remove(p)

    # Write catalogs
    save_json(catalog_dir / "docs_current.json", current)
    save_json(catalog_dir / "docs_removed.json", sorted(prev_removed))
    save_json(catalog_dir / "nav_files.json", sorted(nav_set))
    save_json(catalog_dir / "orphans.json", orphans)
    save_json(catalog_dir / "missing_in_docs.json", missing_in_docs)

    print(f"[root] {root}")
    print(f"[docs] {len(current_set)} markdown files under docs/")
    print(f"[nav ] {len(nav_set)} markdown files referenced by mkdocs.yml nav")
    print(f"[orphans] {len(orphans)} docs present but not in nav (excluding '_' snippets)")
    print(f"[missing] {len(missing_in_docs)} docs referenced by nav but missing on disk")
    print(f"[removed] {len(prev_removed)} docs tracked as removed")

    if orphans:
        print("\nOrphans (present in docs/, not in nav):")
        for p in orphans[:50]:
            print(f"  - {p}")
        if len(orphans) > 50:
            print("  ...")

    if missing_in_docs:
        print("\nMissing-in-docs (in nav, missing from docs/):")
        for p in missing_in_docs:
            print(f"  - {p}")

    if args.print_suggested_nav and orphans:
        print("\nSuggested nav leaf lines (paste where appropriate):")
        for p in orphans:
            title = current.get(p, {}).get("title") or Path(p).stem.replace("_", " ").title()
            print(f"      - {title}: {p}")

    # return nonzero if nav references missing docs (strict would fail)
    return 2 if missing_in_docs else 0


if __name__ == "__main__":
    raise SystemExit(main())
