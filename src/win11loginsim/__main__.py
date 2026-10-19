"""Allows running with ``python -m win11loginsim``."""

import sys

from .app import run

if __name__ == "__main__":
    sys.exit(run())
