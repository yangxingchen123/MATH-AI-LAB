from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.ui_operations.conftest import write_draft_problem, write_ui_project
from tools.ui_operations.constants import OPERATIONS
from tools.ui_operations.gateway import doctor, run_operation


def test_doctor_lists_whitelist() -> None:
    payload = doctor()
    assert payload["version"] == 1
    assert set(payload["operations"]) == set(OPERATIONS)


def test_unknown_operation_rejected(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    result = run_operation(
        tmp_path,
        {"version": 1, "operation": "DeleteEverything", "preview": True, "payload": {}},
    )
    assert result.success is False
    assert "whitelist" in (result.error or "")


def test_payload_cannot_set_root(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    result = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "CreateProblem",
            "preview": True,
            "payload": {"root": str(tmp_path), "title": "x", "body": "y"},
        },
    )
    assert result.success is False
    assert "filesystem" in (result.error or "")


def test_create_problem_preview_does_not_persist(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    result = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "CreateProblem",
            "preview": True,
            "requestId": "t1",
            "payload": {"title": "新题", "body": "证明 1+1=2。"},
        },
    )
    assert result.success is True
    assert result.preview is True
    assert result.validation == "PASS"
    assert result.planned["id"] == "P0001"
    assert result.changed_files == []
    assert not (tmp_path / "02_题目库" / "未解决" / "P0001.md").exists()


def test_create_problem_persist_and_invalid_title(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    bad = run_operation(
        tmp_path,
        {"version": 1, "operation": "CreateProblem", "preview": False, "payload": {"title": "", "body": "x"}},
    )
    assert bad.success is False

    result = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "CreateProblem",
            "preview": False,
            "payload": {"title": "新题", "body": "证明 1+1=2。"},
        },
    )
    assert result.success is True
    assert result.validation == "PASS"
    dest = tmp_path / "02_题目库" / "未解决" / "P0001.md"
    assert dest.is_file()
    assert result.changed_files == ["02_题目库/未解决/P0001.md"]
    text = dest.read_text(encoding="utf-8")
    assert "id: P0001" in text
    assert "status: draft" in text


def test_create_knowledge_and_method(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    knowledge = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "CreateKnowledge",
            "preview": False,
            "payload": {"title": "加法", "body": "自然数加法。", "domain": "算术"},
        },
    )
    assert knowledge.success is True
    assert (tmp_path / "01_知识库" / "K0001.md").is_file()

    method = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "CreateMethod",
            "preview": False,
            "payload": {"title": "直接展开", "body": "把定义代入。"},
        },
    )
    assert method.success is True
    assert (tmp_path / "12_方法库" / "M0001.md").is_file()
    assert "knowledge:" not in (tmp_path / "12_方法库" / "M0001.md").read_text(encoding="utf-8").split("---")[1]


def test_record_attempt_preview_and_persist(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    write_draft_problem(tmp_path)
    preview = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "RecordAttempt",
            "preview": True,
            "payload": {
                "problemId": "P0001",
                "narrative": "我写了一步。",
                "outcome": "unassessed",
                "assistance": "independent",
            },
        },
    )
    assert preview.success is True
    assert preview.planned["attempt"] == "A000001"
    assert not (tmp_path / "11_学习证据" / "尝试记录" / "P0001.md").exists()

    bad = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "RecordAttempt",
            "preview": False,
            "payload": {"problemId": "P0001", "narrative": "x", "outcome": "perfect"},
        },
    )
    assert bad.success is False

    persist = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "RecordAttempt",
            "preview": False,
            "payload": {
                "problemId": "P0001",
                "narrative": "我写了一步。",
                "outcome": "unassessed",
                "assistance": "independent",
            },
        },
    )
    assert persist.success is True
    ledger = tmp_path / "11_学习证据" / "尝试记录" / "P0001.md"
    assert ledger.is_file()
    text = ledger.read_text(encoding="utf-8")
    assert "A000001" in text
    assert "我写了一步。" in text
    assert persist.changed_files


def test_move_workflow_preview_then_persist(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    write_draft_problem(tmp_path)
    preview = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "MoveProblemWorkflow",
            "preview": True,
            "payload": {"problemId": "P0001", "targetWorkflow": "研究中"},
        },
    )
    assert preview.success is True
    assert (tmp_path / "02_题目库" / "未解决" / "P0001.md").is_file()
    persist = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "MoveProblemWorkflow",
            "preview": False,
            "payload": {"problemId": "P0001", "targetWorkflow": "研究中"},
        },
    )
    assert persist.success is True
    assert not (tmp_path / "02_题目库" / "未解决" / "P0001.md").exists()
    assert (tmp_path / "02_题目库" / "研究中" / "P0001.md").is_file()
    assert any("moved" in item for item in persist.changed_files)


def test_promote_inbox_leaves_source(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    inbox = tmp_path / "00_收件箱" / "scratch.md"
    inbox.write_text("# 草稿定义\n\n一组对象。\n", encoding="utf-8")
    result = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "PromoteInboxItem",
            "preview": False,
            "payload": {
                "inboxId": "scratch.md",
                "targetType": "knowledge",
                "title": "对象",
                "body": "一组对象。",
            },
        },
    )
    assert result.success is True
    assert inbox.is_file()
    assert (tmp_path / "01_知识库" / "K0001.md").is_file()
    assert any("not moved" in w.lower() or "left" in w.lower() for w in result.warnings)


