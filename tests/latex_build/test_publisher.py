"""Tests for formal PDF publisher."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.latex_build.models import PublishStatus
from tools.latex_build.publisher import PublishError, publish_formal_pdf


def test_created_when_no_formal_pdf(tmp_path: Path) -> None:
    built = tmp_path / "built.pdf"
    built.write_bytes(b"NEW")
    formal = tmp_path / "out" / "topic.pdf"
    result = publish_formal_pdf(built_pdf=built, formal_pdf=formal, publish_allowed=True)
    assert result.status == PublishStatus.CREATED
    assert result.writes == 1
    assert formal.read_bytes() == b"NEW"


def test_updated_when_different(tmp_path: Path) -> None:
    built = tmp_path / "built.pdf"
    built.write_bytes(b"NEW")
    formal = tmp_path / "topic.pdf"
    formal.write_bytes(b"OLD")
    result = publish_formal_pdf(built_pdf=built, formal_pdf=formal, publish_allowed=True)
    assert result.status == PublishStatus.UPDATED
    assert formal.read_bytes() == b"NEW"


def test_up_to_date_zero_writes(tmp_path: Path) -> None:
    payload = b"SAME"
    built = tmp_path / "built.pdf"
    built.write_bytes(payload)
    formal = tmp_path / "topic.pdf"
    formal.write_bytes(payload)
    result = publish_formal_pdf(built_pdf=built, formal_pdf=formal, publish_allowed=True)
    assert result.status == PublishStatus.UP_TO_DATE
    assert result.writes == 0


def test_blocked_when_not_allowed(tmp_path: Path) -> None:
    built = tmp_path / "built.pdf"
    built.write_bytes(b"NEW")
    formal = tmp_path / "topic.pdf"
    formal.write_bytes(b"OLD")
    result = publish_formal_pdf(built_pdf=built, formal_pdf=formal, publish_allowed=False)
    assert result.status == PublishStatus.BLOCKED
    assert formal.read_bytes() == b"OLD"


def test_old_formal_unchanged_on_blocked_build(tmp_path: Path) -> None:
    formal = tmp_path / "topic.pdf"
    formal.write_bytes(b"GOOD_BYTES")
    missing = tmp_path / "missing.pdf"
    result = publish_formal_pdf(built_pdf=missing, formal_pdf=formal, publish_allowed=True)
    assert result.status == PublishStatus.BLOCKED
    assert formal.read_bytes() == b"GOOD_BYTES"


def test_no_temp_left_after_publish(tmp_path: Path) -> None:
    built = tmp_path / "built.pdf"
    built.write_bytes(b"NEW")
    formal = tmp_path / "topic.pdf"
    publish_formal_pdf(built_pdf=built, formal_pdf=formal, publish_allowed=True)
    assert list(tmp_path.glob("*.tmp")) == []
