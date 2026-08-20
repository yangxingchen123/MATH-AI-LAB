"""Registry and duplicate ID tests."""

from __future__ import annotations

from pathlib import Path

from tools.method_validator.validator import validate_project
from tests.method_validator.conftest import knowledge_md, method_md


def _setup(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    base = project / "12_方法库"
    (base / "a.md").write_text(method_md(mid="M0001"), encoding="utf-8")
    (base / "b.md").write_text(method_md(mid="M0001", title="dup"), encoding="utf-8")


def test_duplicate_id_reports_all_paths(project: Path) -> None:
    _setup(project)
    result = validate_project(root=project)
    dup_issues = [i for i in result.issues if i.rule_id == "M-ID-E001"]
    assert len(dup_issues) == 2
    files = dup_issues[0].details.get("files")
    assert "12_方法库/a.md" in files
    assert "12_方法库/b.md" in files
    assert result.registry == {}


def test_registry_only_on_pass(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "12_方法库" / "M0001.md").write_text(method_md(mid="M0001"), encoding="utf-8")
    (project / "12_方法库" / "M0002.md").write_text(
        method_md(mid="M0002", title="second"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert result.summary.errors == 0
    assert set(result.registry.keys()) == {"M0001", "M0002"}


def test_draft_in_registry(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "12_方法库" / "M0001.md").write_text(
        method_md(mid="M0001", status="draft"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert result.summary.errors == 0
    assert "M0001" in result.registry
    assert result.registry["M0001"].status == "draft"


def test_body_without_headings_passes(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "12_方法库" / "M0001.md").write_text(
        method_md(body="plain text only\n"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert result.summary.errors == 0
