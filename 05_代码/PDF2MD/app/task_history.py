# -*- coding: utf-8 -*-
"""任务历史：本地 JSON，主表按时间展示。"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.task_model import ConvertTask, EngineChoice, TaskStatus, WorkflowChoice
from app.utils.jsonio import write_json_atomic
from app.utils.paths import APP_ROOT

HISTORY_NAME = "task_history.json"
TRASH_NAME = "task_trash.json"


def history_path() -> Path:
    return APP_ROOT / "data" / HISTORY_NAME


def trash_path() -> Path:
    return APP_ROOT / "data" / TRASH_NAME


def record_id(rec: dict[str, Any]) -> str:
    return str(rec.get("id") or rec.get("path") or "")


def _load_json_list(p: Path) -> list[dict[str, Any]]:
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("tasks"), list):
        return [x for x in data["tasks"] if isinstance(x, dict)]
    return []


def load_history(path: Path | None = None) -> list[dict[str, Any]]:
    return _load_json_list(path or history_path())


def save_history(records: list[dict[str, Any]], path: Path | None = None) -> None:
    write_json_atomic(path or history_path(), records)


def load_trash(path: Path | None = None) -> list[dict[str, Any]]:
    return _load_json_list(path or trash_path())


def save_trash(records: list[dict[str, Any]], path: Path | None = None) -> None:
    write_json_atomic(path or trash_path(), records)


_PRESERVE_IF_BLANK = ("output_dir", "output_md", "started_at")


def upsert_history(record: dict[str, Any], path: Path | None = None) -> None:
    rid = record_id(record)
    if not rid:
        return
    records = load_history(path)
    found = False
    for i, old in enumerate(records):
        if record_id(old) == rid:
            merged = dict(old)
            for k, v in record.items():
                if v is None:
                    continue
                if k in _PRESERVE_IF_BLANK and v == "" and old.get(k):
                    continue
                merged[k] = v
            if not record.get("started_at") and old.get("started_at"):
                merged["started_at"] = old["started_at"]
            records[i] = merged
            found = True
            break
    if not found:
        records.append(record)
    save_history(records, path)


def record_from_task(task: ConvertTask, **overrides: Any) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "id": task.id,
        "path": str(task.pdf_path),
        "name": task.name,
        "pages": task.pages,
        "done_pages": task.done_pages,
        "total_pages": task.total_pages or task.pages,
        "engine": task.engine,
        "workflow": task.workflow,
        "status": task.status,
        "output_dir": str(task.output_dir) if task.output_dir else "",
        "output_md": str(task.output_md) if task.output_md else "",
        "error": (task.error or "")[:500],
        "source_kind": task.source_kind,
    }
    rec.update(overrides)
    return rec


def _take_record(
    records: list[dict[str, Any]], rid: str
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    found: dict[str, Any] | None = None
    kept: list[dict[str, Any]] = []
    for rec in records:
        if found is None and record_id(rec) == rid:
            found = rec
        else:
            kept.append(rec)
    return found, kept


def remove_history(rid: str, path: Path | None = None) -> dict[str, Any] | None:
    if not rid:
        return None
    found, kept = _take_record(load_history(path), rid)
    if found is not None:
        save_history(kept, path)
    return found


def push_trash(record: dict[str, Any], path: Path | None = None) -> None:
    rid = record_id(record)
    if not rid:
        return
    records = [r for r in load_trash(path) if record_id(r) != rid]
    records.insert(0, record)
    save_trash(records, path)


def pop_trash(rid: str, path: Path | None = None) -> dict[str, Any] | None:
    if not rid:
        return None
    found, kept = _take_record(load_trash(path), rid)
    if found is not None:
        save_trash(kept, path)
    return found


def _sort_newest_first(
    records: list[dict[str, Any]], *keys: str
) -> list[dict[str, Any]]:
    dated: list[tuple[datetime, dict[str, Any]]] = []
    undated: list[dict[str, Any]] = []
    for rec in records:
        raw = None
        for key in keys:
            raw = rec.get(key)
            if raw:
                break
        dt = _parse_dt(raw)
        if dt is None:
            undated.append(rec)
        else:
            dated.append((dt, rec))
    dated.sort(key=lambda x: x[0], reverse=True)
    return [r for _dt, r in dated] + undated


def sort_trash_newest_first(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _sort_newest_first(records, "deleted_at", "started_at", "ended_at")


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def task_from_record(rec: dict[str, Any]) -> ConvertTask | None:
    """从历史记录还原任务。文件不在了也可以进表。"""
    raw = rec.get("path") or rec.get("id")
    if not raw:
        return None
    path = Path(str(raw))
    status = str(rec.get("status") or TaskStatus.WAITING.value)
    if status == TaskStatus.RUNNING.value:
        status = TaskStatus.INTERRUPTED.value
    task = ConvertTask(
        pdf_path=path,
        source_kind=str(rec.get("source_kind") or ""),
        engine=str(rec.get("engine") or EngineChoice.DOCLING.value),
        workflow=str(rec.get("workflow") or WorkflowChoice.STRUCTURED.value),
        status=status,
        pages=_as_int(rec.get("pages")),
        error=str(rec.get("error") or ""),
        started_at=str(rec.get("started_at") or ""),
    )
    if rec.get("id"):
        task.id = str(rec["id"])
    task.done_pages = _as_int(rec.get("done_pages"))
    total = _as_int(rec.get("total_pages")) or task.pages
    if total is not None:
        task.total_pages = total
    out_dir = rec.get("output_dir")
    if out_dir:
        task.output_dir = Path(str(out_dir))
    out_md = rec.get("output_md")
    if out_md:
        p = Path(str(out_md))
        if p.is_file():
            task.output_md = p
    return task


def sort_history_newest_first(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """近的在前，远的在后；没有时间的放最后。"""
    return _sort_newest_first(records, "started_at", "ended_at")


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)
    return dt
