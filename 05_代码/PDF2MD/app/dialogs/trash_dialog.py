# -*- coding: utf-8 -*-
"""从主表删除的任务记录。恢复会放回主表；永久删除只清记录。"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.task_history import (
    load_trash,
    pop_trash,
    record_id,
    save_trash,
    sort_trash_newest_first,
)


class TrashDialog(QDialog):
    restore_record = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("回收站")
        self.resize(720, 460)
        root = QVBoxLayout(self)
        hint = QLabel(
            "从任务表删除的记录会出现在这里，近的在上。"
            "「恢复」放回主表最上面。「永久删除」只去掉这条记录，不删 output 里的文件。"
        )
        hint.setProperty("role", "muted")
        hint.setWordWrap(True)
        root.addWidget(hint)
        self.empty = QLabel("回收站是空的。")
        self.empty.setProperty("role", "muted")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.empty)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["文件", "状态", "方式", "删除时间"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 280)
        self.table.itemSelectionChanged.connect(self._sync_buttons)
        self.table.cellDoubleClicked.connect(lambda *_: self._restore())
        root.addWidget(self.table, 1)
        row = QHBoxLayout()
        self.btn_restore = QPushButton("恢复")
        self.btn_forget = QPushButton("永久删除")
        self.btn_empty = QPushButton("清空回收站")
        self.btn_restore.clicked.connect(self._restore)
        self.btn_forget.clicked.connect(self._forget)
        self.btn_empty.clicked.connect(self._empty)
        row.addWidget(self.btn_restore)
        row.addWidget(self.btn_forget)
        row.addWidget(self.btn_empty)
        row.addStretch(1)
        root.addLayout(row)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        close_btn = buttons.button(QDialogButtonBox.StandardButton.Close)
        if close_btn is not None:
            close_btn.setText("关闭")
        root.addWidget(buttons)
        self._reload()
        self._sync_buttons()

    def _reload(self) -> None:
        records = sort_trash_newest_first(load_trash())
        self.table.setRowCount(0)
        for rec in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            name = str(rec.get("name") or Path(str(rec.get("path") or "")).name)
            deleted = str(rec.get("deleted_at") or "")[:19].replace("T", " ")
            vals = [
                name,
                str(rec.get("status") or "—"),
                str(rec.get("engine") or rec.get("workflow") or "—"),
                deleted or "—",
            ]
            for col, text in enumerate(vals):
                item = QTableWidgetItem(text)
                if col == 0:
                    item.setData(Qt.ItemDataRole.UserRole, rec)
                    item.setToolTip(str(rec.get("path") or ""))
                self.table.setItem(row, col, item)
        empty = self.table.rowCount() == 0
        self.empty.setVisible(empty)
        self.table.setVisible(not empty)
        self._sync_buttons()

    def _selected_record(self) -> dict | None:
        rows = self.table.selectionModel().selectedRows(0)
        if not rows:
            return None
        item = self.table.item(rows[0].row(), 0)
        rec = item.data(Qt.ItemDataRole.UserRole) if item else None
        return rec if isinstance(rec, dict) else None

    def _sync_buttons(self) -> None:
        has = self._selected_record() is not None
        self.btn_restore.setEnabled(has)
        self.btn_forget.setEnabled(has)
        self.btn_empty.setEnabled(self.table.rowCount() > 0)

    def _restore(self) -> None:
        rec = self._selected_record()
        if not rec:
            return
        self.restore_record.emit(rec)
        self._reload()

    def _forget(self) -> None:
        rec = self._selected_record()
        if not rec:
            return
        try:
            pop_trash(record_id(rec))
        except OSError as e:
            QMessageBox.warning(self, "回收站", f"无法更新回收站：\n{e}")
            return
        self._reload()

    def _empty(self) -> None:
        if self.table.rowCount() == 0:
            return
        if (
            QMessageBox.question(
                self,
                "清空回收站",
                "永久去掉回收站里的全部记录？不删 output 里的文件。",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        try:
            save_trash([])
        except OSError as e:
            QMessageBox.warning(self, "回收站", f"无法清空回收站：\n{e}")
            return
        self._reload()
