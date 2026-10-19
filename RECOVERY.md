# Recovery Procedure

This app is a normal desktop window, not a system component, so recovery is
always straightforward. Use whichever of these is fastest.

## 1. While the app is running

Any of these always work, from any screen:

* Press **Ctrl+Shift+Q** — closes the app immediately. This shortcut is
  wired unconditionally in `app.py` (`MainWindow._install_safety_shortcuts`)
  and is not affected by configuration.
* Press **Escape** (enabled by default via `allow_escape_exit` in config).
* Press **Alt+F4**.
* Right‑click the taskbar icon → **Close window**.

## 2. If the window seems unresponsive

Windows' own tools are never blocked by this app:

1. Press **Ctrl+Shift+Esc** to open **Task Manager** directly (this bypasses
   the app entirely and is never intercepted by it).
2. Find **Win11LoginSim** (or `python.exe` / `pythonw.exe` if running from
   source) in the **Processes** tab.
3. Select it → **End task**.

Ctrl+Alt+Del and Task Manager are deliberately never hooked, suppressed, or
interfered with by this project — it contains no code that could do so.

## 3. If it was set to start automatically and you want that gone

Run the uninstaller (no admin rights required):

```powershell
cd win11-login-sim
python scripts\uninstall_startup.py
```

Or remove it manually, three ways — pick whichever you're comfortable with:

**A. Task Manager (easiest, no registry editor):**
Task Manager → **Startup apps** tab → select **Win11LoginSim** → **Disable**.

**B. Registry Editor:**
1. Press `Win+R`, type `regedit`, press Enter.
2. Navigate to:
   `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
3. Select the `Win11LoginSim` value → **Delete**.
4. Close Registry Editor. No restart required.

**C. Task Scheduler (only if you used the Task Scheduler method):**
```powershell
schtasks /Delete /TN "Win11LoginSim" /F
```

## 4. Uninstalling entirely

Since the app never touches system files:

1. Run `scripts\uninstall_startup.py` (or steps 3A/3B above) if you enabled
   auto‑start.
2. Delete the project folder.
3. Optionally delete its config folder:
   `%APPDATA%\Win11LoginSim`

No reboot, Safe Mode, System Restore, or Windows reinstall is ever required —
this app cannot put Windows into a state that needs them, because it never
modifies Winlogon, Userinit, Utilman, services, or security/authentication
settings.

## 5. If you are ever in doubt

Windows' real sign‑in screen, Ctrl+Alt+Del, Task Manager, Safe Mode, and
System Restore all continue to work exactly as normal at all times — this
project has no mechanism to affect any of them, by design.
