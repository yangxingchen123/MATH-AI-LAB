"""Integration tests for Method Validator v1."""

from __future__ import annotations

from pathlib import Path

from tools.method_validator.discovery import discover_markdown_files
from tools.method_validator.validator import validate_project
from tests.method_validator.conftest import knowledge_md, method_md


def test_discovery_only_method_root(project: Path) -> None:
    (project / "other.md").write_text("# stray", encoding="utf-8")
    (project / "12_方法库" / "M0001.md").write_text(method_md(), encoding="utf-8")
    paths = discover_markdown_files(project)
    assert len(paths) == 1
    assert paths[0].name == "M0001.md"


def test_project_error_clears_registry(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    base = project / "12_方法库"
    (base / "good.md").write_text(method_md(mid="M0001"), encoding="utf-8")
    (base / "bad.md").write_text(method_md(mid="M0000"), encoding="utf-8")
    result = validate_project(root=project)
    assert result.summary.result == "FAIL"
    assert result.registry == {}
