# -*- coding: utf-8 -*-
"""识别 · 公式选项：档位、DeepSeek，以及写回规则说明。"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.ui.identity import formula_profile_tone
from app.ui.widgets.notice import Notice
from app.ui.widgets.status_badge import StatusBadge


class FormulaOptionsDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None,
        *,
        cmb_formula_recovery: QComboBox,
        cb_formulas: QCheckBox,
        cb_deepseek_lp: QCheckBox,
        identity_label: QLabel,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("识别 · 公式选项")
        self.setModal(True)
        self.resize(520, 500)
        root = QVBoxLayout(self)
        root.setSpacing(12)

        head = QLabel("当前配置身份")
        head.setProperty("role", "sectionTitle")
        root.addWidget(head)
        identity_label.setWordWrap(True)
        root.addWidget(identity_label)
        self.badge = StatusBadge("Lean Balanced", "info")
        root.addWidget(self.badge)

        row_cap = QLabel("公式恢复档位")
        row_cap.setProperty("role", "muted")
        root.addWidget(row_cap)
        root.addWidget(cmb_formula_recovery)
        gear_hint = QLabel(
            "「均衡」：日常推荐，勾 DeepSeek 后会关掉 Docling enrich。"
            "「精细」：裁图更大、可同时勾 DeepSeek 和 enrich（更慢）。"
            "「快速」几乎不跑公式 OCR，勾 DeepSeek 会改回均衡。"
        )
        gear_hint.setProperty("role", "subtle")
        gear_hint.setWordWrap(True)
        root.addWidget(gear_hint)

        cb_deepseek_lp.setEnabled(True)
        cb_deepseek_lp.setMinimumHeight(32)
        cb_deepseek_lp.setToolTip(
            "勾选即开启 DeepSeek 公式恢复。均衡、精细都可以用；"
            "若当前是「快速」，会自动改到均衡。"
            "仅对受控 crop 做恢复；不承诺全公式正确。需本机 GPU。"
        )
        root.addWidget(cb_deepseek_lp)
        hint_ds = QLabel(
            "均衡或精细下直接勾选。快速档没有公式 OCR 预算，勾上会改回均衡。"
        )
        hint_ds.setProperty("role", "subtle")
        hint_ds.setWordWrap(True)
        root.addWidget(hint_ds)
        self._cb_deepseek = cb_deepseek_lp

        cb_formulas.setToolTip(
            "开启后 Docling 跑公式 enrich（很慢）。"
            "Lean Balanced 默认关闭，由 DeepSeek crop 主修公式。"
        )
        root.addWidget(cb_formulas)
        hint_en = QLabel(
            "Docling 再跑一遍公式结构，很慢。均衡+DeepSeek 时默认关；精细可以一起开。"
        )
        hint_en.setProperty("role", "subtle")
        hint_en.setWordWrap(True)
        root.addWidget(hint_en)

        root.addWidget(
            Notice(
                "写回规则",
                "这不是报错。恢复公式时以版面上裁好的那条为准："
                "OCR 结果若和原式对不上（周围文字被读成公式等），会丢掉这次识别，"
                "不会凭上下文编一条新公式。",
                tone="info",
            )
        )

        buttons = QDialogButtonBox()
        done = buttons.addButton("完成", QDialogButtonBox.ButtonRole.AcceptRole)
        done.clicked.connect(self.accept)
        root.addStretch(1)
        root.addWidget(buttons)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        cb = getattr(self, "_cb_deepseek", None)
        if cb is not None:
            cb.setEnabled(True)

    def set_identity(self, name: str) -> None:
        suffix = "　Recommended" if name == "Lean Balanced" else ""
        self.badge.set_status(name + suffix, formula_profile_tone(name))
