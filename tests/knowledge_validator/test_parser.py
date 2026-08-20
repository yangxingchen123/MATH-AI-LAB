from __future__ import annotations

from tools.knowledge_validator.parser import extract_front_matter, parse_yaml_mapping


def test_valid_yaml() -> None:
    raw = "schema_version: 1\nid: K0001\ntitle: 凸函数\n"
    data, issues = parse_yaml_mapping(raw)
    assert issues == []
    assert data is not None
    assert data["title"] == "凸函数"
    assert data["id"] == "K0001"


def test_yaml_syntax_error() -> None:
    data, issues = parse_yaml_mapping("aliases: [\n  - broken")
    assert data is None
    assert any(i.rule_id == "K-PARSE-001" for i in issues)


def test_missing_closing_delimiter() -> None:
    text = "---\nschema_version: 1\nid: K0001\n"
    raw, issues = extract_front_matter(text)
    assert raw is None
    assert any(i.rule_id == "K-PARSE-002" for i in issues)


def test_root_not_mapping() -> None:
    data, issues = parse_yaml_mapping("- just\n- a\n- list\n")
    assert data is None
    assert any(i.rule_id == "K-PARSE-003" for i in issues)


def test_duplicate_key() -> None:
    data, issues = parse_yaml_mapping("status: draft\nstatus: reviewed\n")
    assert data is None
    assert any(i.rule_id == "K-PARSE-004" for i in issues)


def test_utf8_chinese_title() -> None:
    data, issues = parse_yaml_mapping("title: 勒让德变换\n")
    assert issues == []
    assert data["title"] == "勒让德变换"
