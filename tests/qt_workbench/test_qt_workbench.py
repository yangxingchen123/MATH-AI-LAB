import pytest
from tools.problem_validator.discovery import find_project_root
from tools.qt_workbench.doctor import doctor
from tools.qt_workbench.nav import NAV_GROUPS, all_nav_items
from tools.qt_workbench.ops import format_result, preview_operation
from tools.qt_workbench.workspace import (
    get_object,
    inbox_promote_id,
    list_attempts,
    list_objects,
    search_exploration,
    snapshot,
)


def _root():
    return find_project_root()


def test_doctor_is_in_process_and_not_core():
    report = doctor()
    assert report["transport"] == "in-process"
    assert report["http"] is False
    assert report["port"] is None
    assert report["core_impact"] is False
    assert report["writes"] is True
    assert "webengine" in report


def test_nav_keeps_three_pillars_and_disables_research_intelligence():
    assert [group["id"] for group in NAV_GROUPS] == [
        "learn",
        "research",
        "personal",
        "advanced",
    ]
    later = [item["id"] for item in all_nav_items() if not item.get("enabled", True)]
    assert later == ["conjectures", "experiments", "timeline"]
    assert any(item["id"] == "exploration" and item.get("enabled") for item in all_nav_items())
    rows = list_objects(_root(), "exploration")
    assert rows[0]["id"] == "overview"
    assert get_object(_root(), "exploration", "overview")["body"].startswith("# 数学探索")


def test_snapshot_lists_real_objects_without_http():
    data = snapshot(_root())
    assert data["transport"] == "in-process"
    assert data["writes"] is False
    problems = {item["id"] for item in list_objects(_root(), "problem")}
    knowledge = {item["id"] for item in list_objects(_root(), "knowledge")}
    assert "P0001" in problems
    assert "P0002" in problems
    assert "P0000" not in problems
    assert "K0001" in knowledge
    assert "K0000" not in knowledge


def test_problem_keeps_yaml_status_separate_from_workflow_dir():
    doc = get_object(_root(), "problem", "P0002")
    assert doc is not None
    assert doc["yaml_status"] == "reviewed"
    assert doc["workflow_dir"] == "已解决"
    assert doc["path"].startswith("02_题目库/")


def test_path_traversal_is_rejected():
    assert get_object(_root(), "problem", "../元数据规范.md") is None
    assert get_object(_root(), "memory", "..\\01_知识库\\x.md") is None
    assert get_object(_root(), "lean", "../correspondence.yaml") is None


def test_qt_window_is_desktop_not_localhost():
    import os

    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from tools.qt_workbench.window import MainWindow, configure_app, prepare_qt_environment
    from tools.qt_workbench.reader import MarkdownReader

    prepare_qt_environment()
    app = QApplication.instance() or QApplication([])
    configure_app(app)
    window = MainWindow(_root())
    try:
        assert window.windowTitle() == "MATH-AI-LAB"
        message = window.statusBar().currentMessage()
        assert "无 HTTP 端口" in message
        assert "localhost" not in message.lower()
        assert "127.0.0.1" not in message
        assert window.current_kind == "home"
        problems_item = None
        for index in range(window.nav.topLevelItemCount()):
            top = window.nav.topLevelItem(index)
            for child_index in range(top.childCount()):
                child = top.child(child_index)
                if child.text(0) == "题目":
                    problems_item = child
        assert problems_item is not None
        window._on_nav(problems_item, 0)
        listed = [
            window.objects.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(window.objects.count())
        ]
        assert any(isinstance(row, dict) and row.get("id") == "P0002" for row in listed)
        window.objects.setCurrentRow(
            next(i for i, row in enumerate(listed) if isinstance(row, dict) and row.get("id") == "P0002")
        )
        assert "YAML status" in window.status_pair.text()
        assert "工作流目录" in window.status_pair.text()
        assert isinstance(window.body, MarkdownReader)
        assert "<h2" in window.body.page_html
        assert "## 题目" not in window.body.page_html
        assert "## 题目" in window.editor.toPlainText()
        assert "$" in window.editor.toPlainText()
        knowledge_item = None
        for index in range(window.nav.topLevelItemCount()):
            top = window.nav.topLevelItem(index)
            for child_index in range(top.childCount()):
                child = top.child(child_index)
                if child.text(0) == "知识":
                    knowledge_item = child
        assert knowledge_item is not None
        window._on_nav(knowledge_item, 0)
        listed = [
            window.objects.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(window.objects.count())
        ]
        window.objects.setCurrentRow(
            next(i for i, row in enumerate(listed) if isinstance(row, dict) and row.get("id") == "K0002")
        )
        assert "五、有效域" in window.body.page_html
        assert "## 五、有效域" not in window.body.page_html
        assert r"\operatorname{dom} f" in window.body.page_html
        assert "## 五、有效域" in window.editor.toPlainText()
        assert window.editor.isReadOnly() is False
        original = window.editor.toPlainText()
        window.editor.setPlainText(original + "\n")
        assert window._is_dirty() is True
        window.editor.setPlainText(original)
        assert window._is_dirty() is False
        assert window.model_combo.count() >= 2
        settings_item = None
        for index in range(window.nav.topLevelItemCount()):
            top = window.nav.topLevelItem(index)
            for child_index in range(top.childCount()):
                child = top.child(child_index)
                if child.text(0) == "设置":
                    settings_item = child
        assert settings_item is not None
        window._on_nav(settings_item, 0)
        assert window.current_kind == "settings"
        assert window.settings_provider.count() >= 2
        exploration_item = None
        for index in range(window.nav.topLevelItemCount()):
            top = window.nav.topLevelItem(index)
            for child_index in range(top.childCount()):
                child = top.child(child_index)
                if child.text(0) == "探索":
                    exploration_item = child
        assert exploration_item is not None
        window._on_nav(exploration_item, 0)
        assert window.current_kind == "exploration"
        assert "五问" in window.body.page_html
        assert "禁止自动 Promotion" in window.body.page_html
        assert "不是 Canonical" in window.body.page_html
    finally:
        window.close()


