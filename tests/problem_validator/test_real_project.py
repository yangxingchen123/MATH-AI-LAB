"""Real project regression tests."""

from __future__ import annotations

from pathlib import Path

from tools.problem_validator.validator import validate_project


REAL_ROOT = Path(__file__).resolve().parents[2]


def test_real_p0001_p0002_pass() -> None:
    result = validate_project(root=REAL_ROOT)
    assert result.summary.errors == 0
    assert result.summary.warnings == 0
    ids = {d.object_id for d in result.documents}
    assert "P0001" in ids
    assert "P0002" in ids
