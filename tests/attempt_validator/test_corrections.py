"""Corrections validation tests."""

from __future__ import annotations

from pathlib import Path

from tools.attempt_validator.validator import validate_project
from tests.attempt_validator.conftest import attempt_record, setup_p0002_multipart, write_ledger


def test_corrections_valid_date_only(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [
            attempt_record(
                extras={
                    "corrections": [{"at": "2026-08-20", "note": "修正说明"}],
                }
            )
        ],
        {"A000001": "body"},
    )
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


def test_corrections_valid_form_a(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [
            attempt_record(
                extras={
                    "corrections": [
                        {"at": "2026-08-20T10:20+08:00", "note": "修正说明"},
                    ],
                }
            )
        ],
        {"A000001": "body"},
    )
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


def test_corrections_empty_list(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [attempt_record(extras={"corrections": []})],
        {"A000001": "body"},
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-CORR-E001" for i in result.issues)


def test_corrections_extra_key(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [
            attempt_record(
                extras={
                    "corrections": [
                        {"at": "2026-08-20", "note": "x", "author": "user"},
                    ],
                }
            )
        ],
        {"A000001": "body"},
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-CORR-E003" for i in result.issues)


def test_corrections_missing_note(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [attempt_record(extras={"corrections": [{"at": "2026-08-20"}]})],
        {"A000001": "body"},
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-CORR-E004" for i in result.issues)


def test_corrections_blank_note(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [
            attempt_record(
                extras={
                    "corrections": [{"at": "2026-08-20", "note": "   "}],
                }
            )
        ],
        {"A000001": "body"},
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-CORR-E005" for i in result.issues)
