"""Outcome and assistance enum tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.attempt_validator.validator import validate_project
from tests.attempt_validator.conftest import setup_p0002_multipart, write_single_attempt


@pytest.mark.parametrize(
    "outcome",
    ["correct", "incorrect", "partial", "unsolved", "abandoned", "unassessed"],
)
def test_outcome_enums(attempt_project: Path, outcome: str) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, outcome=outcome)
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


def test_invalid_outcome(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, outcome="maybe")
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-OUT-E001" for i in result.issues)


@pytest.mark.parametrize("assistance", ["independent", "assisted"])
def test_assistance_enums(attempt_project: Path, assistance: str) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, assistance=assistance)
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


def test_assistance_omitted(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, assistance=None)
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


@pytest.mark.parametrize("assistance", ["omitted", "unknown"])
def test_invalid_assistance(attempt_project: Path, assistance: str) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, assistance=assistance)
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-ASST-E001" for i in result.issues)
