"""Workspace integration tests for Knowledge Associated Evidence v1.4."""

from __future__ import annotations

import hashlib
from pathlib import Path

from tools.workspace_indexer.constants import INDEX_DIR_RELATIVE, MANAGED_FILES
from tools.workspace_indexer.renderer import render_knowledge_associated_evidence
from tools.workspace_indexer.service import check_index, rebuild_index, sync_index

from .conftest import write_attempt, write_problem


def _hashes(project: Path) -> dict[str, str]:
    index_dir = project / INDEX_DIR_RELATIVE
    return {
        name: hashlib.sha256((index_dir / name).read_bytes()).hexdigest()
        for name in MANAGED_FILES
        if (index_dir / name).is_file()
    }


def test_knowledge_associated_evidence_generated_empty(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0002_x.md",
        pid="P0002",
        extras="parts:\n  - a\n  - b\n",
    )
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", aid="A000001", problem="P0002", part="b")
    op = rebuild_index(root=project)
    assert op.result.value in {"BUILT", "UP_TO_DATE"}
    path = project / INDEX_DIR_RELATIVE / "知识关联证据.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "No knowledge-associated evidence available" in text
    assert "mastery=" not in text.lower()
    assert "success rate" not in text.lower()


def test_whole_attempt_k_association(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0001_x.md",
        pid="P0001",
        extras="knowledge:\n  - K0001\n  - K0002\n",
    )
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000001.md",
        aid="A000001",
        problem="P0001",
        part=None,
        outcome="correct",
        assistance="independent",
    )
    rebuild_index(root=project)
    text = (project / INDEX_DIR_RELATIVE / "知识关联证据.md").read_text(encoding="utf-8")
    assert "K0001" in text
    assert "K0002" in text
    assert "A000001" in text
    assert "correct=1" in text


def test_part_attempt_no_k_association(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0001_x.md",
        pid="P0001",
        extras="parts:\n  - a\n  - b\nknowledge:\n  - K0001\n",
    )
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", aid="A000001", problem="P0001", part="a")
    rebuild_index(root=project)
    text = (project / INDEX_DIR_RELATIVE / "知识关联证据.md").read_text(encoding="utf-8")
    assert "No knowledge-associated evidence available" in text


def test_check_missing_then_sync_current(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0001_x.md",
        pid="P0001",
        extras="knowledge:\n  - K0001\n",
    )
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", aid="A000001", problem="P0001", part=None)
    before = check_index(root=project)
    assert before.result.value in {"MISSING", "STALE"}
    sync_index(root=project)
    assert check_index(root=project).result.value == "CURRENT"


def test_whole_to_part_removes_association(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0001_x.md",
        pid="P0001",
        extras="parts:\n  - a\n  - b\nknowledge:\n  - K0001\n",
    )
    path = write_attempt(
        project,
        "11_学习证据/尝试记录/A000001.md",
        aid="A000001",
        problem="P0001",
        part=None,
    )
    rebuild_index(root=project)
    assert "A000001" in (project / INDEX_DIR_RELATIVE / "知识关联证据.md").read_text(encoding="utf-8")
    write_attempt(
        project,
        "11_学习证据/尝试记录/P0001.md",
        aid="A000001",
        problem="P0001",
        part="a",
    )
    sync_index(root=project)
    assert "No knowledge-associated evidence available" in (
        project / INDEX_DIR_RELATIVE / "知识关联证据.md"
    ).read_text(encoding="utf-8")


def test_outcome_change_stale(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0001_x.md",
        pid="P0001",
        extras="knowledge:\n  - K0001\n",
    )
    path = write_attempt(
        project,
        "11_学习证据/尝试记录/A000001.md",
        aid="A000001",
        problem="P0001",
        part=None,
        outcome="partial",
    )
    rebuild_index(root=project)
    assert check_index(root=project).result.value == "CURRENT"
    path.write_text(path.read_text(encoding="utf-8").replace("outcome: partial", "outcome: correct"), encoding="utf-8")
    assert check_index(root=project).result.value == "STALE"
    sync_index(root=project)
    derived = (project / INDEX_DIR_RELATIVE / "知识关联证据.md").read_text(encoding="utf-8")
    assert "correct=1" in derived


def test_body_only_no_k_diff(project: Path) -> None:
    from tools.attempt_validator import validate_project as validate_attempt_project
    from tools.knowledge_validator import validate_project as validate_knowledge_project
    from tools.method_validator import validate_project as validate_method_project
    from tools.problem_validator import validate_project as validate_problem_project
    from tools.workspace_indexer.builder import build_workspace_snapshot

    write_problem(
        project,
        "02_题目库/研究中/P0001_x.md",
        pid="P0001",
        extras="knowledge:\n  - K0001\n",
    )
    apath = write_attempt(
        project,
        "11_学习证据/尝试记录/A000001.md",
        aid="A000001",
        problem="P0001",
        part=None,
    )
    kr = validate_knowledge_project(root=project)
    pr = validate_problem_project(root=project, knowledge_result=kr)
    ar = validate_attempt_project(root=project, problem_result=pr)
    mr = validate_method_project(root=project, knowledge_result=kr)
    snap1 = build_workspace_snapshot(project, knowledge_result=kr, problem_result=pr, attempt_result=ar, method_result=mr)
    r1 = render_knowledge_associated_evidence(snap1)
    apath.write_text(apath.read_text(encoding="utf-8") + "\nextra body\n", encoding="utf-8")
    ar2 = validate_attempt_project(root=project, problem_result=pr)
    snap2 = build_workspace_snapshot(project, knowledge_result=kr, problem_result=pr, attempt_result=ar2, method_result=mr)
    r2 = render_knowledge_associated_evidence(snap2)
    assert r1 == r2


def test_invalid_attempt_zero_writes(project: Path) -> None:
    write_problem(
        project,
        "02_题目库/研究中/P0001_x.md",
        pid="P0001",
        extras="knowledge:\n  - K0001\n",
    )
    path = write_attempt(
        project,
        "11_学习证据/尝试记录/A000001.md",
        aid="A000001",
        problem="P0001",
        part=None,
    )
    rebuild_index(root=project)
    before = _hashes(project)
    path.write_text(path.read_text(encoding="utf-8").replace("outcome: correct", "outcome: not-valid"), encoding="utf-8")
    op = sync_index(root=project)
    assert op.result.value == "FAIL"
    assert _hashes(project) == before
