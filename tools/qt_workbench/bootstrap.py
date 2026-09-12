"""Windows launch helpers. No Frozen Schema. Must not import PySide6."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

LOG_NAME = "math-ai-lab-qt-launch.log"
GUARD_NAME = "math-ai-lab-qt-webengine.guard"


def _temp_dir() -> Path:
    return Path(os.environ.get("TEMP") or os.environ.get("TMP") or ".")


def log_path() -> Path:
    return _temp_dir() / LOG_NAME


def webengine_guard_path() -> Path:
    return _temp_dir() / GUARD_NAME


def write_log(message: str) -> None:
    line = f"{datetime.now().isoformat(timespec='seconds')} {message}"
    path = log_path()
    try:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        return


def notify_error(title: str, text: str) -> None:
    write_log(text)
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, text[:2000], title, 0x10)
            return
        except Exception:
            pass
    sys.stderr.write(text + "\n")


def notify_missing_pyside() -> None:
    notify_error(
        "MATH-AI-LAB",
        "PySide6 未安装，无法打开窗口。\n\n"
        "在仓库根目录运行：\n"
        "python -m pip install -r tools\\qt_workbench\\requirements.txt\n\n"
        f"日志：{log_path()}",
    )


def webengine_blocked() -> bool:
    if os.environ.get("MATH_AI_LAB_QT_NO_WEBENGINE") == "1":
        return True
    if os.environ.get("MATH_AI_LAB_QT_FORCE_WEBENGINE") == "1":
        return False
    return webengine_guard_path().is_file()


def mark_webengine_starting() -> None:
    try:
        webengine_guard_path().write_text("starting\n", encoding="utf-8")
    except OSError:
        return


def clear_webengine_guard() -> None:
    try:
        webengine_guard_path().unlink(missing_ok=True)
    except OSError:
        return
