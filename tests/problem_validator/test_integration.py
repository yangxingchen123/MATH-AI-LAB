"""Integration tests."""

from __future__ import annotations

from pathlib import Path

from tools.problem_validator.validator import validate_project
from tests.problem_validator.conftest import knowledge_md, problem_md


def test_strict_data_dir_no_front_matter_error(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    foo = project / "02_题目库" / "未解决" / "foo.md"
    foo.parent.mkdir(parents=True, exist_ok=True)
    foo.write_text("# no yaml\n", encoding="utf-8")
    result = validate_project(root=project)
    assert any(i.rule_id == "P-PARSE-E005" for i in result.issues)


def test_source_bytes_unchanged(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    path = project / "02_题目库" / "P0001.md"
    content = problem_md()
    path.write_text(content, encoding="utf-8")
    before = path.read_bytes()
    validate_project(root=project)
    assert path.read_bytes() == before
