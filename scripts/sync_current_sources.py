\
#!/usr/bin/env python
"""
scripts/sync_current_sources.py

Purpose:
- Enforce the policy: files under notes/current_documents/ supersede older variants.
- Make that visible on the public site by:
  1) Injecting a "Current source-of-truth" callout at the top of designated docs pages.
  2) Updating docs/books/index.md wording to avoid hardcoded version claims and to point at current sources.

Inputs:
- notes/_org/current_sources.json

Behavior:
- Dry-run by default; use --write to apply.
- Uses GitHub blob URLs for sources (since MkDocs cannot link to non-doc assets in strict mode).

Run:
  .\.venv\Scripts\python scripts\sync_current_sources.py
  .\.venv\Scripts\python scripts\sync_current_sources.py --write
Then:
  .\.venv\Scripts\python -m mkdocs build --strict
  .\.venv\Scripts\python -m mkdocs gh-deploy --force
"""

from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

REPO_GH = "https://github.com/PeterHiggins19/huf_core"
BRANCH = "main"

CALLOUT_START = "<!-- HUF_CURRENT_SOURCE_START -->"
CALLOUT_END   = "<!-- HUF_CURRENT_SOURCE_END -->"

def gh_url(rel_path: str) -> str:
    rel_path = rel_path.replace("\\", "/").lstrip("/")
    return f"{REPO_GH}/blob/{BRANCH}/{rel_path}"

def load_sources(repo: Path) -> dict:
    p = repo / "notes/_org/current_sources.json"
    return json.loads(p.read_text(encoding="utf-8"))

def inject_callout(md_path: Path, title: str, source_rel: str) -> tuple[str, bool]:
    text = md_path.read_text(encoding="utf-8", errors="replace")
    url = gh_url(source_rel)

    callout = "\n".join([
        CALLOUT_START,
        f"!!! note \"Current source-of-truth\"",
        f"    The authoritative working copy for **{title}** is maintained under `notes/current_documents/staged/` and supersedes older variants.",
        f"    ",
        f"    - Source (DOCX): {url}",
        f"    ",
        f"    This page is the public Markdown edition used for the documentation site.",
        CALLOUT_END,
        ""
    ])

    if CALLOUT_START in text and CALLOUT_END in text:
        new = re.sub(
            re.escape(CALLOUT_START) + r".*?" + re.escape(CALLOUT_END) + r"\s*",
            callout,
            text,
            flags=re.DOTALL
        )
        return new, (new != text)

    # Insert after YAML front matter if present, else after HUF header if present, else top.
    lines = text.splitlines()
    insert_at = 0
    if lines and lines[0].strip() == "---":
        # find end of front matter
        for i in range(1, min(len(lines), 200)):
            if lines[i].strip() == "---":
                insert_at = i + 1
                break
    else:
        # HUF header (two-line)
        for i in range(0, min(len(lines), 20)):
            if "HUF-DOC:" in lines[i]:
                # insert after second header line (or next blank)
                insert_at = min(i + 2, len(lines))
                break

    new_lines = lines[:insert_at] + ["", callout.rstrip()] + [""] + lines[insert_at:]
    new = "\n".join(new_lines).strip() + "\n"
    return new, True

def update_books_index(repo: Path, sources: dict) -> tuple[str,bool]:
    p = repo / "docs/books/index.md"
    if not p.exists():
        return "", False
    text = p.read_text(encoding="utf-8", errors="replace")

    # Replace any hardcoded "(vX.Y.Z)" in quick-pick rows to avoid stale claims.
    text2 = re.sub(r"\(v\d+\.\d+\.\d+\)", "(current)", text)

    # Ensure handbook/reference rows exist and point to pages (keeps internal nav stable)
    # Add a small "Current sources" table near the top if not present.
    marker = "## Current sources (authoritative working copies)"
    if marker not in text2:
        handbook_url = gh_url(sources["handbook"]["source"])
        ref_url = gh_url(sources["reference"]["source"])
        insert = "\n".join([
            "",
            marker,
            "",
            "These links point to the authoritative working copies under `notes/current_documents/staged/`.",
            "",
            "| Book | Current source |",
            "|---|---|",
            f"| HUF Handbook | {handbook_url} |",
            f"| HUF Reference | {ref_url} |",
            "",
        ])

        # Insert after the first horizontal rule or after the intro block.
        parts = text2.split("\n---\n", 1)
        if len(parts) == 2:
            text2 = parts[0] + "\n---\n" + insert + parts[1]
        else:
            text2 = insert + text2

    return text2, (text2 != text)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="Repo root")
    ap.add_argument("--write", action="store_true", help="Write changes (default dry-run)")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    sources = load_sources(repo)

    changed = 0

    # 1) Inject callouts into target pages
    for key, spec in sources.items():
        md = repo / spec["page"]
        if not md.exists():
            print(f"[skip] missing page: {spec['page']}")
            continue
        new, did = inject_callout(md, spec["title"], spec["source"])
        if did:
            changed += 1
            print(f"[update] {spec['page']} (callout)")
            if args.write:
                md.write_text(new, encoding="utf-8", newline="\n")

    # 2) Update books index
    new_books, did_books = update_books_index(repo, sources)
    if did_books:
        changed += 1
        print("[update] docs/books/index.md (current sources + remove hardcoded versions)")
        if args.write:
            (repo/"docs/books/index.md").write_text(new_books, encoding="utf-8", newline="\n")

    print(f"[done] changes={changed} (write={'yes' if args.write else 'no'})")
    if not args.write:
        print("Dry-run only. Re-run with --write to apply.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
