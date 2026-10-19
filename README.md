# Win11 Login Simulation

A polished, interactive, Windows‑11‑styled **sign‑in simulation** for personal
entertainment, built with Python + PySide6. It looks like a Windows 11
lock/sign‑in screen, accepts any demo input, "signs you in," and reveals a
surprise message.

> **This is not a real Windows sign‑in screen and cannot be one.** A normal
> desktop application runs *after* Windows has already authenticated you — it
> has no way to run before, during, or in place of the real Windows logon
> (Winlogon). This project never attempts to. It is a themed window that
> looks similar, for fun, on your own already‑unlocked desktop.

## What this is / is not

| | |
|---|---|
| ✅ Is | A full‑screen Qt window styled like the Win11 lock/sign‑in UI |
| ✅ Is | A **local, simulated** credential check (any non‑empty text by default) |
| ✅ Is | Opt‑in, reversible, per‑user startup via the normal `Run` registry key |
| ❌ Is not | Real Windows authentication, in any form |
| ❌ Is not | A credential collector — it never reads, logs, or transmits real passwords |
| ❌ Is not | A way to block Ctrl+Alt+Del, Task Manager, or any Windows security surface |
| ❌ Is not | Something that edits Winlogon, Userinit, Utilman, services, or security policy |

## Requirements

* Windows 11 (developed/target platform). The app also launches on other
  desktop OSes for development, with the Windows‑specific startup scripts
  disabled there.
* Python 3.10+
* Dependencies in `requirements.txt`

## Setup

```powershell
cd win11-login-sim
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running (development)

```powershell
python run.py
```

or

```powershell
python -m win11loginsim
```

The app opens full‑screen on your primary display.

### Using it

1. **Lock screen**: large clock and date over a generated "bloom" wallpaper.
   Click or press any key and it slides up. A typed character carries over
   into the password box, as on Windows.
2. **Sign-in screen**: blurred backdrop, account picture, name and a
   Windows 11-style password box (reveal button and submit arrow inside it).
   Press **Enter** or the arrow. Empty input makes the box shake. Otherwise a
   progress ring and "Welcome" play briefly.
3. **Surprise screen**: cross-fades in with drifting lights, twinkling
   sparkles, a bobbing gift and the configured message.

No instructions or hints are shown on screen. The exit shortcuts below
always work.

### Exiting — always available

* **Ctrl+Shift+Q** — closes the app immediately, from any screen, always.
* **Escape** — also closes it (enabled by default; see Configuration).
* **Alt+F4**, closing from the taskbar, or ending it in Task Manager — all
  work normally, exactly like any other window. Nothing blocks them.

See `RECOVERY.md` for the full recovery procedure, including what to do if
the app was set to start automatically and you want it gone.

## Configuration

On first run, a config file is created at:

```
%APPDATA%\Win11LoginSim\config.json
```

Edit it (app must be closed) and relaunch to apply changes. Key fields:

| Field | Meaning |
|---|---|
| `display_name` | Name shown under the avatar |
| `avatar_initials` | Override initials; blank = derived from `display_name` |
| `demo_mode` | `"any"` (default, accepts any non‑empty text) or `"fixed"` |
| `demo_password` | Only used when `demo_mode` is `"fixed"` |
| `show_clock` | Show clock/date on the lock screen |
| `stay_on_top` | Keep window above others |
| `allow_escape_exit` | Let Escape close the app (recommended: keep `true`) |
| `countdown_seconds` | Decorative countdown on the surprise screen (0 = off) |
| `surprise_title` / `surprise_subtitle` | The reveal message text |
| `accent_hex` | Accent colour, e.g. `"#0067C0"` |

The app never requires an internet connection; all visuals (wallpaper,
avatar) are drawn at runtime with `QPainter` — no bundled images, no
downloads.

## Building a standalone .exe

```powershell
pip install pyinstaller
pyinstaller build.spec
```

The executable is produced at `dist\Win11LoginSim.exe`. It bundles the Python
runtime and PySide6; no separate install of Python is needed to run it.

## Automatic startup (optional, opt‑in, reversible)

By default the app does **not** start automatically. If you want it to launch
when *you* sign in to Windows:

```powershell
python scripts\install_startup.py
```

This adds exactly one value, `Win11LoginSim`, under the **per‑user** registry
key:

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
```

This is the same ordinary mechanism many normal applications use (e.g. chat
clients, update checkers). It:

* requires no administrator rights,
* only affects your own user account,
* never runs before you've already signed in and reached your desktop,
* does not touch Winlogon, Userinit, Utilman, services, or Group Policy.

### Disabling automatic startup

```powershell
python scripts\uninstall_startup.py
```

or manually: open `regedit`, navigate to
`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`, and delete
the `Win11LoginSim` value. You can also disable it via
**Task Manager → Startup apps** (Windows 11) without ever opening the
registry editor.

### Alternative: Task Scheduler

If you prefer Task Scheduler over the Run key:

```powershell
schtasks /Create /SC ONLOGON /TN "Win11LoginSim" ^
  /TR "\"C:\path\to\dist\Win11LoginSim.exe\"" /RL LIMITED
```

Remove it with:

```powershell
schtasks /Delete /TN "Win11LoginSim" /F
```

`/RL LIMITED` keeps the task running with your normal (non‑elevated) user
rights — do not use `/RL HIGHEST` or run this from an elevated prompt; the app
never needs administrator privileges.

## Keyboard & accessibility

* **Enter** — submit the password field.
* **Tab / Shift+Tab** — move focus between the field, the eye‑toggle, and the
  sign‑in button, following standard Qt focus order.
* **Escape** — exits the simulation (toggle via `allow_escape_exit`).
* **Ctrl+Shift+Q** — always exits, unconditionally.
* The app installs **no** keyboard hooks, drivers, or system‑wide input
  filters, and never intercepts Ctrl+Alt+Del or any other Windows security
  shortcut. It only receives ordinary key events sent to its own window, like
  any other application.

## Safety & privacy

* No real credentials are ever read, stored, or transmitted. The password
  field is a plain, local `QLineEdit`; its contents are compared only against
  the local demo config (default: "any non‑empty text passes") and then
  discarded.
* No network access is performed at any point.
* No system files, services, or authentication/security settings are
  modified. The only persistent changes this project can make are: (a) its own
  config JSON in `%APPDATA%\Win11LoginSim`, and (b) the single optional
  per‑user `Run` registry value described above.

## Project structure

```
win11-login-sim/
├── run.py                    # dev entry point
├── requirements.txt
├── build.spec                 # PyInstaller config
├── README.md
├── RECOVERY.md
├── TEST_CHECKLIST.md
├── scripts/
│   ├── install_startup.py
│   └── uninstall_startup.py
└── src/win11loginsim/
    ├── app.py                 # window + screen orchestration + safety exit
    ├── config.py
    ├── assets.py               # wallpaper + avatar generated with QPainter
    ├── theme.py
    ├── utils/paths.py
    ├── widgets/
    │   ├── password_field.py
    │   ├── spinner.py
    │   └── status_icons.py     # decorative network/battery/power glyphs
    └── screens/
        ├── base.py             # shared cover-scaled background
        ├── lock_screen.py
        ├── login_screen.py
        └── surprise_screen.py
```
