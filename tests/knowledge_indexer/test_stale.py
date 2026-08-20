from __future__ import annotations

from pathlib import Path

from tools.knowledge_indexer.models import IndexResultKind
from tools.knowledge_indexer.service import build_index, check_index

from .conftest import write_reviewed_pair


def test_missing_index(project: Path) -> None:
    write_reviewed_pair(project)
    op = check_index(root=project)
    assert op.result == IndexResultKind.MISSING
    assert any(i.rule_id == "KI-STALE-001" for i in op.issues)


def test_current_after_build(project: Path) -> None:
    write_reviewed_pair(project)
    assert build_index(root=project).result == IndexResultKind.BUILT
    op = check_index(root=project)
    assert op.result == IndexResultKind.CURRENT


def test_missing_readme_stale(project: Path) -> None:
    write_reviewed_pair(project)
    build_index(root=project)
    (project / "01_知识库" / "_索引" / "README.md").unlink()
    op = check_index(root=project)
    assert op.result == IndexResultKind.STALE
    assert any(i.rule_id == "KI-STALE-001" for i in op.issues)


def test_json_tampered_stale(project: Path) -> None:
    write_reviewed_pair(project)
    build_index(root=project)
    path = project / "01_知识库" / "_索引" / "knowledge_index.json"
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    op = check_index(root=project)
    assert op.result == IndexResultKind.STALE
    assert any(i.rule_id == "KI-STALE-002" for i in op.issues)


def test_unexpected_file_stale(project: Path) -> None:
    write_reviewed_pair(project)
    build_index(root=project)
    (project / "01_知识库" / "_索引" / "extra.txt").write_text("x", encoding="utf-8")
    op = check_index(root=project)
    assert op.result == IndexResultKind.STALE
    assert any(i.rule_id == "KI-STALE-003" for i in op.issues)


def test_source_change_stale(project: Path) -> None:
    write_reviewed_pair(project)
    build_index(root=project)
    path = project / "01_知识库" / "优化理论" / "凸函数.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("title: 凸函数", "title: 凸函数改"), encoding="utf-8")
    op = check_index(root=project)
    assert op.result == IndexResultKind.STALE
