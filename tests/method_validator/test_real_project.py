"""Real project regression tests."""

from __future__ import annotations

from pathlib import Path

from tools.method_validator.validator import validate_file, validate_project


REAL_ROOT = Path(__file__).resolve().parents[2]


def test_real_m0001_passes() -> None:
    result = validate_file(REAL_ROOT / "12_方法库" / "M0001.md", root=REAL_ROOT)
    assert result.summary.errors == 0
    doc = next(d for d in result.documents if d.object_id == "M0001")
    assert doc.status == "draft"


def test_real_m0002_passes() -> None:
    result = validate_file(REAL_ROOT / "12_方法库" / "M0002.md", root=REAL_ROOT)
    assert result.summary.errors == 0
    doc = next(d for d in result.documents if d.object_id == "M0002")
    assert doc.status == "draft"


def test_real_project_check() -> None:
    result = validate_project(root=REAL_ROOT)
    assert result.summary.errors == 0
    assert result.summary.warnings == 0
    assert set(result.registry.keys()) == {"M0001", "M0002"}
    assert all(doc.status == "draft" for doc in result.registry.values())
