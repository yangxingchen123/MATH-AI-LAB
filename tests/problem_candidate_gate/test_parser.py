from tools.problem_candidate_gate.parser import extract_front_matter, parse_yaml_mapping


def test_valid_yaml() -> None:
    text = "---\nschema_version: 1\nid: P0001\ntitle: 中文标题\n---\n\nbody\n"
    raw, body, issues = extract_front_matter(text)
    assert issues == []
    data, parse_issues = parse_yaml_mapping(raw or "")
    assert parse_issues == []
    assert data["title"] == "中文标题"
    assert "body" in body


def test_invalid_yaml() -> None:
    data, issues = parse_yaml_mapping(":\n  -")
    assert data is None
    assert any(i.rule_id == "PCG-PARSE-001" for i in issues)


def test_missing_closing_delimiter() -> None:
    raw, _, issues = extract_front_matter("---\nid: P0001\n")
    assert raw is None
    assert any(i.rule_id == "PCG-PARSE-002" for i in issues)


def test_root_not_mapping() -> None:
    data, issues = parse_yaml_mapping("- a\n- b\n")
    assert data is None
    assert any(i.rule_id == "PCG-PARSE-003" for i in issues)


def test_duplicate_key() -> None:
    data, issues = parse_yaml_mapping("id: P0001\nid: P0002\n")
    assert data is None
    assert any(i.rule_id == "PCG-PARSE-004" for i in issues)


def test_chinese_title() -> None:
    data, issues = parse_yaml_mapping("title: 线性映射 φ 的谱\n")
    assert issues == []
    assert data["title"] == "线性映射 φ 的谱"
