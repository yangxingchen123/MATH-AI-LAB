"""Tests for atomic Source I/O."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.source_io.atomic import AtomicWriteError, atomic_replace_text


def test_atomic_replace_success(tmp_path: Path) -> None:
    target = tmp_path / "official.md"
    target.write_text("old", encoding="utf-8")
    atomic_replace_text(target, "new")
    assert target.read_text(encoding="utf-8") == "new"


def test_invalid_candidate_preserves_official(tmp_path: Path) -> None:
    target = tmp_path / "official.md"
    target.write_text("keep", encoding="utf-8")

    def reject(_: str) -> None:
        raise ValueError("invalid")

    from tools.source_io.atomic import write_candidate_then_replace

    with pytest.raises(ValueError):
        write_candidate_then_replace(target, "bad", validate=reject)
    assert target.read_text(encoding="utf-8") == "keep"
