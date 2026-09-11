"""文档拖放区域（PDF / EPUB）。"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from app.formats import iter_input_files


def dropped_input_paths(mime) -> list[str]:
    """从拖放 mime 里取出可入队的 PDF / EPUB 路径。"""
    if mime is None or not mime.hasUrls():
        return []
    out: list[str] = []
    seen: set[str] = set()
    for url in mime.urls():
        local = url.toLocalFile()
        if not local:
            continue
        for p in iter_input_files(Path(local)):
            key = str(p)
            if key in seen:
                continue
            seen.add(key)
            out.append(key)
    return out


class DropWidget(QFrame):
    files_dropped = Signal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._compact = False

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title = QLabel("拖入 PDF / EPUB")
        self.title.setProperty("role", "sectionTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label = QLabel("支持多文件 / 文件夹 · 或点击选择。不必拷到 input")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setProperty("role", "muted")
        layout.addWidget(self.title)
        layout.addWidget(self.label)
        self.set_compact(False)

    def set_compact(self, compact: bool) -> None:
        self._compact = compact
        if compact:
            self.setMinimumHeight(56)
            self.setMaximumHeight(64)
            self.title.setText("继续添加 PDF / EPUB")
            self.label.hide()
        else:
            self.setMaximumHeight(16777215)
            self.setMinimumHeight(148)
            self.title.setText("拖入 PDF / EPUB")
            self.label.setText("支持多文件 / 文件夹 · 或点击选择。不必拷到 input")
            self.label.show()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.files_dropped.emit([])  # 空列表 = 打开文件对话框
        super().mousePressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if dropped_input_paths(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:  # noqa: N802
        if dropped_input_paths(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        paths = dropped_input_paths(event.mimeData())
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            event.ignore()
