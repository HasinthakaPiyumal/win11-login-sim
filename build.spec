# PyInstaller build spec for the Win11 Login Simulation.
#
# Build with:
#   pyinstaller build.spec
#
# Produces a single standalone executable at dist/Win11LoginSim.exe.
# No external data files are bundled: all visuals are generated at runtime
# by win11loginsim/assets.py, so there is nothing to ship but code.

# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None
project_root = Path(SPECPATH)

a = Analysis(
    [str(project_root / "run.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=[],
    hiddenimports=[
        "win11loginsim",
        "win11loginsim.app",
        "win11loginsim.assets",
        "win11loginsim.config",
        "win11loginsim.theme",
        "win11loginsim.screens.lock_screen",
        "win11loginsim.screens.login_screen",
        "win11loginsim.screens.surprise_screen",
        "win11loginsim.widgets.password_field",
        "win11loginsim.widgets.spinner",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Win11LoginSim",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # no console window; it's a GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # optional: point to an .ico you own
)
