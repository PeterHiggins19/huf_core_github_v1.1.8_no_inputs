#!/usr/bin/env python3
"""Bootstrap a local dev/runtime environment for HUF Core.

Goal: help non-GitHub-native / GUI-first users get to a runnable setup fast.

What it does:
1) Creates a .venv virtual environment (if missing)
2) Upgrades pip
3) Installs this package in editable mode with [dev] extras

It does NOT:
- Download large upstream datasets (use scripts/fetch_data.py)
- Require 'make' (works on Windows/Mac/Linux)

Usage:
  python scripts/bootstrap.py
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None)


def venv_python(venv_dir: Path) -> Path:
    if platform.system().lower().startswith("win"):
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    venv_dir = repo_root / ".venv"
    py = sys.executable

    if not venv_dir.exists():
        print(f"Creating virtual environment at: {venv_dir}")
        run([py, "-m", "venv", str(venv_dir)], cwd=repo_root)
    else:
        print(f"Virtual environment already exists: {venv_dir}")

    vpy = venv_python(venv_dir)
    if not vpy.exists():
        print("ERROR: venv python not found at", vpy)
        return 2

    # Upgrade pip/setuptools/wheel to reduce install friction
    run([str(vpy), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], cwd=repo_root)

    # Install editable with dev extras (includes pytest, mkdocs, etc.)
    run([str(vpy), "-m", "pip", "install", "-e", ".[dev]"], cwd=repo_root)

    print("\n✅ Bootstrap complete. Next steps:\n")
    if platform.system().lower().startswith("win"):
        print("1) Download civic inputs (Markham + Toronto):")
        print(r"   .venv\Scripts\python scripts\fetch_data.py --markham --toronto")
        print("   (Non-interactive Toronto: add --yes)\n")
        print("2) Run a case:")
        print(r"   .venv\Scripts\huf --help")
    else:
        print("1) Download civic inputs (Markham + Toronto):")
        print("   ./.venv/bin/python scripts/fetch_data.py --markham --toronto")
        print("   (Non-interactive Toronto: add --yes)\n")
        print("2) Run a case:")
        print("   ./.venv/bin/huf --help")

    print("\nIf you prefer Make targets (Mac/Linux): make fetch-data, make fetch-toronto-yes, make planck-guide\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
