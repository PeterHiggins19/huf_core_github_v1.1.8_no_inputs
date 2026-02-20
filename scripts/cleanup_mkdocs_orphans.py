"""scripts/cleanup_mkdocs_orphans.py

Removes common MkDocs "orphan page" noise without deleting data:

- Moves docs/vector_db_coherence_one_pager.patch.md into notes/orphaned_docs/
- Reconciles accidental nested folder docs/docs/**

Rules for nested docs/docs/**:
- If docs/<file> exists and content is identical => delete nested copy
- If docs/<file> missing => move nested file into docs/
- If different => move nested file into notes/orphaned_docs/ (no data loss)

Run from repo root with the repo venv:

  .\.venv\Scripts\python scripts/cleanup_mkdocs_orphans.py
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import shutil


def sha256_text(path: Path) -> str:
    txt = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    docs = root / "docs"
    nested = docs / "docs"
    notes = root / "notes" / "orphaned_docs"
    notes.mkdir(parents=True, exist_ok=True)

    print(f"[root] {root}")
    print(f"[docs] {docs}")

    # 1) Move patch snippet out of docs/
    patch = docs / "vector_db_coherence_one_pager.patch.md"
    if patch.exists():
        dest = notes / patch.name
        shutil.move(str(patch), str(dest))
        print("[move] docs/vector_db_coherence_one_pager.patch.md -> notes/orphaned_docs/")

    # 2) Reconcile docs/docs
    if nested.exists() and nested.is_dir():
        print("[found] docs/docs (nested) — reconciling...")
        for p in sorted(nested.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(nested)
            target = docs / rel
            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists():
                if sha256_text(p) == sha256_text(target):
                    p.unlink()
                    print(f"[delete] duplicate nested file: docs/docs/{rel.as_posix()}")
                else:
                    dest = notes / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(p), str(dest))
                    print(f"[move] differing nested file -> notes/orphaned_docs/{rel.as_posix()}")
            else:
                shutil.move(str(p), str(target))
                print(f"[move] docs/docs/{rel.as_posix()} -> docs/{rel.as_posix()}")

        # remove empty dirs
        for d in sorted([x for x in nested.rglob("*") if x.is_dir()], reverse=True):
            try:
                next(d.iterdir())
            except StopIteration:
                d.rmdir()
        try:
            next(nested.iterdir())
        except StopIteration:
            nested.rmdir()
            print("[delete] removed empty docs/docs")

    else:
        print("[ok] no docs/docs nesting found")

    print("[done] cleanup complete. Rebuild with:")
    print("       .\.venv\Scripts\python -m mkdocs build --strict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
