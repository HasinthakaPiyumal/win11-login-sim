#!/usr/bin/env python3
"""Opt-in installer: launch the simulation when the current user signs in.

What this does and does NOT do
-------------------------------
* Writes exactly ONE value under:
      HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
  This is the standard, documented, per-user autostart mechanism used by
  thousands of ordinary applications (update checkers, chat apps, etc.).
* Requires NO administrator privileges.
* Does NOT touch Winlogon, Userinit, Utilman, any Windows service, Group
  Policy, or any security/authentication setting.
* Only affects the Windows user account that runs this script. It never
  installs for "all users" and never runs before a real sign-in.
* Is fully reversible with ``uninstall_startup.py`` (or by deleting the
  registry value by hand -- see README.md / RECOVERY.md).

This script must be run on Windows (it uses the ``winreg`` module, which only
exists there). Run it with the same user account you want the simulation to
start for -- do not run it elevated / as Administrator.

Usage:
    python scripts\\install_startup.py              # installs
    python scripts\\install_startup.py --target PATH  # custom exe/script path
    python scripts\\install_startup.py --remove      # same as uninstall_startup.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "Win11LoginSim"


def _require_windows() -> None:
    if sys.platform != "win32":
        print(
            "This installer only works on Windows (it edits HKCU\\...\\Run).\n"
            "Nothing was changed.",
            file=sys.stderr,
        )
        sys.exit(1)


def default_target() -> str:
    """Best-guess command line to launch the app.

    Prefers a built executable (dist/Win11LoginSim.exe) next to this repo if
    present; otherwise falls back to `python run.py` from the project root.
    """
    repo_root = Path(__file__).resolve().parent.parent
    exe = repo_root / "dist" / "Win11LoginSim.exe"
    if exe.exists():
        return f'"{exe}"'
    run_py = repo_root / "run.py"
    return f'"{sys.executable}" "{run_py}"'


def install(target_command: str) -> None:
    _require_windows()
    import winreg  # type: ignore  # Windows-only module

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, target_command)

    print("Startup entry installed.")
    print(f"  Registry key : HKEY_CURRENT_USER\\{RUN_KEY}")
    print(f"  Value name   : {VALUE_NAME}")
    print(f"  Command      : {target_command}")
    print()
    print("The simulation will now launch the next time you sign in to Windows.")
    print("To undo this, run: python scripts\\uninstall_startup.py")


def remove() -> None:
    _require_windows()
    import winreg  # type: ignore

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, VALUE_NAME)
        print(f"Removed startup entry '{VALUE_NAME}'. Automatic startup is disabled.")
    except FileNotFoundError:
        print("No startup entry was found; nothing to remove.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        default=None,
        help="Exact command line to run at sign-in (quoted path to the .exe, "
        "or 'python path\\to\\run.py'). Defaults to an auto-detected path.",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove the startup entry instead of installing it.",
    )
    args = parser.parse_args()

    if args.remove:
        remove()
        return

    target = args.target or default_target()
    install(target)


if __name__ == "__main__":
    main()
