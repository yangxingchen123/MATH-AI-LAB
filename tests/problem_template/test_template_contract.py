"""Contract tests for 02_题目库/题目模板.md as Frozen Problem Schema v1 authoring scaffold.

These tests do NOT run formal object validation on the template (P0000 is a
sentinel, not a real Problem). Frozen Schema source of truth remains 元数据规范.md;
FROZEN_FIELDS is imported from Problem Validator constants as a stable implementation
contract, not a second schema.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.problem_validator.constants import FROZEN_FIELDS, RESERVED_PROBLEM_ID, TEMPLATE_RELATIVE_PATH
from tools.problem_validator.parser import parse_markdown_file

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = PROJECT_ROOT / TEMPLATE_RELATIVE_PATH

DEFAULT_REQUIRED_FIELDS = (
    "schema_version",
    "id",
    "type",
    "title",
    "status",
    "created",
    "updated",
)

DEFERRED_FIELDS = frozenset({"domain", "source", "problem_type", "aliases", "methods"})

EXCLUDED_FIELDS = frozenset(
    {
        "result",
        "correct",
        "incorrect",
        "mastery",
        "success_rate",
        "mistake_count",
        "last_attempt",
        "last_reviewed",
        "review_due",
        "personal_difficulty",
        "time_spent",
        "hint_used",
        "confidence",
        "intrinsic_difficulty",
        "tags",
        "attempts",
        "error_modes",
        "part_result",
        "part_score",
        "part_correct",
        "parent_problem",
        "child_problem",
        "children",
        "subproblem_ids",
    }
)

LEGACY_SENTINEL_RE = re.compile(r"\bP000\b")


def _parsed():
    assert TEMPLATE_PATH.is_file()
    return parse_markdown_file(TEMPLATE_PATH, PROJECT_ROOT)


def _body() -> str:
    parsed = _parsed()
    return parsed.body


def test_default_yaml_sentinel_and_base_contract() -> None:
    parsed = _parsed()
    assert parsed.data is not None, "template must have YAML Front Matter"
    data = parsed.data
    assert data.get("schema_version") == 1
    assert data.get("id") == RESERVED_PROBLEM_ID
    assert data.get("type") == "problem"
    assert data.get("status") == "draft"
    for field in DEFAULT_REQUIRED_FIELDS:
        assert field in data, f"missing default field: {field}"


def test_legacy_p000_sentinel_absent() -> None:
    parsed = _parsed()
    yaml_id = (parsed.data or {}).get("id")
    assert yaml_id != "P000"
    text = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert LEGACY_SENTINEL_RE.search(text) is None


def test_default_knowledge_omitted() -> None:
    data = _parsed().data
    assert data is not None
    assert "knowledge" not in data


def test_default_parts_omitted() -> None:
    data = _parsed().data
    assert data is not None
    assert "parts" not in data


def test_default_yaml_is_frozen_field_subset() -> None:
    data = _parsed().data
    assert data is not None
    extra = set(data.keys()) - FROZEN_FIELDS
    assert extra == set()


def test_deferred_fields_absent_from_default_yaml() -> None:
    data = _parsed().data
    assert data is not None
    assert DEFERRED_FIELDS.isdisjoint(data.keys())
    raw = parsed_raw_yaml()
    for field in DEFERRED_FIELDS:
        assert not re.search(rf"^#\s*{re.escape(field)}\s*:", raw, re.MULTILINE)


def parsed_raw_yaml() -> str:
    parsed = _parsed()
    assert parsed.raw_yaml is not None
    return parsed.raw_yaml


def test_excluded_fields_absent_from_default_yaml() -> None:
    data = _parsed().data
    assert data is not None
    assert EXCLUDED_FIELDS.isdisjoint(data.keys())


def test_p0000_sentinel_documented() -> None:
    body = _body()
    assert "P0000" in body
    assert "sentinel" in body.lower() or "仅用于模板" in body or "不得实际分配" in body


def test_multipart_documentation_contract() -> None:
    body = _body()
    assert "parts:" in body
    assert "- a" in body and "- b" in body
    assert '"1"' in body and '"2"' in body
    assert "Problem-local" in body or "题目局部" in body
    assert "至少" in body and "2" in body


def test_reviewed_checklist_and_knowledge_empty_semantics() -> None:
    body = _body()
    assert "status: reviewed" in body
    assert "knowledge: []" in body
    assert "mapping" in body.lower() or "映射" in body
    assert "□" in body or "- [ ]" in body


def test_validator_handoff_commands() -> None:
    body = _body()
    assert "python -m tools.problem_validator check-file" in body
    assert "python -m tools.problem_validator check" in body
    assert "problem_candidate_gate" not in body


def test_no_duplicate_body_metadata_headers() -> None:
    body = _body()
    assert "题目编号：" not in body
    assert "对象状态：" not in body
    assert "创建日期：" not in body
