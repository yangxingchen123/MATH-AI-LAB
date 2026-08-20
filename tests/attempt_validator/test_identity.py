"""Attempt ID and duplicate ID tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.attempt_validator.validator import validate_project
from tests.attempt_validator.conftest import (
    attempt_record,
    setup_p0001_no_parts,
    setup_p0002_multipart,
    write_ledger,
    write_single_attempt,
)


@pytest.mark.parametrize(
    "aid,should_pass",
    [
        ("A000001", True),
        ("A000000", False),
        ("A00001", False),
        ("A1234567", False),
        ("P000001", False),
    ],
)
def test_id_format(attempt_project: Path, aid: str, should_pass: bool) -> None:
    setup_p0002_multipart(attempt_project)
    record = attempt_record(aid=aid)
    write_ledger(attempt_project, "P0002", [record], {aid: "body"})
    result = validate_project(root=attempt_project)
    if should_pass:
        assert result.summary.errors == 0
    else:
        assert result.summary.errors > 0
        assert any(
            i.rule_id in {"A-BASE-E010", "A-BASE-E011", "A-LEDG-E007", "A-BASE-E030"}
            for i in result.issues
        )


def test_duplicate_attempt_id(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    setup_p0001_no_parts(attempt_project)
    write_single_attempt(attempt_project, aid="A000010", problem="P0002", part="b")
    write_single_attempt(
        attempt_project,
        aid="A000010",
        problem="P0001",
        part=None,
        attempted_at="2026-08-19T22:00+08:00",
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-ID-E001" for i in result.issues)


def test_wrong_type(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    record = attempt_record()
    record["type"] = "problem"
    write_ledger(attempt_project, "P0002", [record], {"A000001": "body"})
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-BASE-E021" for i in result.issues)
