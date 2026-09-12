# -*- coding: utf-8 -*-
from app.ui.task_table_layout import (
    COL_FILE,
    COL_PAGES,
    COL_REC,
    LOCKED_TASK_COLUMNS,
    OPTIONAL_TASK_COLUMNS,
    is_optional_task_column,
)


def test_optional_task_columns_are_toggles():
    assert COL_PAGES in OPTIONAL_TASK_COLUMNS
    assert COL_REC in OPTIONAL_TASK_COLUMNS
    assert COL_FILE not in OPTIONAL_TASK_COLUMNS
    assert COL_FILE in LOCKED_TASK_COLUMNS
    assert is_optional_task_column(COL_REC)
    assert not is_optional_task_column(COL_FILE)
