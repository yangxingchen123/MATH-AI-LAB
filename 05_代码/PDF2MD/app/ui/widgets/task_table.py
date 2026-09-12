# -*- coding: utf-8 -*-
"""任务表：可接收 PDF / EPUB 拖入；表头按资源管理器方式拖分隔线。"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget

from app.drop_widget import dropped_input_paths


class ExplorerHeaderView(QHeaderView):
    """末列贴住视口右缘；分隔条命中区加宽，拖动手感接近资源管理器。"""

    EDGE = 8

    def __init__(self, orientation: Qt.Orientation, parent=None) -> None:
        super().__init__(orientation, parent)
        self.setMouseTracking(True)
        self.setSectionsClickable(True)
        self.setSectionsMovable(True)
        self.setFirstSectionMovable(False)
        self.setStretchLastSection(True)
        self.setCascadingSectionResizes(False)
        self.setHighlightSections(False)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._resize_logical: int | None = None
        self._resize_origin_x = 0
        self._resize_origin_w = 0

    def _event_x(self, event: QMouseEvent) -> int:
        try:
            return int(event.position().x())
        except Exception:
            return int(event.x())

    def _last_visible_visual(self) -> int:
        for vis in range(self.count() - 1, -1, -1):
            logical = self.logicalIndex(vis)
            if logical >= 0 and not self.isSectionHidden(logical):
                return vis
        return -1

    def handle_logical_at(self, x: int) -> int | None:
        """命中某列右缘分隔条时返回该列 logical index。最右列贴窗口，不提供右缘手柄。"""
        last_vis = self._last_visible_visual()
        for vis in range(self.count()):
            logical = self.logicalIndex(vis)
            if logical < 0 or self.isSectionHidden(logical):
                continue
            if vis == last_vis:
                continue
            if self.sectionResizeMode(logical) == QHeaderView.ResizeMode.Fixed:
                continue
            left = self.sectionViewportPosition(logical)
            right = left + self.sectionSize(logical)
            if abs(x - right) <= self.EDGE:
                return logical
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            logical = self.handle_logical_at(self._event_x(event))
            if logical is not None:
                self._resize_logical = logical
                self._resize_origin_x = self._event_x(event)
                self._resize_origin_w = self.sectionSize(logical)
                self.setCursor(Qt.CursorShape.SplitHCursor)
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        x = self._event_x(event)
        if self._resize_logical is not None:
            delta = x - self._resize_origin_x
            new_w = max(self.minimumSectionSize(), self._resize_origin_w + delta)
            self.resizeSection(self._resize_logical, new_w)
            return
        if event.buttons() == Qt.MouseButton.NoButton:
            if self.handle_logical_at(x) is not None:
                self.setCursor(Qt.CursorShape.SplitHCursor)
            else:
                self.unsetCursor()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._resize_logical = None
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        if self._resize_logical is None:
            self.unsetCursor()
        super().leaveEvent(event)


class FileDropTableWidget(QTableWidget):
    files_dropped = Signal(list)
    layout_needed = Signal()

    def __init__(self, rows: int = 0, columns: int = 0, parent=None) -> None:
        super().__init__(rows, columns, parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.setHorizontalHeader(ExplorerHeaderView(Qt.Orientation.Horizontal, self))

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

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.layout_needed.emit()
