from __future__ import annotations

from pathlib import Path

from tools.knowledge_indexer.models import IndexResultKind
from tools.knowledge_indexer.service import build_index, check_index
from tools.knowledge_validator import validate_project

from .conftest import knowledge_md, write_knowledge, write_reviewed_pair


def test_validator_failure_preserves_old_index(project: Path) -> None:
    write_reviewed_pair(project)
    assert build_index(root=project).result == IndexResultKind.BUILT
    index = project / "01_知识库" / "_索引"
    old = (index / "README.md").read_text(encoding="utf-8")

    # Add invalid reviewed (missing domain)
    write_knowledge(
        project,
        "01_知识库/bad.md",
        kid="K0009",
        status="reviewed",
        aliases="",
        extras="prerequisites: []\nrelated: []",
    )
    op = build_index(root=project)
    assert op.result == IndexResultKind.FAIL
    assert any(i.rule_id == "KI-VALIDATE-001" for i in op.issues)
    assert (index / "README.md").read_text(encoding="utf-8") == old


def test_invalid_id_blocked_by_validator(project: Path) -> None:
    write_knowledge(project, "01_知识库/bad.md", kid="K00A1")
    op = build_index(root=project)
    assert op.result == IndexResultKind.FAIL
    assert not (project / "01_知识库" / "_索引").exists()


def test_up_to_date_second_build(project: Path) -> None:
    write_reviewed_pair(project)
    assert build_index(root=project).result == IndexResultKind.BUILT
    assert build_index(root=project).result == IndexResultKind.UP_TO_DATE


def test_source_protection(project: Path) -> None:
    write_reviewed_pair(project)
    sources = {
        p: p.read_bytes()
        for p in (project / "01_知识库").rglob("*.md")
        if "_索引" not in p.parts and p.name != "知识库模板.md"
    }
    build_index(root=project)
    for p, content in sources.items():
        assert p.read_bytes() == content


def test_build_then_check_current(project: Path) -> None:
    write_reviewed_pair(project)
    build_index(root=project)
    assert check_index(root=project).result == IndexResultKind.CURRENT
    assert validate_project(root=project).summary.result == "PASS"
