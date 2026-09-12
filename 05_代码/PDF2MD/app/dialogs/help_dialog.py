# -*- coding: utf-8 -*-
"""主窗口使用说明：只写日常转稿会用到的步骤。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.notice import Notice
from app.ui.widgets.section_card import SectionCard

_SECTIONS: tuple[tuple[str, str], ...] = (
    (
        "第一次怎么用",
        "1. 双击 run_gui.bat 打开（不会挂空控制台）。\n"
        "2. 顶部保持「快速自动」。把 PDF 或 EPUB 拖到左侧投放区，也可以拖到下面的任务表。\n"
        "3. 导出目录保持项目里的 output，不要指到桌面 PDFTomd。\n"
        "4. 点底部「开始转换」。页列会出现 128/392 这样的进度。\n"
        "5. 完成后点任务行的文件图标打开 Markdown，或右键「打开文件夹」。",
    ),
    (
        "先选一条路线",
        "日常转论文、课本用「快速自动」，几秒到几分钟就能出 Markdown。\n"
        "版式很乱、必须尽量对齐原稿时，再切「高保真视觉」。两条路线互不影响，"
        "高保真结果在「论文名_高保真」文件夹，不会覆盖快速自动的成品。",
    ),
    (
        "快速自动",
        "1. 顶部保持「快速自动」，拖入或点击添加 PDF。\n"
        "2. 要修公式：点识别旁的「…」，档位选「均衡」，勾上「DeepSeek 高置信公式恢复」。\n"
        "3. 第一次加载公式模型可能要几分钟，之后会复用。请抽查公式后再用。\n"
        "4. 右侧「图片质量」默认「标准」(2×)，一般够用。「高清」(3×) 更清晰但更慢。",
    ),
    (
        "高保真视觉",
        "1. 切到「高保真视觉」，拖入 PDF，点「开始转换」。\n"
        "2. 弹出浏览器后登录 DeepSeek，不要关那个窗口。\n"
        "3. 整页图的渲染倍率跟随右侧「图片质量」。\n"
        "4. 已渲好图只想重排版：右键任务 →「仅重合并与裁图」（不重跑浏览器）。",
    ),
    (
        "EPUB",
        "同一拖放区也可加入 .epub。按书籍目录顺序转成一份 Markdown，"
        "不走 Docling / 公式 OCR / 高保真视觉。加密（DRM）的 EPUB 会明确失败。",
    ),
    (
        "文件放哪",
        "PDF / EPUB 可以留在课本文件夹，直接拖进来，不必拷到项目里的 input。\n"
        "成品只写到本项目 output（每本书一个子文件夹）。\n"
        "任务表就是以往任务：近的在上，远的在下；再拖一本新的会插到最上面。",
    ),
    (
        "任务表怎么用",
        "左侧小方框可以多选：逐个勾，或按住 Ctrl / Shift 点文件名。\n"
        "「开始转换」会转表里所有待转文件，不只转勾选的那几本。"
        "已完成的不会自动重跑，以免覆盖上次结果。\n"
        "「删除选中」（或按 Delete）把勾上的任务移到回收站；"
        "「清空列表」把当前表里全部移到回收站。都不删 output 里的文件。\n"
        "回收站在任务表右上角。可「恢复」（放回表的最上面）或「永久删除」（只去掉记录）。",
    ),
    (
        "中断、失败和重试",
        "「取消」或关窗口会停在当前批次边界，已完成的页会留下。\n"
        "再点「开始转换」或行上的「继续」，从上次页码接着转，不会整本重来。\n"
        "失败、取消后也可以点「继续」。操作列或右键的「重试」才会从头再转。"
        "快速自动里还可以右键「使用 MinerU 重新转换」。",
    ),
    (
        "其它按钮和快捷键",
        "右键还可「打开 Markdown / 文件夹」「查看错误」。\n"
        "「复制为 Markdown」把当前任务表拷到剪贴板。\n"
        "快捷键：开始 Ctrl+Enter，取消 Esc，本说明 F1，设置 Ctrl+,，日志 Ctrl+L。",
    ),
)


def _body(text: str) -> QLabel:
    lab = QLabel(text)
    lab.setWordWrap(True)
    lab.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    lab.setProperty("role", "muted")
    return lab


class HelpDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("使用说明")
        self.resize(560, 680)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 12)
        root.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        pane = QWidget()
        lay = QVBoxLayout(pane)
        lay.setContentsMargins(0, 0, 4, 0)
        lay.setSpacing(12)

        for title, text in _SECTIONS:
            card = SectionCard(title)
            card.body.addWidget(_body(text))
            if title == "高保真视觉":
                card.body.addWidget(
                    Notice(
                        "服务器繁忙",
                        "上传整页图时若出现「服务器繁忙」，是 DeepSeek 账户限流，刷新没用。"
                        "程序会暂停大约 10 分钟再自动续跑。",
                        tone="warning",
                    )
                )
            lay.addWidget(card)

        lay.addStretch(1)
        scroll.setWidget(pane)
        root.addWidget(scroll, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        close_btn = buttons.button(QDialogButtonBox.StandardButton.Close)
        if close_btn is not None:
            close_btn.setText("关闭")
            close_btn.setDefault(True)
        root.addWidget(buttons)
