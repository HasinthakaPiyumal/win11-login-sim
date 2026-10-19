"""Filesystem path helpers.

Centralises every path the application uses so behaviour is identical whether
running from source or from a PyInstaller-frozen executable.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = "Win11LoginSim"


def is_frozen() -> bool:
    """Return True when running inside a PyInstaller bundle."""
    return bool(getattr(sys, "frozen", False))


def app_data_dir() -> Path:
    """Return the per-user application data directory, creating it if needed.

    On Windows this resolves to ``%APPDATA%\\Win11LoginSim``. On other
    platforms (useful for development) it falls back to a sensible location so
    the project can still be exercised outside Windows.
    """
    base = os.environ.get("APPDATA")
    if base:
        root = Path(base)
    else:
        # Non-Windows fallback (development / CI only).
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    directory = root / APP_DIR_NAME
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def config_path() -> Path:
    """Return the path to the JSON configuration file."""
    return app_data_dir() / "config.json"


def executable_path() -> Path:
    """Return the path used to (re)launch the application.

    When frozen this is the .exe itself; otherwise it is the Python
    interpreter. Used by the startup installer script.
    """
    return Path(sys.executable)
