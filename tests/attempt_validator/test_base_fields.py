"""Valid real records and base field tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.attempt_validator.validator import validate_project
from tests.attempt_validator.conftest import (
    attempt_record,
    setup_p0002_multipart,
    write_ledger,
    write_single_attempt,
)


def test_a000001_style_passes(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(
        attempt_project,
        aid="A000001",
        part="b",
        outcome="correct",
        assistance="assisted",
    )
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0
    assert "A000001" in result.registry


def test_a000002_style_passes(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(
        attempt_project,
        aid="A000002",
        part="a",
        outcome="partial",
        assistance="independent",
        attempted_at="2026-08-19T22:05+08:00",
    )
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


@pytest.mark.parametrize(
    "field_name",
    ["schema_version", "id", "type", "problem", "outcome", "attempted_at"],
)
def test_missing_required_field(attempt_project: Path, field_name: str) -> None:
    setup_p0002_multipart(attempt_project)
    record = attempt_record()
    del record[field_name]
    root = attempt_project / "11_学习证据" / "尝试记录" / "P0002.md"
    if field_name == "id":
        root.write_text(
            """---
storage_format: problem_attempt_ledger_v1
problem: P0002
attempts:
  - schema_version: 1
    type: attempt
    problem: P0002
    part: b
    outcome: correct
    assistance: assisted
    attempted_at: '2026-08-19T21:36+08:00'
---

# P0002 尝试记录

## A000001

body
""",
            encoding="utf-8",
        )
    else:
        write_ledger(attempt_project, "P0002", [record], {"A000001": "body"})
    result = validate_project(root=attempt_project)
    assert result.summary.errors > 0
    assert any(i.field == field_name for i in result.issues)


def test_unknown_field_status(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [attempt_record(extras={"status": "reviewed"})],
        {"A000001": "body"},
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-FIELD-E001" for i in result.issues)


def test_schema_version_boolean_rejected(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    record = attempt_record()
    record["schema_version"] = True
    write_ledger(attempt_project, "P0002", [record], {"A000001": "body"})
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-BASE-E002" for i in result.issues)
