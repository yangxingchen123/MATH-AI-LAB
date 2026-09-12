# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from app.task_model import ConvertTask, TaskStatus
from app.task_history import (
    load_history,
    load_trash,
    pop_trash,
    push_trash,
    record_from_task,
    remove_history,
    save_history,
    sort_history_newest_first,
    sort_trash_newest_first,
    task_from_record,
    upsert_history,
)


def test_upsert_history_merges_by_id(tmp_path: Path):
    path = tmp_path / "task_history.json"
    upsert_history({"id": "/book.pdf", "status": "等待", "name": "book.pdf"}, path)
    upsert_history({"id": "/book.pdf", "status": "完成", "done_pages": 10}, path)
    rows = load_history(path)
    assert len(rows) == 1
    assert rows[0]["status"] == "完成"
    assert rows[0]["name"] == "book.pdf"
    assert rows[0]["done_pages"] == 10


def test_record_from_task_uses_path_id(tmp_path: Path):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    t = ConvertTask(pdf_path=pdf, status=TaskStatus.INTERRUPTED.value, pages=40)
    t.done_pages = 15
    rec = record_from_task(t)
    assert rec["id"] == str(pdf.resolve())
    assert rec["done_pages"] == 15
    assert rec["status"] == "中断"


def test_upsert_preserves_output_dir_when_blank(tmp_path: Path):
    path = tmp_path / "task_history.json"
    upsert_history(
        {"id": "/book.pdf", "output_dir": "C:/out/book", "status": "中断"},
        path,
    )
    upsert_history({"id": "/book.pdf", "output_dir": "", "status": "转换中"}, path)
    rows = load_history(path)
    assert rows[0]["output_dir"] == "C:/out/book"
    assert rows[0]["status"] == "转换中"


def test_save_load_roundtrip(tmp_path: Path):
    path = tmp_path / "h.json"
    save_history([{"id": "1", "name": "a.pdf"}], path)
    assert load_history(path)[0]["name"] == "a.pdf"


def test_sort_history_newest_first():
    records = [
        {"id": "old", "started_at": "2026-01-01T10:00:00"},
        {"id": "new", "started_at": "2026-09-08T12:00:00"},
        {"id": "mid", "ended_at": "2026-06-01T08:00:00"},
        {"id": "none"},
    ]
    ordered = sort_history_newest_first(records)
    assert [r["id"] for r in ordered] == ["new", "mid", "old", "none"]


def test_sort_history_mixed_timezone_does_not_raise():
    ordered = sort_history_newest_first(
        [
            {"id": "naive", "started_at": "2026-09-08T20:00:00"},
            {"id": "zulu", "started_at": "2026-09-08T12:00:00Z"},
            {"id": "none"},
        ]
    )
    assert ordered[-1]["id"] == "none"
    assert {r["id"] for r in ordered} == {"naive", "zulu", "none"}


def test_task_from_record_running_becomes_interrupted(tmp_path: Path):
    pdf = tmp_path / "book.pdf"
    rec = {
        "id": str(pdf),
        "path": str(pdf),
        "status": TaskStatus.RUNNING.value,
        "engine": "Docling",
        "done_pages": 12,
        "total_pages": 40,
    }
    task = task_from_record(rec)
    assert task is not None
    assert task.status == TaskStatus.INTERRUPTED.value
    assert task.done_pages == 12
    assert task.total_pages == 40
    assert task.pdf_path.name == "book.pdf"


def test_remove_history_and_trash_roundtrip(tmp_path: Path):
    hist = tmp_path / "task_history.json"
    trash = tmp_path / "task_trash.json"
    upsert_history({"id": "/keep.pdf", "name": "keep.pdf"}, hist)
    upsert_history({"id": "/gone.pdf", "name": "gone.pdf", "status": "完成"}, hist)
    gone = remove_history("/gone.pdf", hist)
    assert gone is not None
    assert gone["name"] == "gone.pdf"
    names = {r["name"] for r in load_history(hist)}
    assert names == {"keep.pdf"}
    gone["deleted_at"] = "2026-09-08T20:00:00"
    push_trash(gone, trash)
    rows = load_trash(trash)
    assert [r["id"] for r in rows] == ["/gone.pdf"]
    push_trash({"id": "/gone.pdf", "name": "gone.pdf", "deleted_at": "2026-09-08T21:00:00"}, trash)
    rows = load_trash(trash)
    assert len(rows) == 1
    assert rows[0]["deleted_at"] == "2026-09-08T21:00:00"
    restored = pop_trash("/gone.pdf", trash)
    assert restored is not None
    assert load_trash(trash) == []


def test_sort_trash_newest_first():
    records = [
        {"id": "old", "deleted_at": "2026-01-01T10:00:00"},
        {"id": "new", "deleted_at": "2026-09-08T12:00:00"},
        {"id": "none"},
    ]
    ordered = sort_trash_newest_first(records)
    assert [r["id"] for r in ordered] == ["new", "old", "none"]
