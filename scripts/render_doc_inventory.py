\
r"""scripts/render_doc_inventory.py

Generate a human-readable Docs Inventory page for the MkDocs site.

Source of truth:
- notes/doc_catalog/docs_current.json
- notes/doc_catalog/docs_removed.json

Output:
- docs/docs_inventory.md  (generated; do not hand-edit)

Run (Windows / PowerShell):
  .\.venv\Scripts\python scripts/render_doc_inventory.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _as_paths_current(obj: Any) -> List[str]:
    """
    Accept a few shapes:
    - ["index.md", "vector_db_coherence.md", ...]
    - [{"path":"index.md"}, ...]
    - {"files":[...]} or {"docs":[...]}
    """
    if obj is None:
        return []

    if isinstance(obj, list):
        out: List[str] = []
        for x in obj:
            if isinstance(x, str):
                out.append(x)
            elif isinstance(x, dict) and "path" in x:
                out.append(str(x["path"]))
        return out

    if isinstance(obj, dict):
        for k in ("files", "docs", "current", "paths"):
            v = obj.get(k)
            if isinstance(v, list):
                return _as_paths_current(v)

    return []


def _as_removed(obj: Any) -> List[Dict[str, str]]:
    """
    Accept shapes:
    - []
    - ["old_page.md", ...]
    - [{"path":"old_page.md","reason":"...","removed_at":"..."}]
    - {"removed":[...]}
    """
    if obj is None:
        return []

    if isinstance(obj, list):
        out: List[Dict[str, str]] = []
        for x in obj:
            if isinstance(x, str):
                out.append({"path": x})
            elif isinstance(x, dict) and "path" in x:
                out.append({k: str(v) for k, v in x.items()})
        return out

    if isinstance(obj, dict):
        for k in ("removed", "tombstones", "deleted"):
            v = obj.get(k)
            if isinstance(v, list):
                return _as_removed(v)

    return []


def _first_h1(md_path: Path) -> str:
    """Extract the first Markdown H1 (# ...) line. If none, return filename."""
    try:
        for line in md_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    except Exception:
        pass
    return md_path.name


def _group_key(rel_path: str) -> str:
    parts = rel_path.replace("\\", "/").split("/")
    if len(parts) <= 1:
        return "root"
    return parts[0]


def _nice_group_name(key: str) -> str:
    mapping = {
        "root": "Top-level",
        "partnerships": "Partnerships",
        "cases": "Cases",
    }
    return mapping.get(key, key.replace("_", " ").title())


def render_inventory(root: Path) -> str:
    docs_dir = root / "docs"
    catalog_dir = root / "notes" / "doc_catalog"

    cur_path = catalog_dir / "docs_current.json"
    rem_path = catalog_dir / "docs_removed.json"

    if not cur_path.exists():
        raise FileNotFoundError(f"Missing: {cur_path}. Run scripts/catalog_docs.py first.")

    current_obj = _load_json(cur_path)
    removed_obj: Any = _load_json(rem_path) if rem_path.exists() else []

    current = sorted(set(p.replace("\\", "/").lstrip("./") for p in _as_paths_current(current_obj)))
    removed = _as_removed(removed_obj)

    current = [p for p in current if p.endswith(".md") and not p.split("/")[-1].startswith("_")]

    rows: List[Tuple[str, str, str]] = []
    for rel in current:
        md_path = docs_dir / rel
        title = _first_h1(md_path) if md_path.exists() else Path(rel).name
        group = _nice_group_name(_group_key(rel))
        rows.append((group, title, rel))

    rows.sort(key=lambda t: (t[0].lower(), t[1].lower()))

    lines: List[str] = []
    lines.append("# Docs inventory")
    lines.append("")
    lines.append("This page is **generated** from the doc catalog:")
    lines.append("")
    lines.append("- `notes/doc_catalog/docs_current.json`")
    lines.append("- `notes/doc_catalog/docs_removed.json`")
    lines.append("")
    lines.append("Do not edit this page by hand. Run:")
    lines.append("")
    lines.append("```powershell")
    lines.append(r".\.venv\Scripts\python scripts/docs_hygiene.py")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Current docs: **{len(current)}**")
    lines.append(f"- Removed docs tracked: **{len(removed)}**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Current docs")
    lines.append("")
    lines.append("| Group | Page | Path |")
    lines.append("|---|---|---|")
    for group, title, rel in rows:
        lines.append(f"| {group} | [{title}]({rel}) | `{rel}` |")
    lines.append("")
    lines.append("## Removed docs (tracked)")
    lines.append("")
    if not removed:
        lines.append("_None currently tracked._")
        lines.append("")
    else:
        lines.append("| Path | Notes |")
        lines.append("|---|---|")
        for item in removed:
            path = item.get("path", "")
            notes = " · ".join(
                f"{k}={v}" for k, v in item.items()
                if k != "path" and v and k in ("reason", "removed_at", "replaced_by")
            )
            lines.append(f"| `{path}` | {notes} |")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## What changed?")
    lines.append("")
    lines.append("If you want a visible changelog for stakeholders, keep `docs_removed.json` populated with entries like:")
    lines.append("")
    lines.append("```json")
    lines.append('[{"path":"old_page.md","removed_at":"2026-02-20","reason":"superseded","replaced_by":"new_page.md"}]')
    lines.append("```")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    md = render_inventory(root)
    out_path = root / "docs" / "docs_inventory.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"[ok] wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
