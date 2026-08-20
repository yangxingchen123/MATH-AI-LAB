"""Registry and duplicate ID tests."""

from __future__ import annotations

from pathlib import Path

from tools.problem_validator.validator import validate_project
from tests.problem_validator.conftest import knowledge_md, problem_md


def _setup(project: Path) -> None:
    kb = project / "01_知识库"
    (kb / "K0001.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    base = project / "02_题目库"
    (base / "a.md").write_text(problem_md(pid="P0001"), encoding="utf-8")
    (base / "b.md").write_text(problem_md(pid="P0001", title="dup"), encoding="utf-8")


def test_duplicate_id_reports_all_paths(project: Path) -> None:
    _setup(project)
    result = validate_project(root=project)
    dup_issues = [i for i in result.issues if i.rule_id == "P-ID-E001"]
    assert len(dup_issues) == 2
    files = dup_issues[0].details.get("files")
    assert "02_题目库/a.md" in files
    assert "02_题目库/b.md" in files


def test_registry_keeps_all_documents(project: Path) -> None:
    _setup(project)
    result = validate_project(root=project)
    assert len(result.documents) == 2
    assert len(result.registry["P0001"]) == 2
