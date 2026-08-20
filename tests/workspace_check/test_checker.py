"""Tests for Workspace Check v1."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.workspace_check.checker import run_workspace_check

from tests.problem_validator.conftest import write_project
from tests.workspace_indexer.conftest import write_problem


@pytest.fixture
def project(tmp_path: Path) -> Path:
    from tests.knowledge_indexer.conftest import write_reviewed_pair
    from tests.workspace_indexer.conftest import ensure_attempt_root, ensure_method_root

    root = write_project(tmp_path)
    write_reviewed_pair(root)
    ensure_attempt_root(root)
    ensure_method_root(root)
    return root


def test_movable_path_warning(project: Path) -> None:
    gov = project / "项目规则.md"
    gov.write_text(
        "Ref: 02_题目库/未解决/P0002_线性映射phi(X)=AX-XB的谱与结构性质.md\n",
        encoding="utf-8",
    )
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002")

    result = run_workspace_check(root=project)
    assert any(i.rule_id == "WC-MOVABLE-W001" for i in result.issues)


def test_workspace_check_reports_method_validation(project: Path) -> None:
    from tests.workspace_indexer.conftest import write_method

    write_method(project, "12_方法库/M0001.md")
    result = run_workspace_check(root=project)
    assert result.method_validation == "PASS"
    assert result.repository_facts.get("methods") == 1


def test_workspace_check_method_error(project: Path) -> None:
    from tests.workspace_indexer.conftest import write_method

    write_method(project, "12_方法库/M0001.md", extras="created: 2026-08-19")
    result = run_workspace_check(root=project)
    assert result.method_validation == "FAIL"
    assert any(i.rule_id == "WC004" for i in result.issues)
    assert result.error_count >= 1
    from tests.workspace_indexer.conftest import write_attempt

    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md")

    def tree_mtime(root: Path) -> dict[str, int]:
        return {
            str(p.relative_to(root)): p.stat().st_mtime_ns
            for p in root.rglob("*")
            if p.is_file()
        }

    before = tree_mtime(project)
    run_workspace_check(root=project)
    after = tree_mtime(project)
    assert before == after
