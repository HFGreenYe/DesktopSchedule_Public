import os
import sys
from pathlib import Path


_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_VALUE_NAME = "WanjiDesktopSchedule"


def _startup_command():
    executable = Path(sys.executable).resolve()
    if getattr(sys, "frozen", False):
        return (
            f'cmd.exe /c start "" /D "{executable.parent}" '
            f'"{executable}"'
        )

    project_root = Path(__file__).resolve().parents[2]
    main_script = project_root / "main.py"
    pythonw = executable.with_name("pythonw.exe")
    if not pythonw.exists():
        pythonw = executable
    return (
        f'cmd.exe /c start "" /D "{project_root}" '
        f'"{pythonw}" "{main_script}"'
    )


def is_startup_enabled():
    if os.name != "nt":
        return False
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _RUN_KEY,
            0,
            winreg.KEY_READ,
        ) as key:
            winreg.QueryValueEx(key, _VALUE_NAME)
            return True
    except FileNotFoundError:
        return False


def set_startup_enabled(enabled):
    if os.name != "nt":
        return False
    import winreg

    if enabled:
        with winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            _RUN_KEY,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(
                key,
                _VALUE_NAME,
                0,
                winreg.REG_SZ,
                _startup_command(),
            )
        return True

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _RUN_KEY,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.DeleteValue(key, _VALUE_NAME)
    except FileNotFoundError:
        pass
    return True
