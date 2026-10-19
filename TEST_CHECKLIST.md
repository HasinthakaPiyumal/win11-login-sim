# Test Checklist

Run through this on the target ASUS laptop (Windows 11 Home) before relying
on the app, and again after any change to config or startup setup.

## Startup (manual launch)

- [ ] `python run.py` launches full‑screen on the primary display.
- [ ] `python -m win11loginsim` also launches correctly.
- [ ] Built `dist\Win11LoginSim.exe` launches correctly with no console window.
- [ ] First launch creates `%APPDATA%\Win11LoginSim\config.json` with defaults.
- [ ] Deleting/corrupting `config.json` and relaunching still starts the app
      (falls back to defaults, logs the error, does not crash).

## Startup (automatic, opt‑in)

- [ ] Before installing: `Win11LoginSim` is **not** present in Task Manager →
      Startup apps, and not present under
      `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.
- [ ] `python scripts\install_startup.py` reports success and prints the
      registry key, value name, and command used.
- [ ] After installing: value appears under the `Run` key (check via
      `regedit` or `reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run`).
- [ ] Sign out and back in (or reboot): the app launches automatically after
      reaching the real Windows desktop — confirming it runs *after*, never
      *instead of*, the actual Windows sign‑in.
- [ ] `python scripts\uninstall_startup.py` removes the value; app no longer
      auto‑starts on next sign‑in.
- [ ] Startup install/uninstall both complete without any admin/UAC prompt.

## Multiple display resolutions

Test at each of (resize the display or use a second monitor / RDP session):

- [ ] 1920×1080 (typical laptop panel)
- [ ] 2560×1440
- [ ] 1366×768 (lower‑end laptop)
- [ ] A scaled DPI setting, e.g. 125% or 150% Windows display scaling

For each:
- [ ] Window covers the entire screen with no gaps or overflow.
- [ ] Wallpaper fills the screen without visible seams or stretching artifacts.
- [ ] Sign‑in card, avatar, and text remain centered and fully visible.
- [ ] Clock/date (lock screen) and surprise text wrap/fit without clipping.

## Keyboard & navigation

- [ ] On the lock screen, any key press slides it up to the login screen.
- [ ] A printable key pressed on the lock screen appears as the first
      character in the password box.
- [ ] On the lock screen, a mouse click also advances to the login screen.
- [ ] Tab cycles focus: password field → reveal button (visible once text is
      typed) → submit arrow, in a sensible order; focused buttons show an outline.
- [ ] Typing in the password field and pressing **Enter** submits.
- [ ] Clicking the arrow button submits.
- [ ] Submitting empty input shakes the password box and does **not** proceed.
- [ ] Submitting any non‑empty text (default `demo_mode = "any"`) shows the
      progress ring and "Welcome", then cross-fades to the surprise screen.
- [ ] With `demo_mode = "fixed"`, only `demo_password` is accepted; any other
      text shows "The password is incorrect. Try again." and shakes the box.
- [ ] No on-screen hint text appears on any screen.
- [ ] Network/battery/accessibility/power glyphs render bottom-right
      (Segoe Fluent Icons) and do nothing when clicked.
- [ ] Reveal button switches between masked and revealed text correctly.
- [ ] Surprise screen animation stays smooth (no visible stutter) at native
      resolution.
- [ ] **Escape** closes the app when `allow_escape_exit` is `true`.
- [ ] **Ctrl+Shift+Q** closes the app from the lock screen, login screen, and
      surprise screen, every time, with no exceptions.
- [ ] **Alt+F4** closes the app from any screen.
- [ ] Ctrl+Alt+Del still opens the normal Windows security screen as usual
      (confirms nothing is intercepting it).
- [ ] Ctrl+Shift+Esc still opens Task Manager as usual.

## Recovery

- [ ] With the app running, Ctrl+Shift+Q closes it within ~1 second.
- [ ] With the app apparently frozen (simulate by pausing the process), Task
      Manager can still end it.
- [ ] Following `RECOVERY.md` end‑to‑end (as if you knew nothing else) results
      in a clean, fully closed app and no auto‑start remaining, using only the
      steps documented there.
- [ ] After full uninstall (delete folder + remove startup entry + delete
      `%APPDATA%\Win11LoginSim`), no trace of the app affects subsequent
      Windows sign‑ins.

## Robustness

- [ ] Launching twice simultaneously does not crash or corrupt config (second
      instance just opens its own window).
- [ ] Killing the process abruptly (Task Manager → End task) leaves no
      locked files and does not corrupt `config.json` on next launch.
- [ ] No network requests are made at any point (verify with a network
      monitor / firewall log if desired — app works identically offline).
