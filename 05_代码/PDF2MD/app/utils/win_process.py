# -*- coding: utf-8 -*-
"""Windows 子进程启动：隐藏窗口，且不额外弹出空控制台。"""
from __future__ import annotations

import os
from pathlib import Path

# CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
# 不要加 DETACHED_PROCESS（0x8）：Win11 上经常仍会分配一个空 Terminal。
CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_PROCESS_GROUP = 0x00000200
DETACHED_PROCESS = 0x00000008


def hidden_creationflags() -> int:
    if os.name != "nt":
        return 0
    return CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP


def prefer_pythonw(python_exe: Path | None) -> Path | None:
    """同目录存在 pythonw.exe 时优先用它，避免弹出控制台。"""
    if python_exe is None:
        return None
    py = Path(python_exe)
    if os.name != "nt":
        return py
    if py.name.lower() == "python.exe":
        cand = py.with_name("pythonw.exe")
        if cand.is_file():
            return cand
    return py
