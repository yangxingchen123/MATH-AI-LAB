"""Fixtures for knowledge_relations tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.knowledge_validator.models import KnowledgeDocument
from tools.method_validator.models import MethodDocument
from tools.problem_validator.models import ProblemDocument


@pytest.fixture
def knowledge_registry() -> dict[str, KnowledgeDocument]:
    return {
        "K0001": KnowledgeDocument(
            path=Path("/fake/K0001.md"),
            relative_path="01_知识库/a/K0001.md",
            data={
                "id": "K0001",
                "type": "knowledge",
                "title": "Alpha",
                "prerequisites": ["K0002"],
                "related": [],
            },
            object_id="K0001",
            status="reviewed",
            prerequisites=["K0002"],
            related=[],
        ),
        "K0002": KnowledgeDocument(
            path=Path("/fake/K0002.md"),
            relative_path="01_知识库/b/K0002.md",
            data={
                "id": "K0002",
                "type": "knowledge",
                "title": "Beta",
                "prerequisites": [],
                "related": ["K0001"],
            },
            object_id="K0002",
            status="reviewed",
            prerequisites=[],
            related=["K0001"],
        ),
    }


def problem_doc(
    *,
    pid: str,
    knowledge: list[str] | None = None,
) -> ProblemDocument:
    data: dict = {
        "schema_version": 1,
        "id": pid,
        "type": "problem",
        "title": "Problem",
        "status": "reviewed",
    }
    if knowledge is not None:
        data["knowledge"] = knowledge
    return ProblemDocument(
        path=Path(f"/fake/{pid}.md"),
        relative_path=f"02_题目库/已解决/{pid}.md",
        data=data,
        object_id=pid,
        status="reviewed",
    )


def method_doc(
    *,
    mid: str,
    knowledge: list[str] | None = None,
) -> MethodDocument:
    data: dict = {
        "schema_version": 1,
        "id": mid,
        "type": "method",
        "title": "Method",
        "status": "draft",
    }
    if knowledge is not None:
        data["knowledge"] = knowledge
    return MethodDocument(
        path=Path(f"/fake/{mid}.md"),
        relative_path=f"12_方法库/{mid}.md",
        data=data,
        object_id=mid,
        status="draft",
    )
