from __future__ import annotations

from pathlib import Path

from tools.knowledge_indexer.builder import build_index_model
from tools.knowledge_indexer.relations import (
    compute_related_effective,
    compute_required_by,
)
from tools.knowledge_validator import validate_project

from .conftest import write_knowledge, write_reviewed_pair


def _registry(project: Path):
    result = validate_project(root=project)
    assert result.summary.errors == 0
    reg = {}
    for doc in result.documents:
        if doc.object_id:
            reg[doc.object_id] = doc
    return reg


def test_required_by_from_prerequisites(project: Path) -> None:
    write_reviewed_pair(project)
    reg = _registry(project)
    rb = compute_required_by(reg)
    assert rb["K0002"] == ["K0001"]
    assert rb["K0001"] == []


def test_related_effective_symmetric(project: Path) -> None:
    write_knowledge(
        project,
        "01_知识库/a.md",
        kid="K0003",
        extras="related:\n  - K0004",
    )
    write_knowledge(project, "01_知识库/b.md", kid="K0004")
    reg = _registry(project)
    eff = compute_related_effective(reg)
    assert eff["K0003"] == ["K0004"]
    assert eff["K0004"] == ["K0003"]


def test_related_effective_dedup_both_sides(project: Path) -> None:
    write_knowledge(
        project,
        "01_知识库/a.md",
        kid="K0003",
        extras="related:\n  - K0004",
    )
    write_knowledge(
        project,
        "01_知识库/b.md",
        kid="K0004",
        extras="related:\n  - K0003",
    )
    reg = _registry(project)
    eff = compute_related_effective(reg)
    assert eff["K0003"] == ["K0004"]
    assert eff["K0004"] == ["K0003"]
    model = build_index_model(reg)
    assert model.related_effective_edges == 1


def test_no_relations_empty_derived(project: Path) -> None:
    write_knowledge(project, "01_知识库/a.md", kid="K0001")
    reg = _registry(project)
    model = build_index_model(reg)
    assert model.entries["K0001"].required_by == []
    assert model.entries["K0001"].related_effective == []
