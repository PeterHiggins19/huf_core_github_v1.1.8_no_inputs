\
#!/usr/bin/env python
"""
Apply HUF two-line headers to docs/learning and docs/books markdown files.

Safe behavior:
- Only updates files that do NOT already contain "HUF-DOC:" in the first 120 lines.
- If a file starts with YAML front matter ('---'), inserts header lines as YAML comments directly after the first '---'.
- Otherwise prepends the two-line header to the top of the file.

This is intended for one-time normalization before "make everything live at once".
Do not wire into CI yet.
"""

from __future__ import annotations
import argparse
import re
from pathlib import Path

HUF_DOC_RE = re.compile(r"HUF-DOC:\s*")

def has_header(text: str) -> bool:
    return any("HUF-DOC:" in ln for ln in text.splitlines()[:120])

def insert_header(text: str, line1: str, line2: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        out = [lines[0], f"# {line1}", f"# {line2}"] + lines[1:]
        return "\n".join(out) + ("\n" if not text.endswith("\n") else "")
    return f"{line1}\n{line2}\n\n{text}"

def slugify(path: Path) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", str(path)).strip("_").upper()
    return s[:120]

def make_header(doc_id: str, canon: str, codes: str, huf_version: str, doc_version: str, status: str, lane: str, ro: str) -> tuple[str,str]:
    l1 = f"HUF-DOC: {doc_id} | HUF:{huf_version} | DOC:{doc_version} | STATUS:{status} | LANE:{lane} | RO:{ro}"
    l2 = f"CODES: {codes} | ART: CM, AS, TR, EB | EVID:E0 | POSTURE:OP | WEIGHTS: OP=0.80 TOOL=0.20 PEER=0.00 | CAP: OP_MIN=0.51 TOOL_MAX=0.49 | CANON:{canon}"
    return l1, l2

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="docs", help="Docs root (default: docs)")
    ap.add_argument("--huf", default="1.1.8", help="HUF version")
    ap.add_argument("--doc", default="v0.1.0", help="Document version tag to apply when missing")
    ap.add_argument("--lane", default="release", help="LANE field (release/draft)")
    ap.add_argument("--status", default="draft", help="STATUS field")
    ap.add_argument("--ro", default="Peter Higgins", help="Responsible operator")
    ap.add_argument("--write", action="store_true", help="Write changes (default is dry-run)")
    args = ap.parse_args()

    docs_root = Path(args.root)
    targets = []
    for sub in ["learning", "books"]:
        d = docs_root / sub
        if d.exists():
            targets.extend(sorted(d.rglob("*.md")))

    changed = 0
    for p in targets:
        text = p.read_text(encoding="utf-8", errors="replace")
        if has_header(text):
            continue
        rel = p.as_posix()
        if rel.endswith("docs/" + sub):
            pass
        # Build doc_id based on path
        if "/learning/" in rel:
            if rel.endswith("/index.md") and rel.count("/") == 2:  # docs/learning/index.md
                doc_id = "HUF.REL.LRN.INDEX.LEARNING"
                codes = "LRN, INDEX"
            else:
                doc_id = "HUF.REL.LRN.MODULE." + slugify(p.parent.relative_to(docs_root / "learning"))
                codes = "LRN"
        else:
            if rel.endswith("docs/books/index.md") or rel.endswith("books/index.md"):
                doc_id = "HUF.REL.BOOK.INDEX.BOOKS"
                codes = "BOOK, INDEX"
            else:
                doc_id = "HUF.REL.BOOK.MANUSCRIPT." + slugify(p.parent.relative_to(docs_root / "books"))
                codes = "BOOK"
        canon = "docs/" + rel.split("docs/",1)[-1] if "docs/" in rel else rel
        line1, line2 = make_header(doc_id, canon, codes, args.huf, args.doc, args.status, args.lane, args.ro)
        new_text = insert_header(text, line1, line2)

        if args.write:
            p.write_text(new_text, encoding="utf-8", newline="\n")
        changed += 1

    print(f"Scanned {len(targets)} file(s); would update {changed} file(s).")
    if not args.write:
        print("Dry-run only. Re-run with --write to apply.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
