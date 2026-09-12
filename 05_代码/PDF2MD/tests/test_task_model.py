# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from app.task_model import ConvertTask, TaskStatus, queue_skip_status


def test_convert_task_has_id_and_message():
    t = ConvertTask(pdf_path=Path("sample.pdf"), message="queued")
    assert t.id.endswith("sample.pdf")
    assert t.message == "queued"
    assert t.source_kind == "pdf"
    assert t.source_path == t.pdf_path
    assert not t.is_epub
    assert t.formula_recognized is None
    assert t.formula_post_ok is None
    assert t.formula_total is None


def test_convert_task_detects_epub():
    t = ConvertTask(pdf_path=Path("book.epub"))
    assert t.source_kind == "epub"
    assert t.is_epub
    assert t.source_path.name == "book.epub"


def test_pages_display_fraction_when_running():
    t = ConvertTask(pdf_path=Path("book.pdf"), pages=392)
    t.total_pages = 392
    t.status = "转换中"
    t.done_pages = 128
    assert t.pages_display() == "128/392"
    t.status = "等待"
    assert t.pages_display() == "392"
    t.status = "中断"
    assert t.pages_display() == "128/392"
    t.status = "失败"
    assert t.pages_display() == "128/392"
    t.status = "等待"
    t.resume_from_checkpoint = True
    assert t.pages_display() == "128/392"


def test_queue_skip_status_keeps_resume():
    t = ConvertTask(pdf_path=Path("book.pdf"))
    assert queue_skip_status(t) == (TaskStatus.WAITING.value, "等待")
    t.resume_from_checkpoint = True
    assert queue_skip_status(t)[0] == TaskStatus.INTERRUPTED.value
