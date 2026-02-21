\
r"""scripts/ensure_nav_entries.py

MkDocs nav auto-fix (text-based, Material-safe).

Why:
- MkDocs Material config can contain python YAML tags (emoji_index, etc.) that
  break yaml.safe_load(). This script edits mkdocs.yml as plain text instead.
- Prevents "pages exist but are not included in nav" warnings by ensuring
  required sidebar entries exist.

Inputs:
- mkdocs.yml (in repo root)
- notes/doc_catalog/nav_required.json (sections + leaf entries to enforce)

Run (PowerShell, repo venv):
  .\.venv\Scripts\python scripts/ensure_nav_entries.py

What it does:
- Ensures required leaf entries exist under the named nav sections.
- Creates the section if missing (appends to nav).
- Does NOT reorder existing nav; only inserts missing lines.

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
    """
    Return (start_index, end_index) of nav block in mkdocs.yml.
    start points to the line 'nav:'.
    end points to the first line AFTER nav block.
    """
    nav_start = None
    for i, line in enumerate(lines):
        if re.match(r"^nav:\s*$", line):
            nav_start = i
            break
    if nav_start is None:
        return (-1, -1)

    # nav continues until next top-level key (column 0, looks like 'theme:' or 'plugins:')
    nav_end = len(lines)
    for j in range(nav_start + 1, len(lines)):
        line = lines[j]
        if re.match(r"^[A-Za-z0-9_][A-Za-z0-9_\-]*\s*:\s*$", line) and not line.startswith(" "):
            nav_end = j
            break
    return (nav_start, nav_end)


def ensure_section(lines: List[str], nav_start: int, nav_end: int, section: str) -> Tuple[List[str], int]:
    """
    Ensure a section like '  - Partnerships:' exists inside nav.
    Returns (new_lines, section_header_index).
    """
    pat = re.compile(rf"^\s*-\s*{re.escape(section)}:\s*$")
    for i in range(nav_start + 1, nav_end):
        if pat.match(lines[i]):
            return (lines, i)

    # Not found: append section at end of nav (just before nav_end)
    insert_at = nav_end
    new = lines[:insert_at] + [f"  - {section}:"] + lines[insert_at:]
    return (new, insert_at)


def ensure_leafs_under_section(lines: List[str], section_header_index: int, leafs: List[dict]) -> List[str]:
    """
    Ensure leaf lines exist under a section header.

    We insert missing leaf lines immediately after the section header.
    Leaf indentation uses 6 spaces: '      - Title: path.md'
    """
    # Compute the section block end: next sibling at indent 2 ("  - Something:")
    block_end = len(lines)
    for j in range(section_header_index + 1, len(lines)):
        if re.match(r"^\s{2}-\s+", lines[j]):  # next top-level nav item
            block_end = j
            break

    block_text = "\n".join(lines[section_header_index + 1:block_end])
    to_insert = []
    for item in leafs:
        path = item["path"].replace("\\", "/").lstrip("./")
        if path not in block_text:
            title = item["title"]
            to_insert.append(f"      - {title}: {path}")

    if not to_insert:
        return lines

    return lines[: section_header_index + 1] + to_insert + lines[section_header_index + 1:]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    mk = root / "mkdocs.yml"
    lines = mk.read_text(encoding="utf-8").splitlines()

    nav_start, nav_end = find_nav_block(lines)
    if nav_start < 0:
        print("[err] mkdocs.yml has no nav: block")
        return 2

    required = read_required(root)

    # We may change line count; recompute nav_end each time we insert.
    for section, leafs in required.items():
        nav_start, nav_end = find_nav_block(lines)
        lines, section_idx = ensure_section(lines, nav_start, nav_end, section)
        lines = ensure_leafs_under_section(lines, section_idx, leafs)

    mk.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("[ok] mkdocs.yml nav updated (missing entries inserted).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
