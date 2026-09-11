# -*- coding: utf-8 -*-
"""Docling 按页批处理的 checkpoint：取消后保留已完成部分，下次从 next_page 续跑。"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from app.utils.jsonio import write_json_atomic

CHECKPOINT_NAME = "checkpoint.json"
DEFAULT_BATCH_SIZE = 5
BATCH_SIZE_STANDARD = 8
BATCH_SIZE_WIDE = 10
BATCH_PAGE_THRESHOLD = 40
WIDE_DOC_PAGES = 80
STATUS_RUNNING = "running"
STATUS_INTERRUPTED = "interrupted"
STATUS_DONE = "done"


class ParseInterrupted(Exception):
    """解析在批次边界被取消；已完成部分已写入磁盘。"""

    def __init__(
        self,
        message: str = "解析已中断",
        *,
        next_page: int | None = None,
        draft_path: Path | None = None,
    ) -> None:
        super().__init__(message)
        self.next_page = next_page
        self.draft_path = draft_path


def adaptive_page_batch_size(total_pages: int | None) -> int:
    """未指定批大小时：40–79 页每批 8 页，80 页及以上每批 10 页。

    仍只在批次边界写 checkpoint，取消后续跑从 next_page 接着转。
    """
    n = int(total_pages or 0)
    if n >= WIDE_DOC_PAGES:
        return BATCH_SIZE_WIDE
    return BATCH_SIZE_STANDARD


def page_batches(
    total_pages: int,
    *,
    start_page: int = 1,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[tuple[int, int]]:
    """1-based 闭区间批次。最后一批可不足 batch_size 页。"""
    if total_pages < 1 or start_page < 1 or start_page > total_pages:
        return []
    size = max(1, int(batch_size))
    out: list[tuple[int, int]] = []
    a = int(start_page)
    while a <= total_pages:
        b = min(a + size - 1, total_pages)
        out.append((a, b))
        a = b + 1
    return out


def should_batch_pages(
    total_pages: int | None,
    *,
    supported: bool,
    threshold: int = BATCH_PAGE_THRESHOLD,
) -> bool:
    if not supported or not total_pages:
        return False
    return int(total_pages) >= int(threshold)


def checkpoint_path(out_dir: Path) -> Path:
    return Path(out_dir) / CHECKPOINT_NAME


def partial_raw_path(out_dir: Path, stem: str) -> Path:
    return Path(out_dir) / f"{stem}.raw.partial.md"


def draft_partial_path(out_dir: Path, stem: str) -> Path:
    return Path(out_dir) / f"{stem}.partial.md"


def new_checkpoint(
    *,
    total_pages: int,
    raw_md: str,
    pdf_path: str = "",
    next_page: int = 1,
) -> dict[str, Any]:
    return {
        "total_pages": int(total_pages),
        "next_page": int(next_page),
        "batches": [],
        "raw_md": raw_md,
        "status": STATUS_RUNNING,
        "pdf_path": pdf_path,
    }


def load_checkpoint(out_dir: Path) -> dict[str, Any] | None:
    path = checkpoint_path(out_dir)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def save_checkpoint(out_dir: Path, data: dict[str, Any]) -> None:
    write_json_atomic(checkpoint_path(out_dir), data)


def mark_checkpoint(out_dir: Path, status: str, **extra: Any) -> dict[str, Any] | None:
    data = load_checkpoint(out_dir)
    if data is None:
        return None
    data["status"] = status
    data.update(extra)
    save_checkpoint(out_dir, data)
    return data


def append_batch(
    out_dir: Path,
    *,
    start: int,
    end: int,
    chars: int,
    raw_md: str,
    total_pages: int,
    pdf_path: str = "",
) -> dict[str, Any]:
    data = load_checkpoint(out_dir) or new_checkpoint(
        total_pages=total_pages,
        raw_md=raw_md,
        pdf_path=pdf_path,
    )
    batches = list(data.get("batches") or [])
    batches.append({"start": int(start), "end": int(end), "chars": int(chars)})
    data["batches"] = batches
    data["next_page"] = int(end) + 1
    data["raw_md"] = raw_md
    data["total_pages"] = int(total_pages)
    data["status"] = STATUS_RUNNING
    if pdf_path:
        data["pdf_path"] = pdf_path
    save_checkpoint(out_dir, data)
    return data


def write_interrupt_draft(out_dir: Path, stem: str) -> Path | None:
    """把已完成的 raw.partial 复制为可读的 .partial.md，并标记 interrupted。"""
    src = partial_raw_path(out_dir, stem)
    if not src.is_file():
        mark_checkpoint(out_dir, STATUS_INTERRUPTED)
        return None
    dst = draft_partial_path(out_dir, stem)
    shutil.copy2(src, dst)
    mark_checkpoint(
        out_dir,
        STATUS_INTERRUPTED,
        raw_md=src.name,
        draft_md=dst.name,
    )
    return dst


def resume_start_page(out_dir: Path, stem: str) -> int:
    """有 checkpoint 且 partial 仍在时从 next_page 续；否则从第 1 页。"""
    data = load_checkpoint(out_dir)
    if not data:
        return 1
    nxt = int(data.get("next_page") or 1)
    if nxt < 1:
        return 1
    partial = Path(out_dir) / str(data.get("raw_md") or partial_raw_path(out_dir, stem).name)
    if not partial.is_file():
        partial = partial_raw_path(out_dir, stem)
    if nxt > 1 and not partial.is_file():
        return 1
    return nxt


def checkpoint_resumable(out_dir: Path, stem: str) -> tuple[bool, int]:
    """是否应从 checkpoint 续跑。返回 (可续跑, next_page)。"""
    data = load_checkpoint(out_dir)
    if not data:
        return False, 1
    if str(data.get("status") or "") == STATUS_DONE:
        return False, 1
    nxt = resume_start_page(out_dir, stem)
    total = int(data.get("total_pages") or 0)
    if nxt > 1 and (total <= 0 or nxt <= total):
        return True, nxt
    return False, nxt
