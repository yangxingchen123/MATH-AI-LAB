from pathlib import Path

from tools.problem_validator.discovery import find_project_root
from tools.qt_workbench.bootstrap import (
    webengine_blocked,
    webengine_guard_path,
    write_log,
)
from tools.qt_workbench.window import prepare_qt_environment


def test_vbs_launcher_uses_ascii_cmd_path():
    text = Path(find_project_root(), "打开工作台.vbs").read_text(encoding="ascii")
    assert "tools\\qt_workbench\\launch.cmd" in text
    assert "sh.Run cmd, 0, False" in text


def test_bat_calls_ascii_launch_cmd():
    text = Path(find_project_root(), "打开工作台.bat").read_text(encoding="utf-8")
    assert r"tools\qt_workbench\launch.cmd" in text
    cmd = Path(find_project_root(), "tools", "qt_workbench", "launch.cmd").read_text(encoding="utf-8")
    assert "pythonw.exe" in cmd
    assert "start \"\" /D" in cmd or 'start "" /D' in cmd
    assert "-m tools.qt_workbench launch" in cmd


def test_webengine_guard_blocks_without_killing_core(tmp_path, monkeypatch):
    monkeypatch.setenv("TEMP", str(tmp_path))
    monkeypatch.setenv("TMP", str(tmp_path))
    monkeypatch.delenv("MATH_AI_LAB_QT_NO_WEBENGINE", raising=False)
    monkeypatch.delenv("MATH_AI_LAB_QT_FORCE_WEBENGINE", raising=False)
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)
    assert webengine_blocked() is False
    webengine_guard_path().write_text("starting\n", encoding="utf-8")
    assert webengine_blocked() is True
    prepare_qt_environment()
    assert os_env_no_webengine()


def os_env_no_webengine() -> bool:
    import os

    return os.environ.get("MATH_AI_LAB_QT_NO_WEBENGINE") == "1"


def test_write_log_goes_to_temp(tmp_path, monkeypatch):
    monkeypatch.setenv("TEMP", str(tmp_path))
    write_log("hello-launch")
    files = list(tmp_path.glob("math-ai-lab-qt-launch.log"))
    assert files
    assert "hello-launch" in files[0].read_text(encoding="utf-8")
