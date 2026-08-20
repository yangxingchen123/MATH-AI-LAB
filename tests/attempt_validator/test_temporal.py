"""Frozen Temporal Contract tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.attempt_validator.ledger import serialize_ledger
from tools.attempt_validator.validator import validate_project
from tests.attempt_validator.conftest import attempt_record, setup_p0002_multipart, write_single_attempt


@pytest.mark.parametrize(
    "attempted_at",
    ["2026-08-19T22:05+08:00", "2026-08-19T14:05+00:00"],
)
def test_form_a_valid(attempt_project: Path, attempted_at: str) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, attempted_at=attempted_at)
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


def test_form_b_valid(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, attempted_at="2026-08-19")
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


@pytest.mark.parametrize(
    "attempted_at",
    [
        "2026-08-19T22:05",
        "2026-08-19T22:05Z",
        "2026-08-19T22:05:00+08:00",
        "2026-02-30",
        "2025-02-29",
        "2026-13-01",
    ],
)
def test_temporal_invalid(attempt_project: Path, attempted_at: str) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, attempted_at=attempted_at)
    result = validate_project(root=attempt_project)
    assert any(i.rule_id.startswith("A-TEMP-") for i in result.issues)


def test_native_yaml_date_rejected(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    root = attempt_project / "11_学习证据" / "尝试记录" / "P0002.md"
    root.write_text(
        """---
storage_format: problem_attempt_ledger_v1
problem: P0002
attempts:
  - schema_version: 1
    id: A000001
    type: attempt
    problem: P0002
    part: b
    outcome: correct
    assistance: assisted
    attempted_at: 2026-08-19
---

# P0002 尝试记录

## A000001

body
""",
        encoding="utf-8",
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-TEMP-E001" for i in result.issues)
