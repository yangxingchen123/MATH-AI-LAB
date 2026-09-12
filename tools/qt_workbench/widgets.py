"""Small visual widgets for the Qt workbench."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class ObjectRow(QFrame):
    def __init__(self, list_widget, item, oid: str, title: str, group: str = "") -> None:
        super().__init__()
        self._list = list_widget
        self._item = item
        self.setObjectName("objectRow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setProperty("selected", False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(2)
        ident = QLabel(oid)
        ident.setObjectName("idText")
        heading = QLabel(title)
        heading.setObjectName("rowTitle")
        heading.setWordWrap(True)
        layout.addWidget(ident)
        layout.addWidget(heading)
        if group:
            meta = QLabel(group)
            meta.setObjectName("rowMeta")
            layout.addWidget(meta)

    def mousePressEvent(self, event) -> None:  # noqa: ANN001
        self._list.setCurrentItem(self._item)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)


class CountCard(QFrame):
    chosen = Signal(str)

    def __init__(self, kind: str, name: str, value: int) -> None:
        super().__init__()
        self.kind = kind
        self.setObjectName("countCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(108)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        number = QLabel(str(value))
        number.setObjectName("countValue")
        label = QLabel(name)
        label.setObjectName("countName")
        layout.addWidget(number)
        layout.addWidget(label)

    def mousePressEvent(self, event) -> None:  # noqa: ANN001
        self.chosen.emit(self.kind)
        super().mousePressEvent(event)


class Chip(QLabel):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setObjectName("chip")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setContentsMargins(10, 4, 10, 4)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


def form_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("formLabel")
    return label


def status_badge(text: str, tone: str = "idle") -> QLabel:
    badge = QLabel(text)
    badge.setObjectName("statusBadge")
    badge.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    badge.setProperty("tone", tone)
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return badge


def apply_tone(widget: QLabel, tone: str, text: str | None = None) -> None:
    if text is not None:
        widget.setText(text)
    widget.setProperty("tone", tone)
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def section_card(
    kicker: str,
    title: str,
    lead: str,
    extra: QWidget | None = None,
) -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setObjectName("settingsCard")
    card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(8)
    kick = QLabel(kicker)
    kick.setObjectName("sectionKicker")
    heading = QLabel(title)
    heading.setObjectName("cardTitle")
    head = QHBoxLayout()
    head.setContentsMargins(0, 0, 0, 0)
    head.addWidget(heading, 1)
    if extra is not None:
        head.addWidget(extra, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    note = QLabel(lead)
    note.setObjectName("mutedLabel")
    note.setWordWrap(True)
    layout.addWidget(kick)
    layout.addLayout(head)
    layout.addWidget(note)
    return card, layout


def chip_row(texts: list[str]) -> QWidget:
    box = QWidget()
    layout = QHBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    for text in texts:
        layout.addWidget(Chip(text), 0)
    layout.addStretch(1)
    return box
