"""Workspace integration tests for Descriptive Derived Evidence v1.3."""

from __future__ import annotations

import hashlib
from pathlib import Path

from tools.workspace_indexer.constants import INDEX_DIR_RELATIVE, MANAGED_FILES
from tools.workspace_indexer.renderer import render_all, render_learning_evidence_state
from tools.workspace_indexer.service import check_index, rebuild_index, sync_index

from .conftest import write_attempt, write_problem


def _hashes(project: Path) -> dict[str, str]:
    index_dir = project / INDEX_DIR_RELATIVE
    return {
        name: hashlib.sha256((index_dir / name).read_bytes()).hexdigest()
        for name in MANAGED_FILES
        if (index_dir / name).is_file()
    }


def test_learning_evidence_state_generated(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0002_x.md",
        pid="P0002",
        title="线性映射",
        extras="parts:\n  - a\n  - b\n  - c\n",
    )
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", aid="A000001", problem="P0002", part="b")
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000002.md",
        aid="A000002",
        problem="P0002",
        part="a",
        outcome="partial",
        assistance="independent",
    )
    op = rebuild_index(root=project)
    assert op.result.value in {"BUILT", "UP_TO_DATE"}
    path = project / INDEX_DIR_RELATIVE / "学习证据状态.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "P0002 / a" in text
    assert "P0002 / b" in text
    assert "partial=1" in text
    assert "correct=1" in text
    assert "mastery" not in text.lower()


def test_check_missing_then_sync_current(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", aid="A000001", problem="P0002", part="b")
    before = check_index(root=project)
    assert before.result.value in {"MISSING", "STALE"}
    sync_index(root=project)
    after = check_index(root=project)
    assert after.result.value == "CURRENT"


def test_outcome_change_stale(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    path = write_attempt(
        project,
        "11_学习证据/尝试记录/A000001.md",
        aid="A000001",
        problem="P0002",
        part="b",
        outcome="partial",
    )
    rebuild_index(root=project)
    assert check_index(root=project).result.value == "CURRENT"
    text = path.read_text(encoding="utf-8").replace("outcome: partial", "outcome: correct")
    path.write_text(text, encoding="utf-8")
    assert check_index(root=project).result.value == "STALE"
    sync_index(root=project)
    assert check_index(root=project).result.value == "CURRENT"
    derived = (project / INDEX_DIR_RELATIVE / "学习证据状态.md").read_text(encoding="utf-8")
    assert "correct=1" in derived


def test_body_only_no_derived_diff(project: Path) -> None:
    from tools.attempt_validator import validate_project as validate_attempt_project
    from tools.knowledge_validator import validate_project as validate_knowledge_project
    from tools.method_validator import validate_project as validate_method_project
    from tools.problem_validator import validate_project as validate_problem_project
    from tools.workspace_indexer.builder import build_workspace_snapshot

    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    apath = write_attempt(project, "11_学习证据/尝试记录/A000001.md", aid="A000001", problem="P0002", part="b")
    kr = validate_knowledge_project(root=project)
    pr = validate_problem_project(root=project, knowledge_result=kr)
    ar = validate_attempt_project(root=project, problem_result=pr)
    mr = validate_method_project(root=project, knowledge_result=kr)
    snap1 = build_workspace_snapshot(project, knowledge_result=kr, problem_result=pr, attempt_result=ar, method_result=mr)
    r1 = render_learning_evidence_state(snap1)
    apath.write_text(apath.read_text(encoding="utf-8") + "\nextra body\n", encoding="utf-8")
    ar2 = validate_attempt_project(root=project, problem_result=pr)
    snap2 = build_workspace_snapshot(project, knowledge_result=kr, problem_result=pr, attempt_result=ar2, method_result=mr)
    r2 = render_learning_evidence_state(snap2)
    assert r1 == r2


def test_invalid_attempt_zero_writes(project: Path) -> None:
    write_problem(project, "02_题目库/研究中/P0002_x.md", pid="P0002", extras="parts:\n  - a\n  - b\n")
    path = write_attempt(
        project,
        "11_学习证据/尝试记录/A000001.md",
        aid="A000001",
        problem="P0002",
        part="b",
    )
    rebuild_index(root=project)
    before = _hashes(project)
    text = path.read_text(encoding="utf-8").replace("outcome: correct", "outcome: not-valid")
    path.write_text(text, encoding="utf-8")
    op = sync_index(root=project)
    assert op.result.value == "FAIL"
    after = _hashes(project)
    assert before == after
