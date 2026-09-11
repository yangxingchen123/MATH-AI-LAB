# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from app.formats import (
    KIND_EPUB,
    KIND_PDF,
    accepts_file,
    capabilities,
    iter_input_files,
    kind_for_path,
)
from app.ui.pipeline_classify import classify_pipeline_stage


def test_kind_for_path():
    assert kind_for_path(Path("a.PDF")) == KIND_PDF
    assert kind_for_path(Path("b.epub")) == KIND_EPUB
    assert kind_for_path(Path("c.txt")) is None


def test_capabilities():
    pdf = capabilities(KIND_PDF)
    assert pdf.vision and pdf.formula_ocr and pdf.engines
    epub = capabilities(KIND_EPUB)
    assert not epub.vision and not epub.formula_ocr and not epub.engines
    assert epub.unit == "spine_chapters"


def test_iter_input_files_dir(tmp_path: Path):
    (tmp_path / "a.pdf").write_bytes(b"%PDF")
    (tmp_path / "b.epub").write_bytes(b"PK")
    (tmp_path / "c.txt").write_text("x", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.EPUB").write_bytes(b"PK")
    found = {p.name.lower() for p in iter_input_files(tmp_path)}
    assert found == {"a.pdf", "b.epub", "d.epub"}
    assert accepts_file(tmp_path / "a.pdf")
    assert not accepts_file(tmp_path / "c.txt")


def test_epub_progress_classifies_as_parse():
    assert classify_pipeline_stage("EPUB：解析章节 1/2") == "parse"
    assert classify_pipeline_stage("EPUB：解包并校验…") == "parse"
