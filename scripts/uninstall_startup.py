#!/usr/bin/env python3
"""Remove the per-user startup entry created by install_startup.py.

This only deletes the single ``Win11LoginSim`` value under
``HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run``.
It touches nothing else. Safe to run even if the entry was never installed.
"""

from install_startup import remove

if __name__ == "__main__":
    remove()
