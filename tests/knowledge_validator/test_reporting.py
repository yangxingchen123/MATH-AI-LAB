from __future__ import annotations

import json
from pathlib import Path

from tools.knowledge_validator.report import format_json, format_text
from tools.knowledge_validator.validator import validate_project

from .conftest import knowledge_md


def test_duplicate_id_reports_both_paths(project: Path) -> None:
    body = knowledge_md(kid="K0002")
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    (project / "01_知识库" / "b.md").write_text(body, encoding="utf-8")
    r = validate_project(root=project)
    dupes = [i for i in r.issues if i.rule_id == "K-BASE-040"]
    assert len(dupes) >= 2
    paths = {i.file for i in dupes}
    assert "01_知识库/a.md" in paths
    assert "01_知识库/b.md" in paths
    for i in dupes:
        assert i.details["duplicate_id"] == "K0002"
        assert i.details["first_path"]
        assert i.details["second_path"]


def test_json_pass_structure(project: Path) -> None:
    (project / "01_知识库" / "a.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    r = validate_project(root=project)
    payload = json.loads(format_json(r))
    assert payload["validator_version"] == "1.1"
    assert payload["schema"]["schema_version"] == 1
    assert payload["schema"]["status"] == "frozen"
    assert "summary" in payload
    assert isinstance(payload["issues"], list)
    assert payload["summary"]["result"] == "PASS"


def test_json_fail_and_relative_paths(project: Path) -> None:
    (project / "01_知识库" / "a.md").write_text(
        knowledge_md(kid="K0001", extras="prerequisites:\n  - K0099"),
        encoding="utf-8",
    )
    r = validate_project(root=project)
    payload = json.loads(format_json(r))
    assert payload["summary"]["result"] == "FAIL"
    issue = next(i for i in payload["issues"] if i["rule_id"] == "K-REL-001")
    assert issue["file"] == "01_知识库/a.md"
    assert issue["target_id"] == "K0099"


def test_text_report_contains_pass(project: Path) -> None:
    (project / "01_知识库" / "a.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    r = validate_project(root=project)
    text = format_text(r)
    assert "Knowledge Validator v1.1" in text
    assert "PASS" in text
