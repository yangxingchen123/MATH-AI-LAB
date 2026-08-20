"""Problem and part relation tests."""

from __future__ import annotations

from pathlib import Path

from tools.attempt_validator.validator import validate_project
from tests.attempt_validator.conftest import (
    attempt_record,
    setup_p0001_no_parts,
    setup_p0002_multipart,
    write_ledger,
    write_single_attempt,
)


def test_part_a_and_b_pass(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [
            attempt_record(aid="A000001", part="a"),
            attempt_record(
                aid="A000002",
                part="b",
                attempted_at="2026-08-19T22:05+08:00",
            ),
        ],
        {"A000001": "body", "A000002": "body"},
    )
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


def test_whole_target_part_omitted(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, part=None)
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


def test_unknown_problem_reference(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, problem="P9999")
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-PROB-E002" for i in result.issues)


def test_unknown_part_reference(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, part="z")
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-PART-E002" for i in result.issues)


def test_part_on_problem_without_parts(attempt_project: Path) -> None:
    setup_p0001_no_parts(attempt_project)
    write_single_attempt(attempt_project, problem="P0001", part="a")
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-PART-E003" for i in result.issues)


def test_part_list_rejected(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    record = attempt_record(part=None)
    record["part"] = ["a", "b"]
    write_ledger(attempt_project, "P0002", [record], {"A000001": "body"})
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-PART-E001" for i in result.issues)


def test_repeated_same_target_allowed(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [
            attempt_record(aid="A000002", part="a", outcome="partial"),
            attempt_record(
                aid="A000015",
                part="a",
                outcome="correct",
                attempted_at="2026-08-20T10:00+08:00",
            ),
        ],
        {"A000002": "body", "A000015": "body"},
    )
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0
