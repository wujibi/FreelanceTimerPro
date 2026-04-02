#!/usr/bin/env python3
"""
Windows launcher for Freelance Timer Pro.

`launcher.pyw` is intended for double-click/shortcut usage and delegates to
`main.py` after forcing the working directory to this project folder so paths
stay consistent regardless of where it was launched from.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_project_cwd() -> Path:
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)
    return script_dir


def _preflight(script_dir: Path) -> None:
    if sys.version_info < (3, 8):
        raise RuntimeError(f"Python 3.8+ required. Current version: {sys.version}")

    if not (script_dir / "main.py").exists():
        raise FileNotFoundError(f"main.py not found in: {script_dir}")


def main() -> int:
    try:
        script_dir = _ensure_project_cwd()
        _preflight(script_dir)

        from main import main as app_main

        app_main()
        return 0
    except Exception as exc:
        # Keep this as plain print so failures are still visible when launched
        # from a terminal; .pyw launches can be inspected via logs if needed.
        print(f"Launcher error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
