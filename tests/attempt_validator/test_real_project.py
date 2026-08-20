"""Real MATH-AI-LAB repository Attempt validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.attempt_validator.validator import validate_file, validate_project

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(not (REPO_ROOT / "元数据规范.md").is_file(), reason="not in repo root")
def test_real_p0002_ledger() -> None:
    path = REPO_ROOT / "11_学习证据" / "尝试记录" / "P0002.md"
    if not path.is_file():
        pytest.skip("P0002 ledger not present")
    result = validate_file(path, root=REPO_ROOT)
    assert result.summary.errors == 0


@pytest.mark.skipif(not (REPO_ROOT / "元数据规范.md").is_file(), reason="not in repo root")
def test_real_project_check() -> None:
    result = validate_project(root=REPO_ROOT)
    assert result.summary.errors == 0
    assert len(result.registry) >= 2
