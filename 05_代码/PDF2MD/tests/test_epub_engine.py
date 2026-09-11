# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import pytest

from app.engines.epub_engine import convert_epub
from app.epub.assemble import apply_export_rules
from app.epub.container import EpubEncryptedError
from tests.helpers.epub_builder import build_minimal_epub


def test_convert_minimal_epub_order_and_image(tmp_path: Path):
    book = build_minimal_epub(tmp_path / "book.epub")
    out = tmp_path / "out"
    result = convert_epub(book, out)
    assert result.parser == "epub"
    assert result.pages == 2
    raw = result.markdown_path.read_text(encoding="utf-8")
    assert "# Minimal Book" in raw
    assert raw.index("Chapter One") < raw.index("Chapter Two")
    assert "![cover](images/cover.png)" in raw
    assert "[next](#sec)" in raw
    assert "- alpha" in raw
    img = out / "images" / "cover.png"
    assert img.is_file() and img.stat().st_size > 0
    ch1 = (out / ".epub" / "chapter_001.md").read_text(encoding="utf-8")
    assert "Chapter One" in ch1
    final = apply_export_rules(raw)
    assert "Chapter Two" in final


def test_convert_encrypted_fails(tmp_path: Path):
    book = build_minimal_epub(tmp_path / "drm.epub", encrypted=True)
    with pytest.raises(EpubEncryptedError, match="DRM"):
        convert_epub(book, tmp_path / "out")
