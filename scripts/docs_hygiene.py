\
r"""scripts/docs_hygiene.py

One-command docs hygiene:

1) Normalize mkdocs.yml nav for required pages
2) Update doc catalog (docs_current / orphans / removed)
3) Run mkdocs build --strict

Run:
  .\.venv\Scripts\python scripts/docs_hygiene.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    py = sys.executable

    run([py, str(root / "scripts" / "ensure_nav_entries.py")])
    run([py, str(root / "scripts" / "catalog_docs.py")])
    run([py, "-m", "mkdocs", "build", "--strict"])

    print("\n[ok] Docs hygiene complete (nav normalized, catalog updated, strict build passed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
