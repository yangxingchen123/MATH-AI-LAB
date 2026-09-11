# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from app.resume_detect import (
    detect_unfinished,
    find_output_markdown,
    partition_pdf_run_queue,
    plan_pdf_run,
    record_can_resume,
    vision_resume_hint,
)
from app.task_model import ConvertTask, TaskStatus, WorkflowChoice
from app.utils.paths import OUTPUT_DIR, sanitize_output_dir
from app.vision_transcribe.manifest import VisionManifest, save_manifest
from app.vision_transcribe.models import BatchStatus


def test_find_output_markdown_prefers_newer(tmp_path: Path):
    import os

    partial = tmp_path / "book.partial.md"
    final = tmp_path / "book.md"
    partial.write_text("p", encoding="utf-8")
    final.write_text("ok", encoding="utf-8")
    os.utime(final, (2_000_000_000, 2_000_000_000))
    os.utime(partial, (1_900_000_000, 1_900_000_000))
    assert find_output_markdown(tmp_path, "book").name == "book.md"
    os.utime(partial, (2_100_000_000, 2_100_000_000))
    assert find_output_markdown(tmp_path, "book").name == "book.partial.md"


def test_record_can_resume_interrupted():
    assert record_can_resume({"status": TaskStatus.INTERRUPTED.value})
    assert record_can_resume({"status": TaskStatus.RUNNING.value})
    assert record_can_resume({"status": TaskStatus.FAILED.value})
    assert not record_can_resume({"status": TaskStatus.DONE.value})


def test_vision_resume_hint_incomplete(tmp_path: Path):
    m = VisionManifest(page_count=20, batches=[])
    m.batches = [
        {
            "id": 1,
            "start_page": 1,
            "end_page": 10,
            "status": BatchStatus.ACCEPTED.value,
        },
        {
            "id": 2,
            "start_page": 11,
            "end_page": 20,
            "status": BatchStatus.PENDING.value,
        },
    ]
    save_manifest(tmp_path, m)
    hint = vision_resume_hint(tmp_path)
    assert hint is not None
    assert hint.done == 10
    assert hint.workflow == WorkflowChoice.VISION.value


def test_vision_resume_hint_counts_accepted_pages(tmp_path: Path):
    m = VisionManifest(page_count=30, batches=[])
    m.batches = [
        {
            "id": 1,
            "start_page": 1,
            "end_page": 10,
            "status": BatchStatus.ACCEPTED.value,
        },
        {
            "id": 2,
            "start_page": 11,
            "end_page": 20,
            "status": BatchStatus.PENDING.value,
        },
        {
            "id": 3,
            "start_page": 21,
            "end_page": 30,
            "status": BatchStatus.ACCEPTED.value,
        },
    ]
    save_manifest(tmp_path, m)
    hint = vision_resume_hint(tmp_path)
    assert hint is not None
    assert hint.done == 20


def test_detect_unfinished_prefers_docling(tmp_path: Path):
    from app.parse_checkpoint import append_batch, write_interrupt_draft

    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF")
    struct = tmp_path / "book"
    struct.mkdir()
    (struct / "book.raw.partial.md").write_text("x", encoding="utf-8")
    append_batch(
        struct,
        start=1,
        end=5,
        chars=1,
        raw_md="book.raw.partial.md",
        total_pages=40,
        pdf_path=str(pdf),
    )
    write_interrupt_draft(struct, "book")
    hint = detect_unfinished(tmp_path, pdf, per_folder=True, prefer_vision=False)
    assert hint is not None
    assert hint.kind == "docling"
    assert hint.done == 5


def test_detect_unfinished_respects_task_workflow_when_both(tmp_path: Path):
    from app.parse_checkpoint import append_batch, write_interrupt_draft

    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF")
    struct = tmp_path / "book"
    struct.mkdir()
    (struct / "book.raw.partial.md").write_text("x", encoding="utf-8")
    append_batch(
        struct,
        start=1,
        end=5,
        chars=1,
        raw_md="book.raw.partial.md",
        total_pages=40,
        pdf_path=str(pdf),
    )
    write_interrupt_draft(struct, "book")
    vis = tmp_path / "book_高保真"
    vis.mkdir()
    m = VisionManifest(page_count=20, batches=[])
    m.batches = [
        {
            "id": 1,
            "start_page": 1,
            "end_page": 10,
            "status": BatchStatus.ACCEPTED.value,
        },
        {
            "id": 2,
            "start_page": 11,
            "end_page": 20,
            "status": BatchStatus.PENDING.value,
        },
    ]
    save_manifest(vis, m)
    doc = detect_unfinished(
        tmp_path,
        pdf,
        per_folder=True,
        prefer_workflow=WorkflowChoice.STRUCTURED.value,
    )
    vis_hint = detect_unfinished(
        tmp_path,
        pdf,
        per_folder=True,
        prefer_workflow=WorkflowChoice.VISION.value,
    )
    assert doc is not None and doc.kind == "docling"
    assert vis_hint is not None and vis_hint.kind == "vision"


def test_partition_resume_first():
    a = ConvertTask(pdf_path=Path("a.pdf"), workflow=WorkflowChoice.STRUCTURED.value)
    a.resume_from_checkpoint = True
    b = ConvertTask(pdf_path=Path("b.pdf"), workflow=WorkflowChoice.VISION.value)
    parts = partition_pdf_run_queue([b, a])
    assert parts[0][0] == "structured"
    assert parts[0][1] == [a]
    assert parts[1][0] == "vision"
    assert parts[1][1] == [b]


def test_sanitize_relative_goes_under_project():
    assert sanitize_output_dir("output") == OUTPUT_DIR or sanitize_output_dir("output").resolve() == OUTPUT_DIR.resolve()
    assert sanitize_output_dir(None) == OUTPUT_DIR


def test_plan_retry_keeps_task_route_not_ui():
    dec = plan_pdf_run(
        workflow=WorkflowChoice.VISION.value,
        engine="Docling",
        force_restart=True,
        resume_requested=False,
        ui_workflow=WorkflowChoice.STRUCTURED.value,
        ui_engine="MinerU",
        hint=None,
        vision_should_force=False,
    )
    assert dec.workflow == WorkflowChoice.VISION.value
    assert dec.engine == "Docling"
    assert dec.resume is False
    assert dec.vision_force_rerun is True


def test_plan_resume_follows_disk_hint():
    from app.resume_detect import ResumeHint

    disk = ResumeHint(
        kind="docling",
        out_dir=Path("out"),
        done=5,
        total=40,
        workflow=WorkflowChoice.STRUCTURED.value,
    )
    dec = plan_pdf_run(
        workflow=WorkflowChoice.VISION.value,
        engine="Docling",
        force_restart=False,
        resume_requested=True,
        ui_workflow=WorkflowChoice.VISION.value,
        ui_engine="自动",
        hint=disk,
    )
    assert dec.workflow == WorkflowChoice.STRUCTURED.value
    assert dec.resume is True
    assert dec.vision_force_rerun is False


def test_plan_fresh_uses_ui():
    dec = plan_pdf_run(
        workflow=WorkflowChoice.STRUCTURED.value,
        engine="Docling",
        force_restart=False,
        resume_requested=False,
        ui_workflow=WorkflowChoice.VISION.value,
        ui_engine="自动",
        hint=None,
        vision_should_force=True,
    )
    assert dec.workflow == WorkflowChoice.VISION.value
    assert dec.engine == "自动"
    assert dec.resume is False
    assert dec.vision_force_rerun is True
