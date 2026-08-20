from __future__ import annotations

from pathlib import Path

from tools.knowledge_indexer.builder import build_index_model
from tools.knowledge_indexer.renderer_markdown import (
    escape_table_cell,
    render_all_markdown,
    render_by_domain,
    render_readme,
    render_relations,
)
from tools.knowledge_validator import validate_project

from .conftest import write_knowledge, write_reviewed_pair


def _model(project: Path):
    result = validate_project(root=project)
    reg = {d.object_id: d for d in result.documents if d.object_id}
    return build_index_model(reg)


def test_readme_banner_and_links(project: Path) -> None:
    write_reviewed_pair(project)
    md = render_readme(_model(project))
    assert "禁止手工维护" in md
    assert "Knowledge Indexer v1.0" in md
    assert "../数学变换/勒让德变换.md" in md
    assert "C:\\" not in md
    assert "Status" in md or "status" in md.lower()


def test_by_domain_and_unset(project: Path) -> None:
    write_reviewed_pair(project)
    write_knowledge(project, "01_知识库/draft.md", kid="K0009", title="草稿")
    text = render_by_domain(_model(project))
    assert "## 凸分析" in text
    assert "K0001" in text and "K0002" in text
    assert "## 未设置 domain" in text
    assert "K0009" in text


def test_relations_columns(project: Path) -> None:
    write_reviewed_pair(project)
    text = render_relations(_model(project))
    assert "Required By" in text
    assert "Related Effective" in text
    assert "K0002" in text


def test_pipe_escaping() -> None:
    assert escape_table_cell("a|b") == "a\\|b"


def test_all_markdown_keys(project: Path) -> None:
    write_reviewed_pair(project)
    files = render_all_markdown(_model(project))
    assert set(files) == {"README.md", "按领域.md", "关系索引.md"}
