# -*- coding: utf-8 -*-
"""低成本 UI 回归：尺寸、默认按钮、列数。不测像素截图。"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

from app.dialogs.help_dialog import HelpDialog
from app.dialogs.experiment_results_dialog import (
    CORE_COLUMNS,
    ExperimentResultsDialog,
    _CORE_COLS,
    _TABLE_COLS,
)
from app.dialogs.formula_benchmark_dialog import FormulaBenchmarkDialog
from app.dialogs.settings_dialog import SettingsDialog
from app.main_window import MainWindow
from app.ui.icons import icon
from app.ui.theme import install_theme


def _app() -> QApplication:
    inst = QApplication.instance()
    if inst is not None:
        return inst
    app = QApplication([])
    install_theme(app, "浅色")
    return app


def _isolate_history(monkeypatch, records=None):
    monkeypatch.setattr("app.task_history.load_history", lambda path=None: list(records or []))
    monkeypatch.setattr("app.task_history.upsert_history", lambda record, path=None: None)
    monkeypatch.setattr("app.task_history.save_history", lambda records, path=None: None)
    monkeypatch.setattr("app.task_history.remove_history", lambda rid, path=None: None)
    monkeypatch.setattr("app.task_history.load_trash", lambda path=None: [])
    monkeypatch.setattr("app.task_history.save_trash", lambda records, path=None: None)
    monkeypatch.setattr("app.task_history.push_trash", lambda record, path=None: None)
    monkeypatch.setattr("app.task_history.pop_trash", lambda rid, path=None: None)


def test_main_window_minimum_and_defaults(monkeypatch):
    _isolate_history(monkeypatch)
    _app()
    w = MainWindow()
    assert w.minimumWidth() >= 800
    assert w.minimumHeight() >= 560
    assert w.table.columnCount() == len(MainWindow.COLS) == 10
    assert MainWindow.COLS[0] == ""
    assert MainWindow.COLS[1] == "文件"
    assert MainWindow.COLS_MARKDOWN[0] == "文件"
    assert "操作" not in MainWindow.COLS_MARKDOWN
    assert w.table.verticalHeader().isHidden()
    from PySide6.QtWidgets import QHeaderView

    header = w.table.horizontalHeader()
    assert header.sectionsMovable()
    assert header.stretchLastSection()
    assert header.visualIndex(MainWindow.COL_ACTIONS) == header.count() - 1
    assert (
        header.sectionResizeMode(MainWindow.COL_PAGES)
        == QHeaderView.ResizeMode.Interactive
    )
    assert w.table.acceptDrops()
    assert w.btn_start.isDefault()
    assert not w.btn_clear.isDefault()
    assert not w.btn_cancel.isDefault()
    assert not w.empty_hint.isHidden()
    assert w.table.isHidden()
    assert "EPUB" in w.drop.title.text()
    assert not hasattr(w, "btn_history")
    assert w.btn_delete_selected.text() == "删除选中"
    assert w.btn_trash.text().startswith("回收站")
    assert not w.btn_delete_selected.isEnabled()
    from PySide6.QtWidgets import QAbstractItemView

    assert w.table.selectionMode() == QAbstractItemView.SelectionMode.ExtendedSelection
    w.close()


def test_images_scale_radio_values(monkeypatch):
    _isolate_history(monkeypatch)
    _app()
    w = MainWindow()
    w.rb_img_fast.setChecked(True)
    assert w._images_scale() == 1.0
    w.rb_img_std.setChecked(True)
    assert w._images_scale() == 2.0
    w.rb_img_hq.setChecked(True)
    assert w._images_scale() == 3.0
    w.close()


def test_deepseek_checkbox_stays_enabled_and_snaps_to_balanced(monkeypatch):
    _isolate_history(monkeypatch)
    monkeypatch.setattr(MainWindow, "_kick_deepseek_background_warmup", lambda self: None)
    monkeypatch.setattr(MainWindow, "_shutdown_deepseek_ocr2", lambda self: None)
    _app()
    w = MainWindow()
    qi = w.cmb_formula_recovery.findData("quality")
    w.cmb_formula_recovery.setCurrentIndex(qi if qi >= 0 else 2)
    assert w.cb_deepseek_lp.isEnabled()
    assert w.cb_formulas.isEnabled()
    w.cb_deepseek_lp.setChecked(True)
    assert w.cb_deepseek_lp.isChecked()
    assert w._formula_recovery_preset() == "quality"
    assert w._deepseek_limited_production() is True
    w.cb_formulas.setChecked(True)
    assert w.cb_formulas.isChecked()
    fi = w.cmb_formula_recovery.findData("fast")
    w.cmb_formula_recovery.setCurrentIndex(fi if fi >= 0 else 0)
    w.cb_deepseek_lp.setChecked(True)
    assert w._formula_recovery_preset() == "balanced"
    w.close()


def test_add_task_shows_filename_and_check(tmp_path: Path, monkeypatch):
    _isolate_history(monkeypatch)
    _app()
    w = MainWindow()
    pdf = tmp_path / "抽样调查实验.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    w._add_task(pdf)
    assert w.table.rowCount() == 1
    assert w.table.item(0, MainWindow.COL_FILE).text() == "抽样调查实验.pdf"
    cb = w._check_at(0)
    assert cb is not None
    assert cb.isChecked()
    w.close()


def test_add_task_newest_on_top(tmp_path: Path, monkeypatch):
    _isolate_history(monkeypatch)
    _app()
    w = MainWindow()
    older = tmp_path / "old.pdf"
    newer = tmp_path / "new.pdf"
    older.write_bytes(b"%PDF-1.4\n")
    newer.write_bytes(b"%PDF-1.4\n")
    w._add_task(older)
    w._add_task(newer)
    assert w.table.rowCount() == 2
    assert w.table.item(0, MainWindow.COL_FILE).text() == "new.pdf"
    assert w.table.item(1, MainWindow.COL_FILE).text() == "old.pdf"
    w._add_task(older)
    assert w.table.item(0, MainWindow.COL_FILE).text() == "old.pdf"
    assert w.table.item(1, MainWindow.COL_FILE).text() == "new.pdf"
    cb = w._check_at(1)
    assert cb is not None
    cb.click()
    names = {t.name for t in w._selected_tasks()}
    assert names == {"old.pdf", "new.pdf"}
    assert w._check_at(0).isChecked()
    assert w._check_at(1).isChecked()
    w.close()


def test_restore_history_newest_on_top(tmp_path: Path, monkeypatch):
    older = tmp_path / "old.pdf"
    newer = tmp_path / "new.pdf"
    older.write_bytes(b"%PDF-1.4\n")
    newer.write_bytes(b"%PDF-1.4\n")
    records = [
        {
            "id": str(older.resolve()),
            "path": str(older),
            "name": "old.pdf",
            "started_at": "2026-01-01T10:00:00",
            "status": "完成",
        },
        {
            "id": str(newer.resolve()),
            "path": str(newer),
            "name": "new.pdf",
            "started_at": "2026-09-08T12:00:00",
            "status": "等待",
        },
    ]
    _isolate_history(monkeypatch, records)
    _app()
    w = MainWindow()
    assert w.table.rowCount() == 2
    assert w.table.item(0, MainWindow.COL_FILE).text() == "new.pdf"
    assert w.table.item(1, MainWindow.COL_FILE).text() == "old.pdf"
    assert w.table.isHidden() is False
    w.close()


def test_done_task_without_formula_qa_shows_disabled(tmp_path: Path, monkeypatch):
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    records = [
        {
            "id": str(pdf.resolve()),
            "path": str(pdf),
            "name": "book.pdf",
            "status": "完成",
            "engine": "Docling",
            "workflow": "快速自动",
            "output_dir": str(tmp_path / "out"),
        }
    ]
    _isolate_history(monkeypatch, records)
    _app()
    w = MainWindow()
    assert w.table.item(0, MainWindow.COL_REC).text() == "未启用"
    assert w.table.item(0, MainWindow.COL_POST).text() == "未启用"
    cell = w.table.cellWidget(0, MainWindow.COL_ACTIONS)
    assert cell is not None
    from PySide6.QtWidgets import QPushButton

    assert "重试" in [b.text() for b in cell.findChildren(QPushButton)]
    header = w.table.horizontalHeader()
    act_item = w.table.horizontalHeaderItem(MainWindow.COL_ACTIONS)
    assert act_item is not None
    assert int(act_item.textAlignment()) & int(Qt.AlignmentFlag.AlignHCenter)
    w.close()


def test_task_table_optional_column_can_toggle(tmp_path: Path, monkeypatch):
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    _isolate_history(
        monkeypatch,
        [
            {
                "id": str(pdf.resolve()),
                "path": str(pdf),
                "name": "book.pdf",
                "status": "完成",
                "engine": "Docling",
                "workflow": "快速自动",
            }
        ],
    )
    _app()
    w = MainWindow()
    header = w.table.horizontalHeader()
    assert header.sectionsMovable()
    w._set_task_column_visible(MainWindow.COL_REC, False)
    assert w.table.isColumnHidden(MainWindow.COL_REC)
    w._set_task_column_visible(MainWindow.COL_REC, True)
    assert not w.table.isColumnHidden(MainWindow.COL_REC)
    w._set_task_column_visible(MainWindow.COL_FILE, False)
    assert not w.table.isColumnHidden(MainWindow.COL_FILE)
    header.moveSection(header.visualIndex(MainWindow.COL_ACTIONS), 2)
    w._pin_actions_column()
    assert header.visualIndex(MainWindow.COL_ACTIONS) == header.count() - 1
    w.close()


def test_explorer_header_handle_skips_window_edge():
    _app()
    from app.ui.widgets.task_table import ExplorerHeaderView, FileDropTableWidget

    table = FileDropTableWidget(0, 4)
    table.resize(400, 80)
    for i in range(4):
        table.setColumnWidth(i, 80)
    header = table.horizontalHeader()
    assert isinstance(header, ExplorerHeaderView)
    assert header.stretchLastSection()
    x0 = header.sectionViewportPosition(0) + header.sectionSize(0)
    assert header.handle_logical_at(x0) == 0
    last = header.logicalIndex(header.count() - 1)
    x_last = header.sectionViewportPosition(last) + header.sectionSize(last) - 1
    assert header.handle_logical_at(x_last) is None
    table.deleteLater()


def test_delete_selected_moves_to_trash(tmp_path: Path, monkeypatch):
    hist = tmp_path / "task_history.json"
    trash = tmp_path / "task_trash.json"
    monkeypatch.setattr("app.task_history.history_path", lambda: hist)
    monkeypatch.setattr("app.task_history.trash_path", lambda: trash)
    _app()
    w = MainWindow()
    keep = tmp_path / "keep.pdf"
    gone = tmp_path / "gone.pdf"
    keep.write_bytes(b"%PDF-1.4\n")
    gone.write_bytes(b"%PDF-1.4\n")
    w._add_task(keep)
    w._add_task(gone)
    assert w.table.item(0, MainWindow.COL_FILE).text() == "gone.pdf"
    w._delete_selected()
    assert w.table.rowCount() == 1
    assert w.table.item(0, MainWindow.COL_FILE).text() == "keep.pdf"
    from app.task_history import load_history, load_trash

    trash_rows = load_trash()
    assert len(trash_rows) == 1
    assert trash_rows[0]["name"] == "gone.pdf"
    assert "deleted_at" in trash_rows[0]
    hist_names = {r.get("name") for r in load_history()}
    assert "gone.pdf" not in hist_names
    assert "keep.pdf" in hist_names
    assert w.btn_trash.text() == "回收站 (1)"
    w._restore_from_trash(trash_rows[0])
    assert w.table.rowCount() == 2
    assert w.table.item(0, MainWindow.COL_FILE).text() == "gone.pdf"
    assert load_trash() == []
    assert w.btn_trash.text() == "回收站"
    w._delete_selected()
    assert w.table.rowCount() == 1
    w._add_task(gone)
    assert w.table.rowCount() == 2
    assert w.table.item(0, MainWindow.COL_FILE).text() == "gone.pdf"
    assert load_trash() == []
    w.close()


def test_multi_select_delete(tmp_path: Path, monkeypatch):
    hist = tmp_path / "task_history.json"
    trash = tmp_path / "task_trash.json"
    monkeypatch.setattr("app.task_history.history_path", lambda: hist)
    monkeypatch.setattr("app.task_history.trash_path", lambda: trash)
    _app()
    w = MainWindow()
    files = [tmp_path / name for name in ("a.pdf", "b.pdf", "c.pdf")]
    for p in files:
        p.write_bytes(b"%PDF-1.4\n")
        w._add_task(p)
    assert [w.table.item(r, MainWindow.COL_FILE).text() for r in range(3)] == [
        "c.pdf",
        "b.pdf",
        "a.pdf",
    ]
    assert {t.name for t in w._selected_tasks()} == {"c.pdf"}
    w._check_at(1).click()
    assert {t.name for t in w._selected_tasks()} == {"c.pdf", "b.pdf"}
    w._delete_selected()
    assert w.table.rowCount() == 1
    assert w.table.item(0, MainWindow.COL_FILE).text() == "a.pdf"
    from app.task_history import load_trash

    assert {r["name"] for r in load_trash()} == {"c.pdf", "b.pdf"}
    w.close()


def test_experiment_core_columns_hidden_rest():
    assert len(CORE_COLUMNS) == 9
    assert len(_CORE_COLS) == 9
    assert len(_TABLE_COLS) == 18


def test_experiment_dialog_builds():
    _app()
    dlg = ExperimentResultsDialog(roots=[Path("logs/experiment")])
    assert dlg.table.columnCount() == 18
    assert dlg.table.isColumnHidden(6)
    assert not dlg.table.isColumnHidden(0)
    dlg.cb_all_cols.setChecked(True)
    assert not dlg.table.isColumnHidden(6)
    dlg.close()


def test_formula_lab_default_table_cols():
    _app()
    dlg = FormulaBenchmarkDialog()
    assert dlg.table.columnCount() == 6
    assert dlg.notice_conflict.isHidden()
    dlg.close()


def test_help_dialog_builds():
    _app()
    dlg = HelpDialog()
    assert dlg.windowTitle() == "使用说明"
    joined = "\n".join(w.text() for w in dlg.findChildren(QLabel))
    for needle in (
        "第一次怎么用",
        "先选一条路线",
        "任务表怎么用",
        "中断、失败和重试",
        "run_gui.bat",
        "快速自动",
        "高保真视觉",
        "EPUB",
        "服务器繁忙",
        "不必拷到",
        "以往任务",
        "近的在上",
        "回收站",
        "删除选中",
        "多选",
        "图片质量",
        "Ctrl+Enter",
    ):
        assert needle in joined
    dlg.close()


def test_trash_dialog_builds(monkeypatch):
    monkeypatch.setattr("app.dialogs.trash_dialog.load_trash", lambda path=None: [])
    _app()
    from app.dialogs.trash_dialog import TrashDialog

    dlg = TrashDialog()
    assert dlg.windowTitle() == "回收站"
    assert dlg.table.columnCount() == 4
    assert dlg.table.rowCount() == 0
    assert dlg.table.isHidden()
    dlg.close()


def test_settings_nav_and_env_table():
    _app()
    dlg = SettingsDialog()
    assert dlg.nav.count() == 5
    assert dlg.stack.count() == 5
    assert dlg.env_table.columnCount() == 3
    assert not dlg.parallel.isEnabled()
    dlg.close()


def test_icons_resolve():
    for name in (
        "settings",
        "help",
        "log",
        "flask",
        "chart",
        "database",
        "more",
        "play",
        "stop",
        "lock",
        "folder",
        "file",
        "chevron-right",
        "trash",
    ):
        ico = icon(name)
        assert not ico.isNull(), name
