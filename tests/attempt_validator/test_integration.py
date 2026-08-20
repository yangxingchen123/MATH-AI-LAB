"""Filename mismatch and integration tests."""

from __future__ import annotations

from pathlib import Path

from tools.attempt_validator.validator import validate_project
from tests.attempt_validator.conftest import attempt_record, setup_p0002_multipart, write_ledger


def test_aid_independent_of_ledger_filename(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [attempt_record(aid="A000050")],
        {"A000050": "body"},
    )
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0
    assert "A000050" in result.registry


def test_registry_empty_on_errors(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    bad = attempt_record()
    bad["outcome"] = "bad"
    write_ledger(attempt_project, "P0002", [bad], {"A000001": "body"})
    result = validate_project(root=attempt_project)
    assert result.summary.errors > 0
    assert result.registry == {}
