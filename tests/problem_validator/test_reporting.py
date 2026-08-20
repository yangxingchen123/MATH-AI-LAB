"""Reporting and JSON tests."""

from __future__ import annotations

import json
from pathlib import Path

from tools.problem_validator.report import format_json
from tools.problem_validator.validator import validate_project
from tests.problem_validator.conftest import knowledge_md, problem_md


def test_json_parseable(project: Path) -> None:
    (project / "01_知识库" / "K0001.md").write_text(
        knowledge_md(kid="K0001"), encoding="utf-8"
    )
    (project / "02_题目库" / "P0001.md").write_text(problem_md(), encoding="utf-8")
    result = validate_project(root=project)
    payload = json.loads(format_json(result))
    assert payload["validator"].startswith("problem_validator")
    assert payload["schema_version"] == 1
    assert "summary" in payload
    assert "dependency" in payload
    assert "issues" in payload
    assert "result" in payload
