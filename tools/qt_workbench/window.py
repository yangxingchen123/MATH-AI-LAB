"""Qt main window. No localhost, no browser."""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from typing import Any

from PySide6.QtCore import QSize, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QCloseEvent, QColor, QFont, QKeySequence, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from tools.studio.catalog import get_document
from tools.ui_operations.documents import EDITABLE_TYPES
from tools.ui_operations.gateway import run_operation

from .ai_prefs import flattened_choices, load_prefs, models_for, providers, save_prefs, selection_label
from .doctor import doctor
from .gpt_client import chat_from_root, connect_gpt, gpt_models, gpt_status
from .nav import FILE_KINDS, HOME_ITEM, NAV_GROUPS, STUDIO_KINDS
from .panels import CREATE_SPECS, CreateObjectDialog, build_action_panel
from .reader import MarkdownReader
from .style import DARK, DARK_QSS, LIGHT, LIGHT_QSS
from .widgets import CountCard, ObjectRow, apply_tone, chip_row, form_label, section_card, status_badge
from .workspace import KIND_LABELS, get_object, list_objects, snapshot

KIND_TITLES = {
    "home": "工作台",
    "knowledge": "知识",
    "problem": "题目",
    "method": "方法",
    "project": "研究",
    "references": "参考",
    "outputs": "成果",
    "memory": "记忆",
    "inbox": "收件箱",
    "prompts": "提示词",
    "lean": "Lean",
    "lab": "Lab",
    "universe": "宇宙",
    "exploration": "探索",
    "settings": "设置",
}

SETTINGS_SECTIONS = (
    {"id": "prefs", "title": "模型偏好", "group": "本机"},
    {"id": "gpt", "title": "接入 GPT", "group": "本机"},
    {"id": "chat", "title": "对话", "group": "本机"},
)


class _GptJob(QThread):
    finished_result = Signal(str, object)

    def __init__(self, kind: str, root: Path, payload: dict[str, Any]) -> None:
        super().__init__()
        self.kind = kind
        self.root = Path(root)
        self.payload = payload

    def run(self) -> None:
        try:
            if self.kind == "connect":
                result = connect_gpt(self.root, **self.payload)
            else:
                result = chat_from_root(self.root, **self.payload)
        except Exception as exc:  # UI sidecar: show any failure in the panel
            result = {"ok": False, "error": str(exc)}
        self.finished_result.emit(self.kind, result)


