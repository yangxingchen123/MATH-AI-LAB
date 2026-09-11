# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import pytest

from app.engines.docling_engine import convert_pdf, converter_supports_page_range
from app.parse_checkpoint import (
    ParseInterrupted,
    adaptive_page_batch_size,
    load_checkpoint,
    page_batches,
    resume_start_page,
    should_batch_pages,
    write_interrupt_draft,
)


def test_page_batches_last_short():
    assert page_batches(12, start_page=1, batch_size=5) == [
        (1, 5),
        (6, 10),
        (11, 12),
    ]
    assert page_batches(12, start_page=6, batch_size=5) == [(6, 10), (11, 12)]
    assert page_batches(3, start_page=1, batch_size=5) == [(1, 3)]
    assert page_batches(10, start_page=11, batch_size=5) == []


def test_should_batch_pages_threshold_and_support():
    assert should_batch_pages(40, supported=True, threshold=40) is True
    assert should_batch_pages(39, supported=True, threshold=40) is False
    assert should_batch_pages(400, supported=False, threshold=40) is False
    assert should_batch_pages(None, supported=True, threshold=40) is False


def test_adaptive_page_batch_size():
    assert adaptive_page_batch_size(None) == 8
    assert adaptive_page_batch_size(39) == 8
    assert adaptive_page_batch_size(40) == 8
    assert adaptive_page_batch_size(79) == 8
    assert adaptive_page_batch_size(80) == 10
    assert adaptive_page_batch_size(392) == 10


def test_converter_supports_page_range_probe():
    class WithRange:
        def convert(self, source, page_range=(1, 99)):
            return source, page_range

    class NoRange:
        def convert(self, source):
            return source

    assert converter_supports_page_range(WithRange()) is True
    assert converter_supports_page_range(NoRange()) is False


class _Doc:
    def __init__(self, text: str) -> None:
        self._text = text

    def export_to_markdown(self) -> str:
        return self._text


class _Result:
    def __init__(self, text: str) -> None:
        self.document = _Doc(text)


class FakeConverter:
    def __init__(self) -> None:
        self.calls: list[tuple[int, int]] = []

    def convert(self, source, page_range=(1, 10**9)):
        self.calls.append(tuple(page_range))
        a, b = page_range
        return _Result(f"pages {a}-{b}")


def test_checkpoint_interrupt_then_resume(tmp_path: Path):
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    out = tmp_path / "out"
    fake = FakeConverter()

    def cancel_after_first_batch() -> bool:
        return len(fake.calls) >= 1

    with pytest.raises(ParseInterrupted) as ei:
        convert_pdf(
            pdf,
            out,
            keep_images=False,
            keep_tables=False,
            keep_formulas=False,
            converter=fake,
            total_pages=12,
            page_batch_size=5,
            page_batch_threshold=1,
            cancelled=cancel_after_first_batch,
        )
    assert ei.value.next_page == 6
    ck = load_checkpoint(out)
    assert ck is not None
    assert ck["status"] == "interrupted"
    assert ck["next_page"] == 6
    assert resume_start_page(out, pdf.stem) == 6
    partial = out / f"{pdf.stem}.raw.partial.md"
    draft = out / f"{pdf.stem}.partial.md"
    assert "pages 1-5" in partial.read_text(encoding="utf-8")
    assert draft.is_file()
    assert not (out / f"{pdf.stem}.raw.md").is_file()

    fake2 = FakeConverter()
    result = convert_pdf(
        pdf,
        out,
        keep_images=False,
        keep_tables=False,
        keep_formulas=False,
        converter=fake2,
        total_pages=12,
        page_batch_size=5,
        page_batch_threshold=1,
        resume=True,
    )
    assert fake2.calls == [(6, 10), (11, 12)]
    text = result.markdown_path.read_text(encoding="utf-8")
    assert "pages 1-5" in text
    assert "pages 6-10" in text
    assert "pages 11-12" in text
    ck2 = load_checkpoint(out)
    assert ck2 is not None
    assert ck2["status"] == "done"


def test_small_document_converts_once_without_page_range(tmp_path: Path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    fake = FakeConverter()
    result = convert_pdf(
        pdf,
        tmp_path / "out2",
        keep_images=False,
        keep_tables=False,
        keep_formulas=False,
        converter=fake,
        total_pages=12,
        page_batch_threshold=40,
    )
    assert fake.calls == [(1, 10**9)]
    assert "pages 1-" in result.markdown_path.read_text(encoding="utf-8")


def test_write_interrupt_draft_without_partial(tmp_path: Path):
    assert write_interrupt_draft(tmp_path, "missing") is None


def test_auto_resume_without_flag_unless_force_restart(tmp_path: Path):
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    out = tmp_path / "out"
    fake = FakeConverter()

    def cancel_after_first_batch() -> bool:
        return len(fake.calls) >= 1

    with pytest.raises(ParseInterrupted):
        convert_pdf(
            pdf,
            out,
            keep_images=False,
            keep_tables=False,
            keep_formulas=False,
            converter=fake,
            total_pages=12,
            page_batch_size=5,
            page_batch_threshold=1,
            cancelled=cancel_after_first_batch,
        )
    fake2 = FakeConverter()
    convert_pdf(
        pdf,
        out,
        keep_images=False,
        keep_tables=False,
        keep_formulas=False,
        converter=fake2,
        total_pages=12,
        page_batch_size=5,
        page_batch_threshold=1,
        resume=False,
    )
    assert fake2.calls == [(6, 10), (11, 12)]

    fake3 = FakeConverter()
    convert_pdf(
        pdf,
        out,
        keep_images=False,
        keep_tables=False,
        keep_formulas=False,
        converter=fake3,
        total_pages=12,
        page_batch_size=5,
        page_batch_threshold=1,
        force_restart=True,
    )
    assert fake3.calls[0] == (1, 5)


def test_unspecified_batch_size_follows_page_count(tmp_path: Path):
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    logs: list[str] = []
    fake = FakeConverter()
    convert_pdf(
        pdf,
        tmp_path / "out40",
        keep_images=False,
        keep_tables=False,
        keep_formulas=False,
        converter=fake,
        total_pages=40,
        page_batch_threshold=40,
        progress=logs.append,
    )
    assert fake.calls[0] == (1, 8)
    assert fake.calls[-1] == (33, 40)
    assert any("每批 8 页" in line for line in logs)
    assert any("耗时" in line and "本批第" in line for line in logs)

    fake80 = FakeConverter()
    convert_pdf(
        pdf,
        tmp_path / "out80",
        keep_images=False,
        keep_tables=False,
        keep_formulas=False,
        converter=fake80,
        total_pages=80,
        page_batch_threshold=40,
    )
    assert fake80.calls[0] == (1, 10)
    assert fake80.calls[-1] == (71, 80)


def test_sanitize_rejects_desktop_pdftomd():
    from app.utils.paths import OUTPUT_DIR, looks_like_foreign_desktop_output, sanitize_output_dir

    stale = Path.home() / "Desktop" / "PDFTomd" / "github-submit" / "output"
    assert looks_like_foreign_desktop_output(stale)
    assert sanitize_output_dir(stale) == OUTPUT_DIR
    assert sanitize_output_dir(OUTPUT_DIR) == OUTPUT_DIR
    from app.task_model import TaskStatus, is_startable_status

    assert is_startable_status(TaskStatus.INTERRUPTED.value)
    assert is_startable_status(TaskStatus.WAITING.value)
    assert not is_startable_status(TaskStatus.DONE.value)
