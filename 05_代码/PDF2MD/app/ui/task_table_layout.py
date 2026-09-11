# -*- coding: utf-8 -*-
"""任务表列：可选列、窗口最小尺寸。列显隐和列宽由用户拖动/右键表头决定。"""
from __future__ import annotations

# 与 MainWindow.COL_* 对齐
COL_CHECK = 0
COL_FILE = 1
COL_PAGES = 2
COL_MODE = 3
COL_STAGE = 4
COL_STATUS = 5
COL_REC = 6
COL_POST = 7
COL_TIME = 8
COL_ACTIONS = 9

OPTIONAL_TASK_COLUMNS = (
    COL_PAGES,
    COL_MODE,
    COL_STAGE,
    COL_REC,
    COL_POST,
    COL_TIME,
)
LOCKED_TASK_COLUMNS = (COL_CHECK, COL_FILE, COL_STATUS, COL_ACTIONS)

WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 560
PROFILE_MIN_WIDTH = 180


def is_optional_task_column(col: int) -> bool:
    return col in OPTIONAL_TASK_COLUMNS