def test_list_attempts_and_exploration_search_are_read_only():
    attempts = list_attempts(_root(), "P0002")
    assert attempts
    assert all(row["id"].startswith("A") for row in attempts)
    assert list_attempts(_root(), "../P0002") == []
    hits = search_exploration("overview")
    assert any(row["id"] == "overview" for row in hits)
    assert search_exploration("   ") == []
    assert inbox_promote_id("00_收件箱/README.md") is None
    assert inbox_promote_id("00_收件箱/note.md") == "note.md"
    assert inbox_promote_id("00_收件箱/sub/note.md") is None
    assert inbox_promote_id("../README.md") is None


def test_attempt_preview_does_not_write_ledger():
    from tools.attempt_validator.constants import ATTEMPT_DIR_NAME

    ledger = _root() / ATTEMPT_DIR_NAME / "P0002.md"
    before = ledger.read_text(encoding="utf-8")
    result = preview_operation(
        _root(),
        "RecordAttempt",
        {
            "problemId": "P0002",
            "narrative": "Qt UI preview only.",
            "outcome": "unassessed",
            "assistance": "independent",
        },
    )
    assert result.success is True
    assert result.preview is True
    assert result.validation == "NOT_RUN"
    assert "Preview only" in " ".join(result.warnings)
    assert ledger.read_text(encoding="utf-8") == before
    text = format_result(result)
    assert "RecordAttempt" in text
    assert "P0002" in text


def test_qt_operations_tab_exposes_domain_actions():
    import os

    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QComboBox, QLabel, QLineEdit, QPlainTextEdit, QPushButton
    from tools.qt_workbench.window import MainWindow, configure_app, prepare_qt_environment

    prepare_qt_environment()
    app = QApplication.instance() or QApplication([])
    configure_app(app)

    def nav_child(window, label):
        for index in range(window.nav.topLevelItemCount()):
            top = window.nav.topLevelItem(index)
            for child_index in range(top.childCount()):
                child = top.child(child_index)
                if child.text(0) == label:
                    return child
        raise AssertionError(label)

    def select_id(window, object_id):
        listed = [
            window.objects.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(window.objects.count())
        ]
        window.objects.setCurrentRow(
            next(i for i, row in enumerate(listed) if isinstance(row, dict) and row.get("id") == object_id)
        )
        app.processEvents()

    window = MainWindow(_root())
    try:
        assert window.doc_tabs.tabText(2) == "操作"
        window._on_nav(nav_child(window, "题目"), 0)
        assert window.create_btn.isHidden() is False
        select_id(window, "P0002")
        window.doc_tabs.setCurrentIndex(2)
        app.processEvents()
        assert window.findChild(QComboBox, "workflowCombo") is not None
        assert window.findChild(QPlainTextEdit, "attemptNarrative") is not None
        window._on_nav(nav_child(window, "知识"), 0)
        assert window.create_btn.isHidden() is False
        window._on_nav(nav_child(window, "Lab"), 0)
        window.doc_tabs.setCurrentIndex(2)
        app.processEvents()
        host = window.actions_host
        assert host.findChild(QLineEdit, "labSet") is not None
        evaluate = host.findChild(QPushButton, "labEvaluateBtn")
        assert evaluate is not None
        evaluate.click()
        app.processEvents()
        result = host.findChild(QPlainTextEdit, "labResult")
        assert result is not None
        assert "wrote_canonical: False" in result.toPlainText()
        window._on_nav(nav_child(window, "探索"), 0)
        assert window.create_btn.isHidden() is True
        window.doc_tabs.setCurrentIndex(2)
        app.processEvents()
        host = window.actions_host
        search = host.findChild(QLineEdit, "failureSearch")
        assert search is not None
        search.setText("overview")
        search_btn = host.findChild(QPushButton, "exploreSearchBtn")
        assert search_btn is not None
        search_btn.click()
        app.processEvents()
        hits = host.findChild(QLabel, "searchHits")
        assert hits is not None
        assert "命中" in hits.text()
        window._on_nav(nav_child(window, "收件箱"), 0)
        window.doc_tabs.setCurrentIndex(2)
        app.processEvents()
        assert window.findChild(QComboBox, "promoteType") is None
    finally:
        window.close()