class MainWindow(QMainWindow):
    def __init__(self, root: Path) -> None:
        super().__init__()
        self.root = Path(root)
        self.dark = True
        self.current_kind = "home"
        self.current_objects: list[dict[str, Any]] = []
        self._edit_ctx: dict[str, Any] | None = None
        self._syncing_editor = False
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(280)
        self._preview_timer.timeout.connect(self._refresh_reading_from_editor)
        self._gpt_job: _GptJob | None = None
        self._gpt_messages: list[dict[str, str]] = []
        self.setWindowTitle("MATH-AI-LAB")
        self.resize(1320, 840)
        self.setMinimumSize(1000, 640)
        self._build()
        self._apply_theme()
        self._refresh_gpt_chrome()
        self._open_home()

    def _build(self) -> None:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        sidebar.setFixedWidth(232)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 18, 16, 14)
        side.setSpacing(0)
        mark = QLabel("MATH-AI-LAB")
        mark.setObjectName("brandMark")
        name = QLabel("工作台")
        name.setObjectName("brandName")
        hint = QLabel("进程内 · 可操作")
        hint.setObjectName("brandHint")
        side.addWidget(mark)
        side.addSpacing(2)
        side.addWidget(name)
        side.addWidget(hint)
        side.addSpacing(16)
        self.nav = QTreeWidget()
        self.nav.setHeaderHidden(True)
        self.nav.setIndentation(14)
        self.nav.setRootIsDecorated(False)
        self.nav.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.nav.setMouseTracking(True)
        self.nav.setUniformRowHeights(True)
        self._fill_nav()
        self.nav.itemClicked.connect(self._on_nav)
        side.addWidget(self.nav, 1)

        list_pane = QFrame()
        list_pane.setObjectName("listPane")
        list_pane.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        list_pane.setMinimumWidth(268)
        list_layout = QVBoxLayout(list_pane)
        list_layout.setContentsMargins(14, 16, 14, 10)
        list_layout.setSpacing(8)
        heading_row = QHBoxLayout()
        self.list_title = QLabel("对象")
        self.list_title.setObjectName("listHeading")
        self.list_count = QLabel("")
        self.list_count.setObjectName("listCount")
        heading_row.addWidget(self.list_title)
        heading_row.addStretch(1)
        heading_row.addWidget(self.list_count)
        self.create_btn = QPushButton("新建")
        self.create_btn.setObjectName("ghostButton")
        self.create_btn.setVisible(False)
        self.create_btn.clicked.connect(self._create_object)
        heading_row.addWidget(self.create_btn)
        self.search = QLineEdit()
        self.search.setObjectName("searchField")
        self.search.setPlaceholderText("过滤 ID 或标题")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter_objects)
        self.objects = QListWidget()
        self.objects.setSpacing(0)
        self.objects.setUniformItemSizes(False)
        self.objects.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.objects.currentItemChanged.connect(self._on_object)
        list_layout.addLayout(heading_row)
        list_layout.addWidget(self.search)
        list_layout.addWidget(self.objects, 1)

        reader = QFrame()
        reader.setObjectName("reader")
        reader.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        reader_layout = QVBoxLayout(reader)
        reader_layout.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        self.home_panel = self._build_home_panel()
        self.doc_panel = self._build_doc_panel()
        self.settings_panel = self._build_settings_panel()
        self.stack.addWidget(self.home_panel)
        self.stack.addWidget(self.doc_panel)
        self.stack.addWidget(self.settings_panel)
        reader_layout.addWidget(self.stack)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(sidebar)
        splitter.addWidget(list_pane)
        splitter.addWidget(reader)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 0)
        splitter.setStretchFactor(2, 1)
        splitter.setSizes([220, 288, 812])

        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        top = QHBoxLayout(topbar)
        top.setContentsMargins(16, 10, 16, 10)
        top.setSpacing(10)
        brand = QLabel("MATH-AI-LAB")
        brand.setObjectName("brandMark")
        self.top_context = QLabel("工作台")
        self.top_context.setObjectName("topContext")
        top.addWidget(brand)
        top.addWidget(self.top_context)
        top.addStretch(1)
        self.save_btn = QPushButton("保存正文")
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save)
        self.model_combo = QComboBox()
        self.model_combo.setObjectName("modelCombo")
        self.model_combo.setToolTip("选择工作台使用的模型。接入 GPT 请打开设置，填写 API Key。")
        self._model_sync = False
        self._fill_model_combo()
        self.model_combo.currentIndexChanged.connect(self._on_top_model_changed)
        self.gpt_top_badge = status_badge("GPT 未接入", "idle")
        self.theme_btn = QPushButton("浅色")
        self.theme_btn.setObjectName("ghostButton")
        self.theme_btn.clicked.connect(self._toggle_theme)
        top.addWidget(self.save_btn)
        top.addWidget(self.model_combo)
        top.addWidget(self.gpt_top_badge)
        top.addWidget(self.theme_btn)

        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(topbar)
        shell_layout.addWidget(splitter, 1)
        self.setCentralWidget(shell)
        status = QStatusBar()
        status.setSizeGripEnabled(False)
        status.showMessage(f"仓库  {self.root}  ·  进程内读取  ·  无 HTTP 端口")
        self.setStatusBar(status)

        find = QAction("查找", self)
        find.setShortcut(QKeySequence.StandardKey.Find)
        find.triggered.connect(self.search.setFocus)
        self.addAction(find)
        save = QAction("保存正文", self)
        save.setShortcut(QKeySequence.StandardKey.Save)
        save.triggered.connect(self._save)
        self.addAction(save)

    def _build_home_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("homePanel")
        panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(36, 28, 36, 24)
        layout.setSpacing(8)
        kicker = QLabel("工作台")
        kicker.setObjectName("sectionKicker")
        title = QLabel("今天只打开需要的对象")
        title.setObjectName("titleLabel")
        title.setWordWrap(True)
        lead = QLabel("从左侧进入知识、题目、方法或研究。题目可在「操作」里记录 Attempt、移动工作流目录；新建走 Domain Operation。")
        lead.setObjectName("mutedLabel")
        lead.setWordWrap(True)
        self.home_cards = QWidget()
        self.home_grid = QGridLayout(self.home_cards)
        self.home_grid.setContentsMargins(0, 12, 0, 8)
        self.home_grid.setHorizontalSpacing(10)
        self.home_grid.setVerticalSpacing(10)
        self.home_brief = MarkdownReader()
        layout.addWidget(kicker)
        layout.addWidget(title)
        layout.addWidget(lead)
        layout.addWidget(self.home_cards)
        layout.addWidget(self.home_brief, 1)
        return panel

    def _build_doc_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("docPanel")
        panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(36, 28, 36, 16)
        layout.setSpacing(8)
        self.kicker = QLabel()
        self.kicker.setObjectName("sectionKicker")
        self.title_label = QLabel()
        self.title_label.setObjectName("titleLabel")
        self.title_label.setWordWrap(True)
        self.meta = QLabel()
        self.meta.setObjectName("pathLabel")
        self.meta.setWordWrap(True)
        self.chip_host = QWidget()
        self.chip_layout = QHBoxLayout(self.chip_host)
        self.chip_layout.setContentsMargins(0, 4, 0, 8)
        self.chip_layout.setSpacing(8)
        self.status_pair = QLabel()
        self.status_pair.setObjectName("mutedLabel")
        self.status_pair.setWordWrap(True)
        self.status_pair.hide()
        self.edit_hint = QLabel("源码只改正文。YAML Front Matter、对象 ID 与 status 不在此编辑。")
        self.edit_hint.setObjectName("editHint")
        self.edit_hint.setWordWrap(True)
        self.body = MarkdownReader()
        self.editor = QPlainTextEdit()
        self.editor.setObjectName("sourceEditor")
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.editor.setTabStopDistance(32)
        self.editor.textChanged.connect(self._on_editor_changed)
        self.actions_scroll = QScrollArea()
        self.actions_scroll.setObjectName("actionScroll")
        self.actions_scroll.setWidgetResizable(True)
        self.actions_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.actions_host = QWidget()
        self.actions_layout = QVBoxLayout(self.actions_host)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_scroll.setWidget(self.actions_host)
        self.doc_tabs = QTabWidget()
        self.doc_tabs.addTab(self.body, "阅读")
        self.doc_tabs.addTab(self.editor, "源码")
        self.doc_tabs.addTab(self.actions_scroll, "操作")
        layout.addWidget(self.kicker)
        layout.addWidget(self.title_label)
        layout.addWidget(self.meta)
        layout.addWidget(self.chip_host)
        layout.addWidget(self.status_pair)
        layout.addWidget(self.edit_hint)
        layout.addWidget(self.doc_tabs, 1)
        return panel

    def _build_settings_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("docPanel")
        panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        scroll = QScrollArea()
        scroll.setObjectName("actionScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.settings_scroll = scroll
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(32, 24, 32, 28)
        layout.setSpacing(14)

        kicker = QLabel("本机")
        kicker.setObjectName("sectionKicker")
        title = QLabel("设置")
        title.setObjectName("titleLabel")
        lead = QLabel("模型偏好与 GPT 接入都只留在这台电脑，不进仓库，也不写正式知识库。")
        lead.setObjectName("mutedLabel")
        lead.setWordWrap(True)

        self.settings_provider = QComboBox()
        self.settings_provider.setObjectName("settingsCombo")
        self.settings_model = QComboBox()
        self.settings_model.setObjectName("settingsCombo")
        self.settings_custom = QLineEdit()
        self.settings_custom.setObjectName("customModel")
        self.settings_custom.setPlaceholderText("例如 llama3.1:70b")
        prefs_form = QFormLayout()
        prefs_form.setContentsMargins(0, 8, 0, 4)
        prefs_form.setSpacing(8)
        prefs_form.setHorizontalSpacing(14)
        prefs_form.addRow(form_label("提供方"), self.settings_provider)
        prefs_form.addRow(form_label("模型"), self.settings_model)
        prefs_form.addRow(form_label("自定义"), self.settings_custom)
        save = QPushButton("保存选择")
        save.setObjectName("primaryButton")
        save.clicked.connect(self._save_settings_model)
        self.settings_status = QLabel()
        self.settings_status.setObjectName("mutedLabel")
        self.settings_status.setWordWrap(True)
        self.settings_provider.currentIndexChanged.connect(self._on_settings_provider_changed)
        self.settings_model.currentIndexChanged.connect(self._on_settings_model_changed)
        prefs_card, prefs_body = section_card(
            "偏好",
            "模型",
            "顶栏会同步这里的选择。Cursor 对话仍在 Cursor 输入框旁选模型。",
        )
        prefs_body.addLayout(prefs_form)
        prefs_actions = QHBoxLayout()
        prefs_actions.addWidget(save, 0, Qt.AlignmentFlag.AlignLeft)
        prefs_actions.addWidget(self.settings_status, 1)
        prefs_body.addLayout(prefs_actions)

        self.gpt_badge = status_badge("未接入", "idle")
        self.settings_gpt_model = QComboBox()
        self.settings_gpt_model.setObjectName("settingsCombo")
        self.settings_api_key = QLineEdit()
        self.settings_api_key.setObjectName("customModel")
        self.settings_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.settings_api_key.setPlaceholderText("粘贴 sk- 开头的 API Key")
        self.settings_base_url = QLineEdit()
        self.settings_base_url.setObjectName("customModel")
        self.settings_base_url.setPlaceholderText("https://api.openai.com/v1")
        gpt_grid = QGridLayout()
        gpt_grid.setContentsMargins(0, 8, 0, 4)
        gpt_grid.setHorizontalSpacing(12)
        gpt_grid.setVerticalSpacing(8)
        gpt_grid.addWidget(form_label("GPT 模型"), 0, 0)
        gpt_grid.addWidget(form_label("Base URL"), 0, 1)
        gpt_grid.addWidget(self.settings_gpt_model, 1, 0)
        gpt_grid.addWidget(self.settings_base_url, 1, 1)
        gpt_grid.addWidget(form_label("API Key"), 2, 0, 1, 2)
        gpt_grid.addWidget(self.settings_api_key, 3, 0, 1, 2)
        self.gpt_connect_btn = QPushButton("接入 GPT")
        self.gpt_connect_btn.setObjectName("primaryButton")
        self.gpt_connect_btn.clicked.connect(self._connect_gpt)
        self.gpt_connect_status = QLabel()
        self.gpt_connect_status.setObjectName("statusNote")
        self.gpt_connect_status.setWordWrap(True)
        gpt_card, gpt_body = section_card(
            "连接",
            "接入 GPT",
            "填写 OpenAI Key。兼容中转可改 Base URL。密钥写入 .mathailab/credentials.json。",
            extra=self.gpt_badge,
        )
        gpt_body.addLayout(gpt_grid)
        gpt_actions = QHBoxLayout()
        gpt_actions.addWidget(self.gpt_connect_btn, 0, Qt.AlignmentFlag.AlignLeft)
        gpt_actions.addWidget(self.gpt_connect_status, 1)
        gpt_body.addLayout(gpt_actions)

        self.gpt_transcript = QPlainTextEdit()
        self.gpt_transcript.setObjectName("gptTranscript")
        self.gpt_transcript.setReadOnly(True)
        self.gpt_transcript.setMinimumHeight(200)
        self.gpt_transcript.setPlaceholderText("接入后在这里对话。")
        composer = QFrame()
        composer.setObjectName("composerBar")
        composer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        prompt_row = QHBoxLayout(composer)
        prompt_row.setContentsMargins(4, 4, 6, 4)
        prompt_row.setSpacing(6)
        self.gpt_prompt = QLineEdit()
        self.gpt_prompt.setObjectName("gptPrompt")
        self.gpt_prompt.setPlaceholderText("问 GPT…")
        self.gpt_prompt.returnPressed.connect(self._send_gpt)
        self.gpt_send_btn = QPushButton("发送")
        self.gpt_send_btn.setObjectName("primaryButton")
        self.gpt_send_btn.clicked.connect(self._send_gpt)
        prompt_row.addWidget(self.gpt_prompt, 1)
        prompt_row.addWidget(self.gpt_send_btn)
        chat_card, chat_body = section_card("对话", "GPT", "发送内容只走本机 sidecar，不写正式 Source。")
        chat_body.addWidget(self.gpt_transcript, 1)
        chat_body.addWidget(composer)

        self.settings_meta = QLabel()
        self.settings_meta.setObjectName("mutedLabel")
        self.settings_meta.setWordWrap(True)

        layout.addWidget(kicker)
        layout.addWidget(title)
        layout.addWidget(lead)
        layout.addWidget(prefs_card)
        layout.addWidget(gpt_card)
        layout.addWidget(chat_card, 1)
        layout.addWidget(self.settings_meta)
        self.settings_cards = {"prefs": prefs_card, "gpt": gpt_card, "chat": chat_card}
        scroll.setWidget(inner)
        outer.addWidget(scroll)
        return panel

    def _fill_nav(self) -> None:
        home = QTreeWidgetItem([HOME_ITEM["label"]])
        home.setData(0, Qt.ItemDataRole.UserRole, HOME_ITEM)
        self.nav.addTopLevelItem(home)
        for group in NAV_GROUPS:
            parent = QTreeWidgetItem([group["label"]])
            parent.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = QFont(parent.font(0))
            font.setPointSize(10)
            font.setBold(True)
            font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.8)
            parent.setFont(0, font)
            for item in group["items"]:
                child = QTreeWidgetItem([item["label"]])
                child.setData(0, Qt.ItemDataRole.UserRole, item)
                if not item.get("enabled", True):
                    child.setDisabled(True)
                    child.setToolTip(0, "尚未开放")
                parent.addChild(child)
            parent.setExpanded(True)
            self.nav.addTopLevelItem(parent)
        self.nav.setCurrentItem(home)

    def _apply_theme(self) -> None:
        tokens = DARK if self.dark else LIGHT
        self.setStyleSheet(DARK_QSS if self.dark else LIGHT_QSS)
        self.theme_btn.setText("浅色" if self.dark else "深色")
        muted = QColor(tokens["faint"])
        for index in range(self.nav.topLevelItemCount()):
            top = self.nav.topLevelItem(index)
            data = top.data(0, Qt.ItemDataRole.UserRole)
            if not isinstance(data, dict):
                top.setForeground(0, muted)

    def _toggle_theme(self) -> None:
        self.dark = not self.dark
        self._apply_theme()
        self._refresh_row_selection()
        self.home_brief.set_markdown(self.home_brief.source, dark=self.dark)
        self.body.set_markdown(self.body.source, dark=self.dark)

    def _on_nav(self, item: QTreeWidgetItem, _column: int) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, dict):
            return
        if not self._confirm_leave():
            self._select_nav_kind(self.current_kind)
            return
        if not data.get("enabled", True):
            self._show_message(data.get("label") or "未开放", "Research Intelligence 尚未开放。先使用工作台阅读现有对象。")
            return
        kind = str(data.get("kind") or "")
        if kind == "home":
            self._open_home()
        elif kind == "universe":
            self._open_universe()
        elif kind == "exploration":
            self._open_section("exploration")
        elif kind == "settings":
            self._open_settings()
        else:
            self._open_section(kind)

    def _open_home(self) -> None:
        self.current_kind = "home"
        self.list_title.setText("今日")
        self.search.setPlaceholderText("过滤 ID 或标题")
        brief = get_document(self.root, "today", "brief") or {}
        data = snapshot(self.root)
        counts = data["counts"]
        self._set_list([{"id": "brief", "title": "今日简报", "group": "索引"}])
        self._fill_home_cards(counts)
        body = str(brief.get("body") or "")
        self.home_brief.set_markdown(body, dark=self.dark)
        self.stack.setCurrentWidget(self.home_panel)
        self.create_btn.setVisible(False)
        self._clear_edit_ctx()
        self.top_context.setText("工作台")

    def _fill_home_cards(self, counts: dict[str, int]) -> None:
        while self.home_grid.count():
            taken = self.home_grid.takeAt(0)
            widget = taken.widget()
            if widget is not None:
                widget.deleteLater()
        cards = [
            ("knowledge", "知识", counts["knowledge"]),
            ("problem", "题目", counts["problems"]),
            ("method", "方法", counts["methods"]),
            ("project", "研究", counts["projects"]),
            ("lab", "Lab", counts["lab"]),
        ]
        for index, (kind, name, value) in enumerate(cards):
            card = CountCard(kind, name, value)
            card.chosen.connect(self._open_section)
            self.home_grid.addWidget(card, 0, index)

    def _open_universe(self) -> None:
        self.current_kind = "universe"
        self.list_title.setText("宇宙")
        self.search.setPlaceholderText("过滤 ID 或标题")
        self.create_btn.setVisible(False)
        self._set_list([])
        self._show_document(
            {
                "title": "数学宇宙（投影）",
                "kind_label": "只读投影",
                "path": "packages/domain-math",
                "body": (
                    "宇宙层是运行时投影，不是新 YAML，也不是数据库。\n\n"
                    "- Knowledge → Definition，不是 Theorem\n"
                    "- Problem → Question\n"
                    "- Lab → Candidate，不能自动升级\n"
                    "- 过程层见侧栏「探索」：观察、失败、下一步；仍不写 Canonical\n"
                    "- 本窗口直接读仓库对象\n"
                ),
            }
        )

    def _open_settings(self) -> None:
        self.current_kind = "settings"
        self.list_title.setText("设置")
        self.create_btn.setVisible(False)
        self.search.setPlaceholderText("过滤设置项")
        self._set_list(list(SETTINGS_SECTIONS))
        self._clear_edit_ctx()
        self._load_settings_form()
        self.stack.setCurrentWidget(self.settings_panel)
        self.top_context.setText("设置  ·  本机")
        report = doctor()
        self.settings_meta.setText(
            f"Qt 窗口 · {report['transport']} · 无 HTTP · PySide6 {report['pyside_version'] or '未安装'}"
        )
        self.objects.blockSignals(True)
        self.objects.setCurrentRow(0)
        self.objects.blockSignals(False)
        self._refresh_row_selection()

    def _fill_model_combo(self) -> None:
        prefs = load_prefs(self.root)
        self._model_sync = True
        self.model_combo.clear()
        selected = 0
        for index, (provider, model, label) in enumerate(flattened_choices()):
            self.model_combo.addItem(label, {"provider": provider, "model": model})
            if provider == prefs["provider"] and (
                provider == "custom" or model == prefs["model"]
            ):
                selected = index
        self.model_combo.setCurrentIndex(selected)
        self._model_sync = False

    def _on_top_model_changed(self, _index: int) -> None:
        if self._model_sync:
            return
        data = self.model_combo.currentData()
        if not isinstance(data, dict):
            return
        provider = str(data.get("provider") or "")
        model = str(data.get("model") or "")
        current = load_prefs(self.root)
        if provider == "custom":
            save_prefs(
                self.root,
                {
                    "provider": "custom",
                    "custom_model": current.get("custom_model") or "",
                },
            )
        else:
            save_prefs(self.root, {"provider": provider, "model": model})
        self._load_settings_form()
        label = selection_label(load_prefs(self.root))
        self.statusBar().showMessage(f"已选择 AI 模型  {label}  ·  仓库  {self.root}  ·  无 HTTP 端口")

    def _load_settings_form(self) -> None:
        prefs = load_prefs(self.root)
        self._model_sync = True
        self.settings_provider.blockSignals(True)
        self.settings_model.blockSignals(True)
        self.settings_provider.clear()
        for row in providers():
            self.settings_provider.addItem(str(row["label"]), row["id"])
        provider_index = max(
            0,
            self.settings_provider.findData(prefs["provider"]),
        )
        self.settings_provider.setCurrentIndex(provider_index)
        self._refill_settings_models(str(prefs["provider"]), str(prefs["model"]))
        self.settings_custom.setText(prefs.get("custom_model") or "")
        self.settings_custom.setEnabled(prefs["provider"] == "custom")
        self.settings_model.setEnabled(prefs["provider"] != "custom")
        self._load_gpt_form(prefs)
        self.settings_provider.blockSignals(False)
        self.settings_model.blockSignals(False)
        self._model_sync = False
        self._fill_model_combo()

    def _refill_settings_models(self, provider: str, selected_model: str) -> None:
        self.settings_model.clear()
        models = models_for(provider)
        if not models:
            self.settings_model.addItem("使用自定义名称", "")
            return
        chosen = 0
        for index, row in enumerate(models):
            self.settings_model.addItem(row["label"], row["id"])
            if row["id"] == selected_model:
                chosen = index
        self.settings_model.setCurrentIndex(chosen)

    def _on_settings_provider_changed(self, _index: int) -> None:
        if self._model_sync:
            return
        provider = str(self.settings_provider.currentData() or "")
        self._refill_settings_models(provider, "")
        self.settings_custom.setEnabled(provider == "custom")
        self.settings_model.setEnabled(provider != "custom")
        self._save_settings_model()

    def _on_settings_model_changed(self, _index: int) -> None:
        if self._model_sync:
            return
        self._save_settings_model()

    def _save_settings_model(self) -> None:
        provider = str(self.settings_provider.currentData() or "cursor")
        model = str(self.settings_model.currentData() or "")
        custom = self.settings_custom.text().strip()
        saved = save_prefs(
            self.root,
            {"provider": provider, "model": model, "custom_model": custom},
        )
        self._fill_model_combo()
        label = selection_label(saved)
        self.settings_status.setText(f"已保存  {label}")
        self.statusBar().showMessage(f"已选择  {label}")

    def _load_gpt_form(self, prefs: dict[str, str]) -> None:
        gpt = gpt_status(self.root)
        self.settings_gpt_model.blockSignals(True)
        self.settings_gpt_model.clear()
        chosen = 0
        selected = prefs["model"] if prefs.get("provider") == "openai" else str(gpt.get("model") or "gpt-4.1")
        for index, row in enumerate(gpt_models()):
            self.settings_gpt_model.addItem(row["label"], row["id"])
            if row["id"] == selected:
                chosen = index
        self.settings_gpt_model.setCurrentIndex(chosen)
        self.settings_gpt_model.blockSignals(False)
        self.settings_base_url.setText(str(gpt.get("base_url") or "https://api.openai.com/v1"))
        self.settings_api_key.clear()
        if gpt.get("connected"):
            source = {"file": "本机已保存密钥", "env": "环境变量 OPENAI_API_KEY", "input": "本机已保存密钥"}.get(
                str(gpt.get("key_source") or ""),
                "已有密钥",
            )
            self.settings_api_key.setPlaceholderText(f"{source}，留空则继续使用")
            self._set_gpt_status(True, f"已接入  {gpt.get('model')}", "ok")
        else:
            self.settings_api_key.setPlaceholderText("粘贴 sk- 开头的 API Key")
            self._set_gpt_status(False, "填写密钥后接入", "idle")

    def _set_gpt_busy(self, busy: bool) -> None:
        self.gpt_connect_btn.setEnabled(not busy)
        self.gpt_send_btn.setEnabled(not busy)
        self.gpt_prompt.setEnabled(not busy)
        self.settings_api_key.setEnabled(not busy)
        self.gpt_connect_btn.setText("处理中…" if busy else "接入 GPT")

    def _start_gpt_job(self, kind: str, payload: dict[str, Any]) -> bool:
        if self._gpt_job is not None and self._gpt_job.isRunning():
            return False
        self._set_gpt_busy(True)
        job = _GptJob(kind, self.root, payload)
        job.finished_result.connect(self._on_gpt_done)
        job.finished.connect(job.deleteLater)
        self._gpt_job = job
        job.start()
        return True

    def _connect_gpt(self) -> None:
        self._start_gpt_job(
            "connect",
            {
                "model": str(self.settings_gpt_model.currentData() or "gpt-4.1"),
                "api_key": self.settings_api_key.text().strip(),
                "base_url": self.settings_base_url.text().strip(),
            },
        )

    def _send_gpt(self) -> None:
        if self._gpt_job is not None and self._gpt_job.isRunning():
            return
        text = self.gpt_prompt.text().strip()
        if not text:
            self.gpt_connect_status.setText("请先输入要问 GPT 的内容。")
            return
        history = list(self._gpt_messages)
        self._gpt_messages.append({"role": "user", "content": text})
        self.gpt_prompt.clear()
        self._append_gpt_line("你", text)
        self._start_gpt_job(
            "chat",
            {
                "message": text,
                "model": str(self.settings_gpt_model.currentData() or "gpt-4.1"),
                "history": history,
            },
        )

    def _append_gpt_line(self, who: str, text: str) -> None:
        current = self.gpt_transcript.toPlainText().rstrip()
        block = f"{who}\n{text}"
        self.gpt_transcript.setPlainText((current + "\n\n" if current else "") + block)
        cursor = self.gpt_transcript.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.gpt_transcript.setTextCursor(cursor)

    def _set_gpt_status(self, connected: bool, note: str, tone: str) -> None:
        apply_tone(self.gpt_badge, tone, "已接入" if connected else "未接入")
        apply_tone(self.gpt_top_badge, tone, "GPT 已接入" if connected else "GPT 未接入")
        apply_tone(self.gpt_connect_status, "err" if tone == "err" else "plain", note)

    def _refresh_gpt_chrome(self) -> None:
        gpt = gpt_status(self.root)
        if gpt.get("connected"):
            self._set_gpt_status(True, f"已接入  {gpt.get('model')}", "ok")
        else:
            self._set_gpt_status(False, "填写密钥后接入", "idle")

    def _reveal_settings_section(self, section_id: str) -> None:
        card = self.settings_cards.get(section_id)
        if card is None:
            return
        self.settings_scroll.ensureWidgetVisible(card, 12, 24)
        labels = {"prefs": "模型偏好", "gpt": "接入 GPT", "chat": "对话"}
        self.top_context.setText(f"设置  ·  {labels.get(section_id, '本机')}")

    def _on_gpt_done(self, kind: str, result: object) -> None:
        self._set_gpt_busy(False)
        payload = result if isinstance(result, dict) else {"ok": False, "error": "未知结果"}
        if kind == "connect":
            if payload.get("ok"):
                self._load_settings_form()
                self._set_gpt_status(
                    True,
                    f"已接入  {payload.get('model')}，探测到 {payload.get('models', 0)} 个模型",
                    "ok",
                )
                self.statusBar().showMessage(f"已接入 GPT  {payload.get('model')}")
            else:
                self._set_gpt_status(False, str(payload.get("error") or "接入失败"), "err")
            return
        if payload.get("ok"):
            reply = str(payload.get("text") or "")
            self._gpt_messages.append({"role": "assistant", "content": reply})
            self._append_gpt_line("GPT", reply)
            self.gpt_connect_status.setText(f"已回复  {payload.get('model') or ''}".strip())
            return
        apply_tone(self.gpt_connect_status, "err", str(payload.get("error") or "发送失败"))

    def _open_section(self, kind: str) -> None:
        if not self._confirm_leave():
            return
        self.current_kind = kind
        self.list_title.setText(KIND_TITLES.get(kind, kind))
        self.search.setPlaceholderText("过滤 ID 或标题")
        self.create_btn.setVisible(kind in CREATE_SPECS)
        self._select_nav_kind(kind)
        rows = list_objects(self.root, kind)
        self._set_list(rows)
        if not rows:
            self._show_message(KIND_TITLES.get(kind, kind), "这一栏目前没有可显示的对象。")
            return
        self.objects.setCurrentRow(0)

    def _select_nav_kind(self, kind: str) -> None:
        for index in range(self.nav.topLevelItemCount()):
            top = self.nav.topLevelItem(index)
            data = top.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(data, dict) and data.get("kind") == kind:
                self.nav.setCurrentItem(top)
                return
            for child_index in range(top.childCount()):
                child = top.child(child_index)
                child_data = child.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(child_data, dict) and child_data.get("kind") == kind:
                    self.nav.setCurrentItem(child)
                    return

    def _set_list(self, rows: list[dict[str, Any]]) -> None:
        self.current_objects = rows
        self.search.blockSignals(True)
        self.search.clear()
        self.search.blockSignals(False)
        self._render_list(rows)

    def _render_list(self, rows: list[dict[str, Any]]) -> None:
        self.objects.blockSignals(True)
        self.objects.clear()
        for row in rows:
            oid = str(row.get("id") or "")
            title = str(row.get("title") or oid)
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, row)
            item.setSizeHint(QSize(0, 76 if row.get("group") else 58))
            self.objects.addItem(item)
            widget = ObjectRow(self.objects, item, oid, title, str(row.get("group") or ""))
            self.objects.setItemWidget(item, widget)
        self.list_count.setText(f"{len(rows)} 项")
        self.objects.blockSignals(False)
        self._refresh_row_selection()

    def _filter_objects(self, text: str) -> None:
        query = text.strip().lower()
        if not query:
            self._render_list(self.current_objects)
            return
        filtered = [
            row
            for row in self.current_objects
            if query in str(row.get("id") or "").lower() or query in str(row.get("title") or "").lower()
        ]
        self._render_list(filtered)

    def _on_object(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        self._refresh_row_selection()
        if current is None:
            return
        row = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(row, dict):
            return
        if previous is not None and current is not previous and self._is_dirty():
            if not self._confirm_leave():
                self.objects.blockSignals(True)
                self.objects.setCurrentItem(previous)
                self.objects.blockSignals(False)
                self._refresh_row_selection()
                return
        if self.current_kind == "home":
            self._open_home()
            return
        if self.current_kind == "settings":
            self.stack.setCurrentWidget(self.settings_panel)
            self._reveal_settings_section(str(row.get("id") or ""))
            return
        kind = self.current_kind
        object_id = str(row["id"])
        if kind in STUDIO_KINDS or kind in FILE_KINDS or kind == "lean" or kind == "exploration":
            studio_kind = kind
            if row.get("jump") == "project":
                studio_kind = "project"
            doc = get_object(self.root, studio_kind, object_id)
            if doc is None:
                self._show_message(object_id, "找不到这个对象，或路径不安全。")
                return
            self._show_document(doc)

    def _refresh_row_selection(self) -> None:
        current = self.objects.currentItem()
        for row in range(self.objects.count()):
            item = self.objects.item(row)
            widget = self.objects.itemWidget(item)
            if isinstance(widget, ObjectRow):
                widget.set_selected(item is current)

    def _clear_chips(self) -> None:
        while self.chip_layout.count():
            taken = self.chip_layout.takeAt(0)
            widget = taken.widget()
            if widget is not None:
                widget.deleteLater()

    def _show_document(self, doc: dict[str, Any]) -> None:
        self.stack.setCurrentWidget(self.doc_panel)
        self.title_label.setText(str(doc.get("title") or doc.get("id") or ""))
        kind_label = str(doc.get("kind_label") or KIND_LABELS.get(self.current_kind, ""))
        path = str(doc.get("path") or "")
        self.kicker.setText(kind_label or KIND_TITLES.get(self.current_kind, ""))
        self.meta.setText(path)
        yaml_status = doc.get("yaml_status")
        workflow = doc.get("workflow_dir")
        lines = []
        chips: list[str] = []
        if yaml_status:
            lines.append(f"YAML status：{yaml_status}")
            chips.append(f"YAML status  {yaml_status}")
        if workflow:
            lines.append(f"工作流目录：{workflow}")
            chips.append(f"工作流目录  {workflow}")
        if yaml_status and workflow:
            lines.append("这两列不能合成一枚徽章。")
        mapping = doc.get("knowledge")
        if mapping == []:
            lines.append("mapping 已完成，当前没有直接对象。")
            chips.append("mapping 已完成，当前没有直接对象")
        self.status_pair.setText("\n".join(lines))
        self._clear_chips()
        if chips:
            self.chip_layout.addWidget(chip_row(chips))
        self.chip_host.setVisible(bool(chips))
        body = str(doc.get("body") or "")
        self._preview_timer.stop()
        self.body.set_markdown(body, dark=self.dark)
        object_type = self.current_kind if self.current_kind in EDITABLE_TYPES else None
        object_id = str(doc.get("id") or "")
        editable = object_type is not None and bool(object_id) and bool(doc.get("path"))
        self._syncing_editor = True
        self.editor.setPlainText(body)
        self._syncing_editor = False
        self.editor.setReadOnly(not editable)
        self.edit_hint.setVisible(True)
        self.edit_hint.setText(
            "源码只改正文。YAML Front Matter、对象 ID 与 status 不在此编辑。"
            if editable
            else "此页只读。Lab / Lean / 投影页不能当作 Source 来改。"
        )
        self._edit_ctx = {
            "objectType": object_type,
            "objectId": object_id,
            "saved_body": body,
            "editable": editable,
        }
        self.top_context.setText(f"{KIND_TITLES.get(self.current_kind, self.current_kind)}  ·  {object_id or doc.get('title') or ''}")
        self.doc_tabs.setTabEnabled(1, True)
        self._bind_actions(doc)
        self._update_save_state()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._confirm_leave():
            event.accept()
        else:
            event.ignore()

    def _bind_actions(self, doc: dict[str, Any]) -> None:
        while self.actions_layout.count():
            taken = self.actions_layout.takeAt(0)
            widget = taken.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        app = QApplication.instance()
        if app is not None:
            app.processEvents()
        panel = build_action_panel(
            root=self.root,
            kind=self.current_kind,
            doc=doc,
            on_reload=self._reload_after_operation,
            on_open=self._open_kind_object,
        )
        self.actions_layout.addWidget(panel)

    def _reload_after_operation(self, kind: str | None = None, object_id: str | None = None) -> None:
        stay = self.doc_tabs.currentIndex()
        target_kind = kind or self.current_kind
        self._open_section(target_kind)
        if object_id:
            self._select_object_id(object_id)
        self.doc_tabs.setCurrentIndex(stay)

    def _select_object_id(self, object_id: str) -> None:
        for row in range(self.objects.count()):
            item = self.objects.item(row)
            data = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
            if isinstance(data, dict) and str(data.get("id") or "") == object_id:
                self.objects.setCurrentRow(row)
                return

    def _open_kind_object(self, kind: str, object_id: str) -> None:
        if kind != self.current_kind:
            self._open_section(kind)
        self._select_object_id(object_id)

    def _create_object(self) -> None:
        if self.current_kind not in CREATE_SPECS:
            return
        if not self._confirm_leave():
            return
        dialog = CreateObjectDialog(self, self.root, self.current_kind)
        if dialog.exec() and dialog.created_id:
            self._reload_after_operation(kind=self.current_kind, object_id=dialog.created_id)

    def _show_message(self, title: str, body: str) -> None:
        self._show_document({"title": title, "kind_label": "说明", "path": "", "body": body, "id": ""})

    def _clear_edit_ctx(self) -> None:
        self._edit_ctx = None
        self._update_save_state()

    def _is_dirty(self) -> bool:
        ctx = self._edit_ctx
        if not ctx or not ctx.get("editable"):
            return False
        return self.editor.toPlainText() != ctx.get("saved_body", "")

    def _on_editor_changed(self) -> None:
        if self._syncing_editor:
            return
        self._update_save_state()
        if self._edit_ctx:
            self._preview_timer.start()

    def _refresh_reading_from_editor(self) -> None:
        self.body.set_markdown(self.editor.toPlainText(), dark=self.dark)

    def _update_save_state(self) -> None:
        dirty = self._is_dirty()
        self.save_btn.setEnabled(dirty)
        message = f"仓库  {self.root}  ·  进程内  ·  无 HTTP 端口"
        if dirty:
            message = "未保存的正文修改  ·  " + message
        elif self._edit_ctx and self._edit_ctx.get("editable"):
            message = "可编辑正文  ·  " + message
        else:
            message = "只读  ·  " + message
        self.statusBar().showMessage(message)

    def _confirm_leave(self) -> bool:
        if not self._is_dirty():
            return True
        box = QMessageBox(self)
        box.setWindowTitle("未保存的修改")
        box.setText("当前 Markdown 正文已修改。")
        save_btn = box.addButton("保存", QMessageBox.ButtonRole.AcceptRole)
        box.addButton("丢弃", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked == save_btn:
            return self._save(interactive=True)
        if clicked == cancel_btn:
            return False
        return True

    def _save(self, *_args: object, interactive: bool = True) -> bool:
        ctx = self._edit_ctx
        if not ctx or not ctx.get("editable") or not ctx.get("objectType"):
            return False
        body = self.editor.toPlainText()
        request = {
            "version": 1,
            "operation": "UpdateMarkdownBody",
            "requestId": str(uuid.uuid4()),
            "payload": {
                "objectType": ctx["objectType"],
                "objectId": ctx["objectId"],
                "body": body,
            },
        }
        preview = run_operation(self.root, {**request, "preview": True})
        if not preview.success:
            messages = preview.error or "校验失败"
            if preview.issues:
                messages += "\n" + "\n".join(item.message for item in preview.issues[:8])
            QMessageBox.warning(self, "无法保存", messages)
            return False
        destination = str(preview.planned.get("destination") or "")
        if interactive:
            answer = QMessageBox.question(
                self,
                "确认写入",
                f"将只改正文并写入：\n{destination}\n\nYAML Front Matter 保持不变。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return False
        persist = run_operation(self.root, {**request, "preview": False})
        if not persist.success:
            QMessageBox.warning(self, "写入失败", persist.error or "validator 拒绝了这次保存")
            return False
        ctx["saved_body"] = body
        self._update_save_state()
        self.statusBar().showMessage(f"已写入 {destination}  ·  YAML 未改", 6000)
        return True


def prepare_qt_environment() -> None:
    from .bootstrap import webengine_blocked, write_log

    os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
    os.environ.setdefault(
        "QTWEBENGINE_CHROMIUM_FLAGS",
        "--disable-gpu --disable-gpu-compositing --no-sandbox",
    )
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        os.environ.setdefault("MATH_AI_LAB_QT_NO_WEBENGINE", "1")
    if webengine_blocked():
        os.environ.setdefault("MATH_AI_LAB_QT_NO_WEBENGINE", "1")
        write_log("webengine blocked by env or previous-crash guard")


def configure_app(app: QApplication) -> None:
    app.setApplicationName("MATH-AI-LAB")
    app.setOrganizationName("MATH-AI-LAB")
    font = QFont("Microsoft YaHei UI", 10)
    if not font.exactMatch():
        font = QFont("Segoe UI", 10)
    app.setFont(font)


def run(root: Path, *, argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv
    prepare_qt_environment()
    app = QApplication.instance()
    owns = app is None
    if app is None:
        app = QApplication(args)
    configure_app(app)
    window = MainWindow(root)
    window.show()
    window.raise_()
    window.activateWindow()
    if not owns:
        return 0
    return app.exec()
