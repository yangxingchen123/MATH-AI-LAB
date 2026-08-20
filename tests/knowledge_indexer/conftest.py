"""Fixtures for Knowledge Indexer tests."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from tests.knowledge_validator.conftest import knowledge_md, write_project


@pytest.fixture
def project(tmp_path: Path) -> Path:
    return write_project(tmp_path)


def write_knowledge(
    project: Path,
    relative: str,
    *,
    kid: str,
    title: str = "示例",
    status: str = "draft",
    aliases: str | None = None,
    extras: str = "",
) -> Path:
    path = project / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        knowledge_md(
            kid=kid,
            title=title,
            status=status,
            aliases=aliases,
            extras=extras,
        ),
        encoding="utf-8",
    )
    return path


def write_reviewed_pair(project: Path) -> None:
    write_knowledge(
        project,
        "01_知识库/优化理论/凸函数.md",
        kid="K0002",
        title="凸函数",
        status="reviewed",
        aliases="Convex function",
        extras="domain: 凸分析\nprerequisites: []\nrelated: []",
    )
    write_knowledge(
        project,
        "01_知识库/数学变换/勒让德变换.md",
        kid="K0001",
        title="勒让德变换",
        status="reviewed",
        aliases="Legendre transform",
        extras="domain: 凸分析\nprerequisites:\n  - K0002\nrelated: []",
    )
