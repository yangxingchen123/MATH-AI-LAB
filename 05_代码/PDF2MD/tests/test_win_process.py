# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path

from app.ocr.deepseek_worker_client import DeepSeekWorkerClient
from app.utils.win_process import (
    DETACHED_PROCESS,
    hidden_creationflags,
    prefer_pythonw,
)


def test_hidden_creationflags_omit_detached():
    flags = hidden_creationflags()
    if os.name != "nt":
        assert flags == 0
        return
    assert flags & DETACHED_PROCESS == 0
    assert flags != 0


def test_deepseek_and_paddle_share_hidden_flags():
    ds = DeepSeekWorkerClient(allow_spawn=False)._spawn_creationflags()
    from app.utils.win_process import hidden_creationflags as hf

    assert ds == hf()


def test_prefer_pythonw_same_dir(tmp_path: Path):
    py = tmp_path / "python.exe"
    pyw = tmp_path / "pythonw.exe"
    py.write_text("", encoding="utf-8")
    if os.name == "nt":
        pyw.write_text("", encoding="utf-8")
        assert prefer_pythonw(py) == pyw
    else:
        assert prefer_pythonw(py) == py
