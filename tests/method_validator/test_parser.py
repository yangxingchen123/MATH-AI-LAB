"""Parser tests for Method Validator v1."""

from __future__ import annotations

from pathlib import Path

from tools.method_validator.parser import extract_front_matter, parse_markdown_file, parse_yaml_mapping


def test_duplicate_yaml_key() -> None:
    data, issues = parse_yaml_mapping("id: M0001\nid: M0002\n")
    assert data is None
    assert any(i.rule_id == "M-PARSE-E004" for i in issues)


def test_missing_closing_delimiter(tmp_path: Path) -> None:
    path = tmp_path / "M0001.md"
    path.write_text("---\nid: M0001\n", encoding="utf-8")
    result = parse_markdown_file(path, tmp_path)
    assert any(i.rule_id == "M-PARSE-E002" for i in result.issues)


def test_missing_front_matter(tmp_path: Path) -> None:
    path = tmp_path / "M0001.md"
    path.write_text("# no yaml\n", encoding="utf-8")
    result = parse_markdown_file(path, tmp_path)
    assert any(i.rule_id == "M-PARSE-E005" for i in result.issues)


def test_body_preserved(tmp_path: Path) -> None:
    path = tmp_path / "M0001.md"
    path.write_text(
        "---\nschema_version: 1\nid: M0001\ntype: method\ntitle: t\nstatus: draft\n---\n\n# custom\n",
        encoding="utf-8",
    )
    result = parse_markdown_file(path, tmp_path)
    assert result.body.startswith("\n# custom")


def test_extract_no_front_matter() -> None:
    raw, body, issues = extract_front_matter("# heading only\n")
    assert raw is None
    assert issues == []
