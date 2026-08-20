from pathlib import Path

from tools.problem_candidate_gate.constants import MANUAL_REVIEW_ITEMS
from tools.problem_candidate_gate.readiness import status_project

from .conftest import problem_md


def test_ready_for_final_review(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(status="reviewed", extras="knowledge: []"), encoding="utf-8"
    )
    r = status_project(root=project)
    assert r.readiness == "READY_FOR_FINAL_REVIEW"
    assert r.summary.errors == 0
    assert r.summary.warnings == 0
    assert r.manual_review_items == list(MANUAL_REVIEW_ITEMS)


def test_ready_with_warnings(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(
        problem_md(body="Candidate Content Review: PENDING\n"), encoding="utf-8"
    )
    r = status_project(root=project)
    assert r.readiness == "READY_WITH_WARNINGS"
    assert r.manual_review_items


def test_not_ready_on_error(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(pid="P0000"), encoding="utf-8")
    r = status_project(root=project)
    assert r.readiness == "NOT_READY"


def test_manual_review_always_listed(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    r = status_project(root=project)
    assert "parts 是否应 Frozen 进入 Problem v1" in r.manual_review_items
    assert len(r.manual_review_items) >= 6
