\
r"""scripts/ensure_nav_entries.py

MkDocs nav auto-fix (text-based, Material-safe) with ordering normalization.

Why:
- MkDocs Material config can contain python YAML tags (emoji_index, etc.) that
  break yaml.safe_load(). This script edits mkdocs.yml as plain text instead.
- Prevents "pages exist but are not included in nav" warnings by ensuring
  required sidebar entries exist.
- Normalizes the ORDER of required leaf entries so the sidebar looks intentional.

Inputs:
- mkdocs.yml (in repo root)
- notes/doc_catalog/nav_required.json (sections + leaf entries to enforce)

Run (PowerShell, repo venv):
  .\.venv\Scripts\python scripts/ensure_nav_entries.py

What it does:
- Ensures required sections exist.
- Removes any existing occurrences of required leaf entries.
- Inserts required leaf entries in the exact order specified in nav_required.json.
- Does NOT reorder unrelated nav items.

Exit codes:
- 0: ok
- 2: mkdocs.yml missing nav: block
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


def read_required(root: Path) -> Dict[str, List[dict]]:
    p = root / "notes" / "doc_catalog" / "nav_required.json"
    return json.loads(p.read_text(encoding="utf-8"))


def find_nav_block(lines: List[str]) -> Tuple[int, int]:
    """Return (start_index, end_index) of nav block in mkdocs.yml."""
    nav_start = None
    for i, line in enumerate(lines):
        if re.match(r"^nav:\s*$", line):
            nav_start = i
            break
    if nav_start is None:
        return (-1, -1)

    nav_end = len(lines)
    for j in range(nav_start + 1, len(lines)):
        line = lines[j]
        if re.match(r"^[A-Za-z0-9_][A-Za-z0-9_\-]*\s*:\s*$", line) and not line.startswith(" "):
            nav_end = j
            break
    return (nav_start, nav_end)


def ensure_section(lines: List[str], nav_start: int, nav_end: int, section: str) -> Tuple[List[str], int]:
    """Ensure a section like '  - Partnerships:' exists inside nav."""
    pat = re.compile(rf"^\s*-\s*{re.escape(section)}:\s*$")
    for i in range(nav_start + 1, nav_end):
        if pat.match(lines[i]):
            return (lines, i)

    insert_at = nav_end
    new = lines[:insert_at] + [f"  - {section}:"] + lines[insert_at:]
    return (new, insert_at)


def _section_block_end(lines: List[str], section_header_index: int) -> int:
    block_end = len(lines)
    for j in range(section_header_index + 1, len(lines)):
        if re.match(r"^\s{2}-\s+", lines[j]):  # next top-level nav item
            block_end = j
            break
    return block_end


def normalize_required_leafs(lines: List[str], section_header_index: int, leafs: List[dict]) -> List[str]:
    """
    Remove existing occurrences of required leafs (by path match) and re-insert in required order
    immediately after the section header.
    """
    block_end = _section_block_end(lines, section_header_index)

    req_paths = [item["path"].replace("\\", "/").lstrip("./") for item in leafs]
    req_set = set(req_paths)

    header = lines[: section_header_index + 1]
    body = lines[section_header_index + 1:block_end]
    tail = lines[block_end:]

    kept_body = []
    for line in body:
        norm = line.replace("\\", "/")
        if any(p in norm for p in req_set):
            continue
        kept_body.append(line)

    insert = [f"      - {item['title']}: {path}" for item, path in zip(leafs, req_paths)]
    return header + insert + kept_body + tail


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    mk = root / "mkdocs.yml"
    lines = mk.read_text(encoding="utf-8").splitlines()

    nav_start, nav_end = find_nav_block(lines)
    if nav_start < 0:
        print("[err] mkdocs.yml has no nav: block")
        return 2

    required = read_required(root)

    for section, leafs in required.items():
        nav_start, nav_end = find_nav_block(lines)
        lines, section_idx = ensure_section(lines, nav_start, nav_end, section)
        lines = normalize_required_leafs(lines, section_idx, leafs)

    mk.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("[ok] mkdocs.yml nav updated (required entries normalized).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
