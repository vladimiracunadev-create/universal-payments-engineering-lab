#!/usr/bin/env python3
"""Repository wrapper for the installed ``paylab`` CLI."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from payments_lab.cli import main  # noqa: E402


if __name__ == "__main__":
    main()
