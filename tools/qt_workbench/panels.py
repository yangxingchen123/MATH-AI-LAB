"""Action forms for the Qt 操作 tab. Writes go through Domain Operations."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from tools.qt_workbench.ops import run_gated
from tools.qt_workbench.workspace import inbox_promote_id, list_attempts, search_exploration
from tools.research_lab.evaluators.sum_free import evaluate_candidate
from tools.ui_operations.constants import WORKFLOW_DIRS

OUTCOME_ORDER = ("unassessed", "partial", "correct", "incorrect", "unsolved", "abandoned")
PROMOTE_ORDER = ("problem", "knowledge", "method")

CREATE_SPECS = {
    "problem": {"operation": "CreateProblem", "heading": "创建题目", "extra": "parts"},
    "knowledge": {"operation": "CreateKnowledge", "heading": "创建知识", "extra": "domain"},
    "method": {"operation": "CreateMethod", "heading": "创建方法", "extra": None},
}

ReloadFn = Callable[..., None]
OpenFn = Callable[[str, str], None]


def _hint(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("editHint")
    label.setWordWrap(True)
    return label


def _heading(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("listHeading")
    label.setWordWrap(True)
    return label


def _field_edit() -> QLineEdit:
    edit = QLineEdit()
    edit.setObjectName("field")
    return edit


def _field_text(rows: int = 8) -> QPlainTextEdit:
    edit = QPlainTextEdit()
    edit.setObjectName("field")
    edit.setTabStopDistance(32)
    edit.setMinimumHeight(24 * rows)
    return edit


def build_action_panel(
    *,
    root: Path,
    kind: str,
    doc: dict[str, Any],
    on_reload: ReloadFn,
    on_open: OpenFn,
) -> QWidget:
    panel = QWidget()
    panel.setObjectName("actionPanel")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 8, 8, 16)
    layout.setSpacing(12)
    if kind == "problem":
        layout.addWidget(ProblemActions(root, doc, on_reload))
    elif kind == "inbox":
        layout.addWidget(InboxActions(root, doc, on_reload))
    elif kind == "exploration":
        layout.addWidget(ExploreTools(on_open))
    elif kind == "lab":
        layout.addWidget(LabTools())
    elif kind in CREATE_SPECS:
        layout.addWidget(_hint("左侧「新建」会走 Create*：Python 分配 ID，预览通过后再写入。"))
    else:
        layout.addWidget(_hint("此页没有可执行的 Domain Operation。Lab / Lean / 宇宙仍是只读投影。"))
    layout.addStretch(1)
    return panel


class ProblemActions(QWidget):
    def __init__(self, root: Path, doc: dict[str, Any], on_reload: ReloadFn) -> None:
        super().__init__()
        self.root = root
        self.problem_id = str(doc.get("id") or "")
        self.on_reload = on_reload
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(_heading("工作流目录"))
        layout.addWidget(_hint("只移动 02_题目库/ 目录。这不是 YAML objectStatus。"))
        current = str(doc.get("workflow_dir") or "")
        self.workflow = QComboBox()
        self.workflow.setObjectName("workflowCombo")
        self.workflow.addItems(list(WORKFLOW_DIRS))
        if current in WORKFLOW_DIRS:
            self.workflow.setCurrentText(current)
        move_btn = QPushButton("预览移动")
        move_btn.setObjectName("ghostButton")
        move_btn.clicked.connect(self._move)
        row = QHBoxLayout()
        row.addWidget(self.workflow, 1)
        row.addWidget(move_btn)
        layout.addLayout(row)

        layout.addWidget(_heading("我的 Attempt"))
        layout.addWidget(_hint("只记录你自己的作答。canonical / AI 解答不会进入 ledger。append-only。"))
        attempts = list_attempts(root, self.problem_id)
        if not attempts:
            layout.addWidget(_hint("还没有 Attempt。"))
        else:
            summary = QLabel(
                "\n".join(
                    f"{row['id']}  ·  {row.get('outcome')}"
                    + (f"  ·  part {row['part']}" if row.get("part") else "")
                    for row in attempts[-8:]
                )
            )
            summary.setObjectName("mutedLabel")
            summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            layout.addWidget(summary)

        layout.addWidget(_heading("New Attempt"))
        form = QFormLayout()
        parts = [str(item) for item in (doc.get("parts") or []) if item]
        self.part = QComboBox()
        self.part.setObjectName("partCombo")
        self.part.addItem("（整题）", "")
        for part in parts:
            self.part.addItem(part, part)
        if parts:
            form.addRow("part", self.part)
        self.outcome = QComboBox()
        self.outcome.setObjectName("outcomeCombo")
        for item in OUTCOME_ORDER:
            self.outcome.addItem(item)
        self.outcome.setCurrentText("unassessed")
        form.addRow("outcome", self.outcome)
        layout.addLayout(form)
        layout.addWidget(QLabel("作答"))
        self.narrative = _field_text(10)
        self.narrative.setObjectName("attemptNarrative")
        layout.addWidget(self.narrative)
        attempt_btn = QPushButton("预览 Attempt")
        attempt_btn.setObjectName("primaryButton")
        attempt_btn.clicked.connect(self._attempt)
        layout.addWidget(attempt_btn, 0, Qt.AlignmentFlag.AlignLeft)

    def _move(self) -> None:
        result = run_gated(
            self,
            self.root,
            "MoveProblemWorkflow",
            {"problemId": self.problem_id, "targetWorkflow": self.workflow.currentText()},
        )
        if result is not None and result.success and not result.preview:
            self.on_reload(kind="problem", object_id=self.problem_id)

    def _attempt(self) -> None:
        part = self.part.currentData()
        payload: dict[str, Any] = {
            "problemId": self.problem_id,
            "narrative": self.narrative.toPlainText(),
            "outcome": self.outcome.currentText(),
            "assistance": "independent",
        }
        if part:
            payload["part"] = part
        result = run_gated(self, self.root, "RecordAttempt", payload)
        if result is not None and result.success and not result.preview:
            self.narrative.clear()
            self.on_reload(kind="problem", object_id=self.problem_id)


class InboxActions(QWidget):
    def __init__(self, root: Path, doc: dict[str, Any], on_reload: ReloadFn) -> None:
        super().__init__()
        self.root = root
        self.on_reload = on_reload
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        inbox_id = inbox_promote_id(str(doc.get("id") or ""))
        if inbox_id is None:
            layout.addWidget(_hint("README 或子目录文件不能提升。提升只接受 00_收件箱/ 根下的文件名。"))
            return
        self.inbox_id = inbox_id
        layout.addWidget(_heading("提升为正式对象"))
        layout.addWidget(_hint("写入走 Create*。收件箱原文件按现有生命周期保留，不会移动或删除。"))
        self.target = QComboBox()
        self.target.setObjectName("promoteType")
        for item in PROMOTE_ORDER:
            self.target.addItem(item)
        layout.addWidget(self.target)
        self.title = _field_edit()
        self.title.setText(str(doc.get("title") or inbox_id))
        layout.addWidget(QLabel("title"))
        layout.addWidget(self.title)
        layout.addWidget(QLabel("正文"))
        self.body = _field_text(10)
        self.body.setPlainText(str(doc.get("body") or ""))
        layout.addWidget(self.body)
        btn = QPushButton("预览提升")
        btn.setObjectName("primaryButton")
        btn.clicked.connect(self._promote)
        layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignLeft)

    def _promote(self) -> None:
        target = self.target.currentText()
        result = run_gated(
            self,
            self.root,
            "PromoteInboxItem",
            {
                "inboxId": self.inbox_id,
                "targetType": target,
                "title": self.title.text(),
                "body": self.body.toPlainText(),
            },
        )
        if result is None or not result.success or result.preview:
            return
        created = result.planned.get("id")
        kind = {"problem": "problem", "knowledge": "knowledge", "method": "method"}[target]
        if isinstance(created, str):
            self.on_reload(kind=kind, object_id=created)
        else:
            self.on_reload()


class ExploreTools(QWidget):
    def __init__(self, on_open: OpenFn) -> None:
        super().__init__()
        self.on_open = on_open
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(_heading("检索过程记录"))
        layout.addWidget(_hint("字面匹配，无向量、无 embedding。命中仍是 Candidate，不是定理。"))
        row = QHBoxLayout()
        self.query = QLineEdit()
        self.query.setObjectName("failureSearch")
        self.query.setPlaceholderText("例如 not_sum_free、reasoning、overview")
        btn = QPushButton("检索")
        btn.setObjectName("exploreSearchBtn")
        btn.clicked.connect(self._search)
        self.query.returnPressed.connect(self._search)
        row.addWidget(self.query, 1)
        row.addWidget(btn)
        layout.addLayout(row)
        self.hits = QLabel("输入关键词后检索。")
        self.hits.setObjectName("searchHits")
        self.hits.setWordWrap(True)
        self.hits.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.hits)
        self.hit_box = QVBoxLayout()
        layout.addLayout(self.hit_box)

    def _search(self) -> None:
        while self.hit_box.count():
            taken = self.hit_box.takeAt(0)
            widget = taken.widget()
            if widget is not None:
                widget.deleteLater()
        hits = search_exploration(self.query.text())
        self.hits.setText(f"{len(hits)} 条命中 · status=candidate · embeddings=false")
        for row in hits[:20]:
            oid = str(row.get("id") or "")
            btn = QPushButton(f"{row.get('title') or oid}  ·  {row.get('group') or ''}")
            btn.setObjectName("ghostButton")
            btn.setStyleSheet("text-align: left;")
            btn.clicked.connect(lambda _=False, item=oid: self.on_open("exploration", item))
            self.hit_box.addWidget(btn)


class LabTools(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(_heading("sum-free 评估"))
        layout.addWidget(
            _hint("已知答案校准，不是新定理。不写 Canonical。n 过大时枚举不要从这里跑。")
        )
        form = QFormLayout()
        self.n = QSpinBox()
        self.n.setObjectName("labN")
        self.n.setRange(0, 40)
        self.n.setValue(10)
        self.values = _field_edit()
        self.values.setObjectName("labSet")
        self.values.setText("6,7,8,9,10")
        form.addRow("n", self.n)
        form.addRow("集合", self.values)
        layout.addLayout(form)
        btn = QPushButton("评估")
        btn.setObjectName("labEvaluateBtn")
        btn.clicked.connect(self._evaluate)
        layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignLeft)
        self.out = _field_text(8)
        self.out.setReadOnly(True)
        self.out.setObjectName("labResult")
        layout.addWidget(self.out)

    def _evaluate(self) -> None:
        raw = self.values.text().replace("，", ",")
        try:
            values = {int(item.strip()) for item in raw.split(",") if item.strip()}
        except ValueError:
            self.out.setPlainText("集合必须是逗号分隔的整数。")
            return
        report = evaluate_candidate(int(self.n.value()), values)
        report = {**report, "wrote_canonical": False, "not_a_theorem": True}
        self.out.setPlainText(
            "\n".join(f"{key}: {value}" for key, value in report.items())
        )


class CreateObjectDialog(QDialog):
    def __init__(self, parent: QWidget, root: Path, kind: str) -> None:
        super().__init__(parent)
        self.root = root
        self.kind = kind
        spec = CREATE_SPECS[kind]
        self.operation = spec["operation"]
        self.created_id: str | None = None
        self.setWindowTitle(spec["heading"])
        if parent is not None:
            self.setStyleSheet(parent.styleSheet())
        layout = QVBoxLayout(self)
        layout.addWidget(_hint("只收集 Frozen Schema 已有字段。ID 由 Python 分配。预览通过后再确认写入。"))
        layout.addWidget(QLabel("title"))
        self.title = _field_edit()
        layout.addWidget(self.title)
        self.extra_edit = _field_edit()
        extra = spec["extra"]
        if extra == "domain":
            layout.addWidget(QLabel("domain（可选，draft 可不填）"))
            layout.addWidget(self.extra_edit)
        elif extra == "parts":
            layout.addWidget(QLabel("parts（可选，空格或逗号分隔，仅真实 multipart）"))
            layout.addWidget(self.extra_edit)
        else:
            self.extra_edit.hide()
        layout.addWidget(QLabel("正文"))
        self.body = _field_text(12)
        layout.addWidget(self.body)
        btn = QPushButton("预览")
        btn.setObjectName("primaryButton")
        btn.clicked.connect(self._submit)
        layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignLeft)
        self.resize(520, 560)

    def _payload(self) -> dict[str, Any]:
        data: dict[str, Any] = {"title": self.title.text(), "body": self.body.toPlainText()}
        extra = CREATE_SPECS[self.kind]["extra"]
        raw = self.extra_edit.text().strip()
        if extra == "domain" and raw:
            data["domain"] = raw
        if extra == "parts" and raw:
            data["parts"] = [item for item in raw.replace("，", " ").replace(",", " ").split() if item]
        return data

    def _submit(self) -> None:
        result = run_gated(self, self.root, self.operation, self._payload())
        if result is None or not result.success or result.preview:
            return
        created = result.planned.get("id")
        if isinstance(created, str):
            self.created_id = created
            self.accept()
        else:
            self.accept()
