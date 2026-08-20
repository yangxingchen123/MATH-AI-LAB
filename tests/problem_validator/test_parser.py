"""Parser tests for Problem Validator v1."""

from __future__ import annotations

from pathlib import Path

from tools.problem_validator.parser import parse_markdown_file
from tests.problem_validator.conftest import problem_md, write_project


def test_valid_front_matter(project: Path) -> None:
    path = project / "02_题目库" / "p.md"
    path.write_text(problem_md(title="中文标题"), encoding="utf-8")
    parsed = parse_markdown_file(path, project)
    assert parsed.data is not None
    assert parsed.data["title"] == "中文标题"
    assert not parsed.issues


def test_malformed_yaml(project: Path) -> None:
    path = project / "02_题目库" / "bad.md"
    path.write_text("---\nschema_version: [\n---\n", encoding="utf-8")
    parsed = parse_markdown_file(path, project)
    assert any(i.rule_id == "P-PARSE-E001" for i in parsed.issues)


def test_missing_closing_delimiter(project: Path) -> None:
    path = project / "02_题目库" / "bad.md"
    path.write_text("---\nid: P0001\n", encoding="utf-8")
    parsed = parse_markdown_file(path, project)
    assert any(i.rule_id == "P-PARSE-E002" for i in parsed.issues)


def test_yaml_root_non_mapping(project: Path) -> None:
    path = project / "02_题目库" / "bad.md"
    path.write_text("---\n- item\n---\n", encoding="utf-8")
    parsed = parse_markdown_file(path, project)
    assert any(i.rule_id == "P-PARSE-E003" for i in parsed.issues)


def test_duplicate_key(project: Path) -> None:
    path = project / "02_题目库" / "bad.md"
    path.write_text(
        "---\nid: P0001\nid: P0002\ntype: problem\ntitle: t\nstatus: draft\n"
        "schema_version: 1\ncreated: 2026-08-19\nupdated: 2026-08-19\n---\n",
        encoding="utf-8",
    )
    parsed = parse_markdown_file(path, project)
    assert any(i.rule_id == "P-PARSE-E004" for i in parsed.issues)


def test_missing_front_matter_strict_error(project: Path) -> None:
    path = project / "02_题目库" / "未解决" / "foo.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# no yaml\n", encoding="utf-8")
    parsed = parse_markdown_file(path, project)
    assert any(i.rule_id == "P-PARSE-E005" for i in parsed.issues)
