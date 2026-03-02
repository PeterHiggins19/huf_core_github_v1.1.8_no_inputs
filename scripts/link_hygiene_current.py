\
#!/usr/bin/env python
"""
scripts/link_hygiene_current.py

Policy:
- MkDocs "strict" only validates links to files in docs/. For any link that should point to
  non-doc artifacts (DOCX/XLSX/ZIP/scripts), use a full GitHub URL.
- "Current documents override": if a file exists in notes/current_documents/(staged|inbox),
  that path is treated as authoritative for that basename, even if older revisions exist elsewhere.

What it does (safe, repeatable):
1) Builds an index of "current documents" by basename:
   - Prefer staged over inbox
   - If multiple candidates in the same lane, choose most recent mtime
2) Scans docs/**/*.md and applies these fixes:
   - (docs/...) -> (...) for internal doc links
   - Any relative link to *.docx/*.xlsx/*.zip/*.pdf (or notes/current_documents/...) is rewritten to
     the authoritative file under notes/current_documents using a GitHub blob URL.
   - Rewrites old repo/site names if found.

Dry-run by default. Use --write to apply.

After running:
  python -m mkdocs build --strict
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_GH = "https://github.com/PeterHiggins19/huf_core"
BRANCH = "main"

DOCS_DIR = "docs"
CURRENT_ROOT = Path("notes/current_documents")
LANE_ORDER = ["staged", "inbox"]  # staged overrides inbox

ASSET_EXTS = {".docx", ".xlsx", ".xls", ".zip", ".pdf", ".pptx"}

LINK_RE = re.compile(r'(\[[^\]]*\])\(([^)]+)\)')

def is_external(target: str) -> bool:
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target)) or target.startswith('//')

def normalize_target(target: str) -> str:
    t = target.strip()
    # drop trailing title
    t = re.sub(r'\s+"[^"]*"\s*$', '', t)
    t = re.sub(r"\s+'[^']*'\s*$", '', t)
    return t

def split_target(target: str) -> Tuple[str, str]:
    t = normalize_target(target)
    if "#" in t:
        base, frag = t.split("#", 1)
        return base, "#" + frag
    return t, ""

@dataclass
class CurDoc:
    path: Path
    lane: str
    mtime: float

def build_current_index(repo: Path) -> Dict[str, CurDoc]:
    idx: Dict[str, CurDoc] = {}
    if not (repo / CURRENT_ROOT).exists():
        return idx

    for lane in LANE_ORDER:
        lane_dir = repo / CURRENT_ROOT / lane
        if not lane_dir.exists():
            continue
        for p in lane_dir.rglob("*"):
            if not p.is_file():
                continue
            # include everything — we only rewrite links for ASSET_EXTS and notes/current_documents paths
            key = p.name.lower()
            cur = CurDoc(path=p.relative_to(repo), lane=lane, mtime=p.stat().st_mtime)
            if key not in idx:
                idx[key] = cur
            else:
                # staged always wins; within lane, newest wins
                prev = idx[key]
                if prev.lane != lane:
                    continue  # prev is staged and lane is inbox
                if cur.mtime > prev.mtime:
                    idx[key] = cur
    return idx

def to_github_url(rel_path: Path) -> str:
    return f"{REPO_GH}/blob/{BRANCH}/" + rel_path.as_posix()

def rewrite_md(text: str, idx: Dict[str, CurDoc]) -> Tuple[str, List[str]]:
    changes: List[str] = []

    # 1) internal doc links: (docs/xyz.md) -> (xyz.md)
    def _fix_docs_prefix(m: re.Match) -> str:
        label, target = m.group(1), m.group(2)
        t = normalize_target(target)
        if is_external(t) or t.startswith("mailto:"):
            return m.group(0)
        base, frag = split_target(t)
        if base.startswith("docs/"):
            new = base[len("docs/"):] + frag
            changes.append(f"remove docs/ prefix: {t} -> {new}")
            return f"{label}({new})"
        return m.group(0)

    text2 = LINK_RE.sub(_fix_docs_prefix, text)

    # 2) rewrite links to current docs artifacts
    def _rewrite_assets(m: re.Match) -> str:
        label, target = m.group(1), m.group(2)
        t = normalize_target(target)
        if is_external(t) or t.startswith("mailto:"):
            return m.group(0)
        base, frag = split_target(t)
        # If link points into notes/current_documents (relative), use GitHub URL
        if base.startswith("notes/current_documents/"):
            new = to_github_url(Path(base)) + frag
            changes.append(f"notes/current_documents -> github: {t} -> {new}")
            return f"{label}({new})"
        # If link points to a doc asset (docx/xlsx/zip/pdf), resolve by basename in current index
        ext = Path(base).suffix.lower()
        if ext in ASSET_EXTS:
            key = Path(base).name.lower()
            if key in idx:
                rel = idx[key].path
                new = to_github_url(rel) + frag
                changes.append(f"asset -> current ({idx[key].lane}): {t} -> {new}")
                return f"{label}({new})"
        return m.group(0)

    text3 = LINK_RE.sub(_rewrite_assets, text2)

    # 3) rewrite old repo/site names (safe global replacements)
    replacements = [
        ("huf_core_github_v1.1.8_no_inputs", "huf_core"),
        ("peterhiggins19.github.io/huf_core_github_v1.1.8_no_inputs", "peterhiggins19.github.io/huf_core"),
        ("PeterHIggins19", "PeterHiggins19"),
    ]
    out = text3
    for old, new in replacements:
        if old in out:
            out = out.replace(old, new)
            changes.append(f"replace: {old} -> {new}")

    return out, changes

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="Repo root")
    ap.add_argument("--write", action="store_true", help="Write changes (default dry-run)")
    ap.add_argument("--report", default="notes/_org/link_hygiene_report.md", help="Where to write a report")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    docs_dir = repo / DOCS_DIR
    if not docs_dir.exists():
        raise SystemExit(f"docs dir not found: {docs_dir}")

    idx = build_current_index(repo)

    report_lines = []
    changed_files = 0
    for md in sorted(docs_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        new, changes = rewrite_md(text, idx)
        if changes:
            changed_files += 1
            report_lines.append(f"## {md.relative_to(repo).as_posix()}")
            for c in changes:
                report_lines.append(f"- {c}")
            report_lines.append("")
            if args.write:
                md.write_text(new, encoding="utf-8", newline="\n")

    report = "\n".join(report_lines).strip() + "\n"
    print(f"[link_hygiene] current_docs_index={len(idx)} basenames")
    print(f"[link_hygiene] files_changed={changed_files}")
    if args.write:
        out = repo / args.report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8", newline="\n")
        print(f"[link_hygiene] wrote report: {out.as_posix()}")
    else:
        print("[link_hygiene] dry-run; re-run with --write to apply and emit report")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
