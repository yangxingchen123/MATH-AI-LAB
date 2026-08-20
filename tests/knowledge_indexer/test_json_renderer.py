from __future__ import annotations

import json
from pathlib import Path

from tools.knowledge_indexer.builder import build_index_model, compute_source_metadata_sha256
from tools.knowledge_indexer.renderer_json import render_json
from tools.knowledge_validator import validate_project

from .conftest import write_knowledge, write_reviewed_pair


def _model(project: Path):
    result = validate_project(root=project)
    assert result.summary.result == "PASS"
    reg = {d.object_id: d for d in result.documents if d.object_id}
    return build_index_model(reg), reg


def test_json_valid_and_chinese(project: Path) -> None:
    write_reviewed_pair(project)
    model, _ = _model(project)
    text = render_json(model)
    assert "\\u" not in text or "凸分析" in text
    assert "凸分析" in text
    payload = json.loads(text)
    assert payload["index_version"] == 1
    assert list(payload["knowledge"].keys()) == ["K0001", "K0002"]


def test_relative_path_and_required_by(project: Path) -> None:
    write_reviewed_pair(project)
    model, _ = _model(project)
    payload = json.loads(render_json(model))
    assert payload["knowledge"]["K0001"]["path"].startswith("01_知识库/")
    assert not Path(payload["knowledge"]["K0001"]["path"]).is_absolute()
    assert payload["knowledge"]["K0001"]["metadata"]["prerequisites"] == ["K0002"]
    assert payload["knowledge"]["K0002"]["derived"]["required_by"] == ["K0001"]
    assert payload["knowledge"]["K0001"]["derived"]["related_effective"] == []
    assert payload["knowledge"]["K0001"]["metadata"]["related"] == []


def test_draft_null_vs_reviewed_empty(project: Path) -> None:
    write_knowledge(project, "01_知识库/d.md", kid="K0005", status="draft")
    model, _ = _model(project)
    meta = model.entries["K0005"].metadata_dict()
    assert meta["domain"] is None
    assert meta["prerequisites"] is None
    assert meta["related"] is None
    assert meta["aliases"] is None


def test_sha256_stable_and_deterministic_render(project: Path) -> None:
    write_reviewed_pair(project)
    model1, reg = _model(project)
    model2, _ = _model(project)
    assert compute_source_metadata_sha256(reg) == model1.source_metadata_sha256
    assert render_json(model1) == render_json(model2)
    assert "generated_at" not in render_json(model1)
