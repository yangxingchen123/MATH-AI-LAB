"""Discovery tests for Problem Validator v1."""

from __future__ import annotations

from pathlib import Path

from tools.problem_validator.discovery import discover_markdown_files, is_template_file
from tests.problem_validator.conftest import problem_md, write_project


def test_recursive_md_discovery(project: Path) -> None:
    nested = project / "02_题目库" / "未解决"
    nested.mkdir(parents=True, exist_ok=True)
    (nested / "P0001_a.md").write_text(problem_md(), encoding="utf-8")
    included, excluded = discover_markdown_files(project)
    assert len(included) == 1
    assert len(excluded) == 1
    assert is_template_file(excluded[0], project)


def test_template_excluded(project: Path) -> None:
    included, excluded = discover_markdown_files(project)
    assert len(included) == 0
    assert len(excluded) == 1
    assert excluded[0].name == "题目模板.md"


def test_deterministic_order(project: Path) -> None:
    base = project / "02_题目库"
    (base / "z.md").write_text(problem_md(pid="P0002"), encoding="utf-8")
    (base / "a.md").write_text(problem_md(pid="P0001"), encoding="utf-8")
    included, _ = discover_markdown_files(project)
    rels = [p.name for p in included]
    assert rels == ["a.md", "z.md"]


def test_filename_does_not_need_match_pid(project: Path) -> None:
    base = project / "02_题目库"
    (base / "legacy_name.md").write_text(problem_md(pid="P0001"), encoding="utf-8")
    included, _ = discover_markdown_files(project)
    assert included[0].name == "legacy_name.md"
