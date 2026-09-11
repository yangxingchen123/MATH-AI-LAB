# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import pytest

from app.epub.container import EpubEncryptedError, EpubError, EpubPackage
from app.epub.opf import parse_opf, peek_spine_count
from tests.helpers.epub_builder import build_minimal_epub


def test_open_minimal_epub(tmp_path: Path):
    book = build_minimal_epub(tmp_path / "ok.epub")
    with EpubPackage(book) as pkg:
        assert pkg.container_rootfile() == "OEBPS/content.opf"
        opf = parse_opf(pkg)
        assert opf.title == "Minimal Book"
        assert [i.idref for i in opf.spine] == ["ch1", "ch2"]
    assert peek_spine_count(book) == 2


def test_encrypted_epub_raises(tmp_path: Path):
    book = build_minimal_epub(tmp_path / "drm.epub", encrypted=True)
    with pytest.raises(EpubEncryptedError, match="DRM"):
        with EpubPackage(book):
            pass


def test_not_zip_raises(tmp_path: Path):
    p = tmp_path / "fake.epub"
    p.write_text("not a zip", encoding="utf-8")
    with pytest.raises(EpubError, match="ZIP"):
        with EpubPackage(p):
            pass
