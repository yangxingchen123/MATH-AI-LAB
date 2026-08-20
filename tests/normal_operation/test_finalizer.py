"""Tests for Normal Operation finalizer."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from tools.normal_operation.finalizer import finalize
from tools.normal_operation.models import LayerStatus
from tools.workspace_indexer.models import IndexOperationResult, IndexResultKind


def _index_result(kind: IndexResultKind) -> IndexOperationResult:
    return IndexOperationResult(result=kind, project_root=".", index_dir="09_长期记忆/自动索引/")


def test_problem_change_runs_problem_validator(tmp_path: Path) -> None:
    (tmp_path / "元数据规范.md").write_text("# schema\n", encoding="utf-8")
    (tmp_path / "01_知识库").mkdir()
    called: list[str] = []

    def track(name):
        def _fn(root, **kwargs):
            called.append(name)
            return type("R", (), {"summary": type("S", (), {"errors": 0})()})()

        return _fn

    with patch("tools.normal_operation.finalizer.validate_knowledge_project", side_effect=track("knowledge")), patch(
        "tools.normal_operation.finalizer.validate_problem_project",
        side_effect=track("problem"),
    ), patch("tools.normal_operation.finalizer.check_index", return_value=_index_result(IndexResultKind.CURRENT)), patch(
        "tools.normal_operation.finalizer.run_workspace_check",
        return_value=type("W", (), {"error_count": 0, "warning_count": 0})(),
    ), patch("tools.normal_operation.finalizer.run_verification") as verify:
        verify.return_value = type("V", (), {"overall_status": type("S", (), {"value": "PASS"})()})()
        result = finalize(root=tmp_path, changed=["problem"], include_verification=False)
    assert "problem" in called
    assert result.validation_status == LayerStatus.PASS
    assert result.workspace_sync_performed is False


def test_stale_workspace_triggers_single_sync(tmp_path: Path) -> None:
    (tmp_path / "元数据规范.md").write_text("# schema\n", encoding="utf-8")
    (tmp_path / "01_知识库").mkdir()
    checks = iter(
        [
            _index_result(IndexResultKind.STALE),
            _index_result(IndexResultKind.CURRENT),
        ]
    )

    with patch("tools.normal_operation.finalizer.validate_problem_project") as pv, patch(
        "tools.normal_operation.finalizer.validate_knowledge_project"
    ) as kv, patch("tools.normal_operation.finalizer.check_index", side_effect=lambda **_: next(checks)), patch(
        "tools.normal_operation.finalizer.sync_index",
        return_value=_index_result(IndexResultKind.BUILT),
    ) as sync, patch(
        "tools.normal_operation.finalizer.run_workspace_check",
        return_value=type("W", (), {"error_count": 0, "warning_count": 0})(),
    ), patch("tools.normal_operation.finalizer.run_verification") as verify:
        kv.return_value = type("R", (), {"summary": type("S", (), {"errors": 0})()})()
        pv.return_value = type("R", (), {"summary": type("S", (), {"errors": 0})()})()
        verify.return_value = type("V", (), {"overall_status": type("S", (), {"value": "PASS"})()})()
        result = finalize(root=tmp_path, changed=["problem"])
    sync.assert_called_once()
    assert result.workspace_sync_performed is True
    assert result.workspace_final == IndexResultKind.CURRENT.value


def test_validator_fail_blocks_sync(tmp_path: Path) -> None:
    (tmp_path / "元数据规范.md").write_text("# schema\n", encoding="utf-8")
    (tmp_path / "01_知识库").mkdir()
    with patch("tools.normal_operation.finalizer.validate_knowledge_project") as kv, patch(
        "tools.normal_operation.finalizer.validate_problem_project"
    ) as pv, patch("tools.normal_operation.finalizer.sync_index") as sync:
        kv.return_value = type("R", (), {"summary": type("S", (), {"errors": 0})()})()
        pv.return_value = type("R", (), {"summary": type("S", (), {"errors": 1})()})()
        result = finalize(root=tmp_path, changed=["problem"])
    sync.assert_not_called()
    assert result.validation_status == LayerStatus.FAIL
