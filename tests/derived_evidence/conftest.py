"""Fixtures for derived evidence tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.attempt_validator.models import AttemptDocument
from tools.problem_validator.models import ProblemDocument
from tools.attempt_validator import validate_project as validate_attempt_project
from tools.problem_validator import validate_project as validate_problem_project
from tools.knowledge_validator import validate_project as validate_knowledge_project


@pytest.fixture
def project(tmp_path: Path) -> Path:
    from tests.knowledge_indexer.conftest import write_reviewed_pair
    from tests.workspace_indexer.conftest import ensure_method_root, write_project

    root = write_project(tmp_path)
    write_reviewed_pair(root)
    ensure_method_root(root)
    return root


def validated_registries(project: Path):
    kr = validate_knowledge_project(root=project)
    pr = validate_problem_project(root=project, knowledge_result=kr)
    ar = validate_attempt_project(root=project, problem_result=pr)
    return pr, ar


def attempt_doc(
    *,
    aid: str = "A000001",
    problem: str = "P0002",
    part: str | None = "b",
    outcome: str = "correct",
    assistance: str | None = "assisted",
) -> AttemptDocument:
    data: dict = {
        "schema_version": 1,
        "id": aid,
        "type": "attempt",
        "problem": problem,
        "outcome": outcome,
        "attempted_at": "2026-08-19T21:36+08:00",
    }
    if part is not None:
        data["part"] = part
    if assistance is not None:
        data["assistance"] = assistance
    return AttemptDocument(
        path=Path(f"/fake/{aid}.md"),
        relative_path=f"11_学习证据/尝试记录/{aid}.md",
        data=data,
        body="body",
        object_id=aid,
    )


def problem_doc(
    *,
    pid: str = "P0002",
    parts: list[str] | None = None,
    knowledge: list[str] | None = None,
) -> ProblemDocument:
    data: dict = {
        "schema_version": 1,
        "id": pid,
        "type": "problem",
        "title": "Test",
        "status": "draft",
    }
    if parts is not None:
        data["parts"] = parts
    if knowledge is not None:
        data["knowledge"] = knowledge
    return ProblemDocument(
        path=Path(f"/fake/{pid}.md"),
        relative_path=f"02_题目库/研究中/{pid}.md",
        data=data,
        body="body",
        object_id=pid,
        status="draft",
    )
