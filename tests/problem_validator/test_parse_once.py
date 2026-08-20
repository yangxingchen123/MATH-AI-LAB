"""Parse-once regression test."""

from __future__ import annotations

from pathlib import Path

from tools.problem_validator import validator as validator_module
from tools.problem_validator.validator import set_parse_markdown_file_for_tests, validate_project
from tests.problem_validator.conftest import knowledge_md, problem_md


def test_validate_project_parses_each_file_once(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "02_题目库" / "P0001.md").write_text(problem_md(), encoding="utf-8")
    (project / "02_题目库" / "P0002.md").write_text(
        problem_md(pid="P0002", extras="parts:\n  - a\n  - b"), encoding="utf-8"
    )

    counts: dict[str, int] = {}
    original = validator_module.parse_markdown_file

    def counting_parse(path: Path, project_root: Path):
        key = str(path.resolve())
        counts[key] = counts.get(key, 0) + 1
        return original(path, project_root)

    set_parse_markdown_file_for_tests(counting_parse)
    try:
        validate_project(root=project)
    finally:
        set_parse_markdown_file_for_tests(None)

    assert all(c == 1 for c in counts.values())
    assert len(counts) == 2