def test_promote_rejects_path_traversal(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    result = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "PromoteInboxItem",
            "preview": True,
            "payload": {"inboxId": "../元数据规范.md", "targetType": "problem"},
        },
    )
    assert result.success is False


def test_ts_contract_matches_python() -> None:
    text = (Path(__file__).resolve().parents[2] / "packages" / "domain" / "src" / "operations.ts").read_text(
        encoding="utf-8"
    )
    for name in OPERATIONS:
        assert f'"{name}"' in text


def test_full_workbench_flow(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    inbox = tmp_path / "00_收件箱" / "note.md"
    inbox.write_text("一条收件箱笔记。", encoding="utf-8")

    problem = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "CreateProblem",
            "preview": False,
            "payload": {"title": "流程题", "body": "证明 2+2=4。"},
        },
    )
    assert problem.success and problem.planned["id"] == "P0001"

    attempt = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "RecordAttempt",
            "preview": False,
            "payload": {
                "problemId": "P0001",
                "narrative": "先写 2+2。",
                "outcome": "unassessed",
            },
        },
    )
    assert attempt.success

    moved = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "MoveProblemWorkflow",
            "preview": False,
            "payload": {"problemId": "P0001", "targetWorkflow": "研究中"},
        },
    )
    assert moved.success
    assert (tmp_path / "02_题目库" / "研究中" / "P0001.md").is_file()

    knowledge = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "CreateKnowledge",
            "preview": False,
            "payload": {"title": "整数加法", "body": "交换律。"},
        },
    )
    assert knowledge.success

    method = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "CreateMethod",
            "preview": False,
            "payload": {"title": "直接计算", "body": "按定义算。"},
        },
    )
    assert method.success

    promoted = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "PromoteInboxItem",
            "preview": False,
            "payload": {"inboxId": "note.md", "targetType": "knowledge", "title": "笔记", "body": "一条收件箱笔记。"},
        },
    )
    assert promoted.success
    assert inbox.is_file()
    assert (tmp_path / "01_知识库" / "K0002.md").is_file()


def test_cli_json_roundtrip(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    request = {
        "version": 1,
        "operation": "CreateKnowledge",
        "preview": True,
        "requestId": "cli",
        "payload": {"title": "CLI", "body": "body"},
    }
    proc = subprocess.run(
        [sys.executable, "-m", "tools.ui_operations", "run", "--root", str(tmp_path)],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        check=False,
        cwd=Path(__file__).resolve().parents[2],
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["success"] is True
    assert data["preview"] is True
    assert data["planned"]["id"] == "K0001"


def test_update_markdown_body_preview_then_persist_keeps_yaml(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    write_draft_problem(tmp_path)
    original = (tmp_path / "02_题目库" / "未解决" / "P0001.md").read_text(encoding="utf-8")
    preview = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "UpdateMarkdownBody",
            "preview": True,
            "payload": {"objectType": "problem", "objectId": "P0001", "body": "新的正文。\n"},
        },
    )
    assert preview.success is True
    assert preview.preview is True
    assert (tmp_path / "02_题目库" / "未解决" / "P0001.md").read_text(encoding="utf-8") == original
    persist = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "UpdateMarkdownBody",
            "preview": False,
            "payload": {"objectType": "problem", "objectId": "P0001", "body": "新的正文。\n"},
        },
    )
    assert persist.success is True
    text = (tmp_path / "02_题目库" / "未解决" / "P0001.md").read_text(encoding="utf-8")
    assert "id: P0001" in text
    assert "status: draft" in text
    assert "新的正文。" in text
    assert persist.changed_files == ["02_题目库/未解决/P0001.md"]


def test_update_markdown_body_rejects_path_payload_and_traversal(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    write_draft_problem(tmp_path)
    rooted = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "UpdateMarkdownBody",
            "preview": True,
            "payload": {"objectType": "problem", "objectId": "P0001", "body": "x", "path": "02_题目库/x.md"},
        },
    )
    assert rooted.success is False
    traversal = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "UpdateMarkdownBody",
            "preview": True,
            "payload": {"objectType": "memory", "objectId": "../元数据规范.md", "body": "hack"},
        },
    )
    assert traversal.success is False


def test_update_markdown_note_without_yaml(tmp_path: Path) -> None:
    write_ui_project(tmp_path)
    dest = tmp_path / "09_长期记忆" / "笔记.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("旧笔记\n", encoding="utf-8")
    result = run_operation(
        tmp_path,
        {
            "version": 1,
            "operation": "UpdateMarkdownBody",
            "preview": False,
            "payload": {
                "objectType": "memory",
                "objectId": "09_长期记忆/笔记.md",
                "body": "改过的笔记",
            },
        },
    )
    assert result.success is True
    assert dest.read_text(encoding="utf-8") == "改过的笔记\n"
