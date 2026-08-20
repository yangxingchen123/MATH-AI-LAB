from __future__ import annotations

from pathlib import Path

from tools.knowledge_indexer.builder import build_index_model
from tools.knowledge_indexer.service import render_snapshot
from tools.knowledge_validator import validate_project

from .conftest import write_reviewed_pair


def test_builder_counts(project: Path) -> None:
    write_reviewed_pair(project)
    result = validate_project(root=project)
    reg = {d.object_id: d for d in result.documents if d.object_id}
    model = build_index_model(reg)
    assert model.knowledge_objects == 2
    assert model.status_counts["reviewed"] == 2
    assert model.prerequisite_edges == 1
    assert model.domains["凸分析"] == ["K0001", "K0002"]


def test_determinism_snapshot(project: Path) -> None:
    write_reviewed_pair(project)
    result = validate_project(root=project)
    reg = {d.object_id: d for d in result.documents if d.object_id}
    m1 = build_index_model(reg)
    m2 = build_index_model(reg)
    assert render_snapshot(m1).files == render_snapshot(m2).files
