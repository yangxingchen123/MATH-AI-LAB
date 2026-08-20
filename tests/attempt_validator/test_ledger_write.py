"""Tests for atomic Attempt Ledger append."""

from __future__ import annotations

from pathlib import Path

from tests.attempt_validator.conftest import attempt_record, setup_p0002_multipart, write_ledger
from tools.attempt_validator.ledger import append_attempt_to_ledger, load_ledger_file


def test_second_attempt_appends_same_ledger(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [attempt_record(aid="A000001")],
        {"A000001": "first"},
    )
    result = append_attempt_to_ledger(
        attempt_project,
        problem_id="P0002",
        record=attempt_record(aid="A000002", part="a", attempted_at="2026-08-19T22:05+08:00"),
        narrative="second",
    )
    assert result.written is True
    assert result.action == "APPEND"
    path = attempt_project / "11_学习证据" / "尝试记录" / "P0002.md"
    loaded = load_ledger_file(path, attempt_project)
    assert len(loaded.attempts) == 2
    assert loaded.sections["A000002"] == "second"


def test_invalid_attempt_rollback_preserves_ledger(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [attempt_record(aid="A000001")],
        {"A000001": "keep"},
    )
    path = attempt_project / "11_学习证据" / "尝试记录" / "P0002.md"
    original = path.read_text(encoding="utf-8")
    bad = attempt_record(aid="A000001")
    bad["outcome"] = "not-an-outcome"
    result = append_attempt_to_ledger(
        attempt_project,
        problem_id="P0002",
        record=bad,
        narrative="bad",
    )
    assert result.written is False
    assert path.read_text(encoding="utf-8") == original
