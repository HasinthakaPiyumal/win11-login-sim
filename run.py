#!/usr/bin/env python3
"""Development entry point: ``python run.py``.

Adds ``src/`` to the path so the app can be run directly from a checkout
without installing it as a package.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from win11loginsim.app import run  # noqa: E402

if __name__ == "__main__":
    sys.exit(run())
