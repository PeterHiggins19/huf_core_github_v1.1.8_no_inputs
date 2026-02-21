\
r"""scripts/repo_cleanup.py

Repo hygiene helper.

Goal:
- Remove generated outputs from Git tracking (without deleting your local copies)
- Keep the repo looking like a Python project (not “92% HTML” from committed site/)

This script is SAFE by default: it prints what it would do.

Run (dry-run):
  .\.venv\Scripts\python scripts/repo_cleanup.py

Apply (actually runs git rm --cached):
  .\.venv\Scripts\python scripts/repo_cleanup.py --apply
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


CANDIDATES = [
    "site",
    "out",
    "huf_core.egg-info",
]


def run_git(args: list[str], root: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=str(root), text=True, errors="replace")


def is_tracked(path: str, root: Path) -> bool:
    try:
        out = run_git(["ls-files", "--", path], root).strip()
        return bool(out)
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Run git rm --cached for tracked candidates.")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]

    try:
        run_git(["rev-parse", "--is-inside-work-tree"], root)
    except Exception:
        print("[err] Not a git repository (or git not available). Run from the repo root.")
        return 2

    tracked = [p for p in CANDIDATES if is_tracked(p, root)]
    if not tracked:
        print("[ok] No tracked generated folders detected (site/, out/, *.egg-info/).")
        return 0

    print("[found] Tracked generated outputs:")
    for p in tracked:
        print("  -", p)

    print("\nRecommended commands:")
    cmd = "git rm -r --cached " + " ".join(tracked)
    print("  " + cmd)
    print('  git commit -m "Repo hygiene: stop tracking generated outputs"')
    print("  git push\n")

    if not args.apply:
        print("[dry-run] No changes applied. Re-run with --apply to execute git rm --cached.")
        return 0

    print("[apply] Running:", cmd)
    subprocess.check_call(["git", "rm", "-r", "--cached", *tracked], cwd=str(root))
    print("[next] Now commit and push:")
    print('  git commit -m "Repo hygiene: stop tracking generated outputs"')
    print("  git push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
