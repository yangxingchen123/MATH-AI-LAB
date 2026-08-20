from __future__ import annotations

from pathlib import Path

from tools.knowledge_validator.discovery import (
    DiscoveryError,
    discover_markdown_files,
    find_project_root,
    resolve_project_root,
)

from .conftest import write_project


def test_find_project_root(tmp_path: Path) -> None:
    root = write_project(tmp_path / "proj")
    assert find_project_root(root) == root.resolve()


def test_find_from_subdirectory(tmp_path: Path) -> None:
    root = write_project(tmp_path / "proj")
    sub = root / "01_知识库" / "优化理论"
    sub.mkdir(parents=True)
    assert find_project_root(sub) == root.resolve()


def test_explicit_root(tmp_path: Path) -> None:
    root = write_project(tmp_path / "proj")
    assert resolve_project_root(root) == root.resolve()


def test_invalid_root(tmp_path: Path) -> None:
    bad = tmp_path / "empty"
    bad.mkdir()
    try:
        resolve_project_root(bad)
        assert False, "expected DiscoveryError"
    except DiscoveryError as exc:
        assert exc.rule_id == "K-DISC-001"


def test_discover_excludes_template_and_sorts(tmp_path: Path) -> None:
    root = write_project(tmp_path / "proj")
    kb = root / "01_知识库"
    (kb / "b.md").write_text("# b\n", encoding="utf-8")
    (kb / "a.md").write_text("# a\n", encoding="utf-8")
    nested = kb / "x"
    nested.mkdir()
    (nested / "c.md").write_text("# c\n", encoding="utf-8")
    included, excluded = discover_markdown_files(root)
    assert len(excluded) == 1
    assert excluded[0].name == "知识库模板.md"
    rels = [p.relative_to(root).as_posix() for p in included]
    assert rels == sorted(rels)
    assert "01_知识库/知识库模板.md" not in rels


def test_discover_excludes_generated_index(tmp_path: Path) -> None:
    root = write_project(tmp_path / "proj")
    kb = root / "01_知识库"
    (kb / "real.md").write_text(
        "---\nschema_version: 1\nid: K0001\ntype: knowledge\ntitle: t\n"
        "status: draft\ncreated: 2026-08-19\nupdated: 2026-08-19\n---\n",
        encoding="utf-8",
    )
    index = kb / "_索引"
    index.mkdir()
    (index / "README.md").write_text("# generated\n", encoding="utf-8")
    included, excluded = discover_markdown_files(root)
    rels_inc = [p.relative_to(root).as_posix() for p in included]
    rels_exc = [p.relative_to(root).as_posix() for p in excluded]
    assert "01_知识库/real.md" in rels_inc
    assert "01_知识库/_索引/README.md" in rels_exc
    assert "01_知识库/_索引/README.md" not in rels_inc
