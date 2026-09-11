"""转换任务数据模型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from app.formats import KIND_EPUB, KIND_PDF, kind_for_path


class TaskStatus(str, Enum):
    WAITING = "等待"
    RUNNING = "转换中"
    DONE = "完成"
    FAILED = "失败"
    CANCELLED = "取消"
    INTERRUPTED = "中断"


class EngineChoice(str, Enum):
    DOCLING = "Docling"
    MINERU = "MinerU"
    AUTO = "自动"


class WorkflowChoice(str, Enum):
    STRUCTURED = "快速自动"
    VISION = "高保真视觉"


@dataclass
class ConvertTask:
    pdf_path: Path
    source_kind: str = ""
    engine: str = EngineChoice.DOCLING.value
    workflow: str = WorkflowChoice.STRUCTURED.value
    status: str = TaskStatus.WAITING.value
    pages: int | None = None
    size_bytes: int = 0
    elapsed_sec: float | None = None
    output_md: Path | None = None
    output_dir: Path | None = None
    error: str = ""
    message: str = ""
    formula_recognized: int | None = None
    formula_post_ok: int | None = None
    formula_total: int | None = None
    vision_force_rerun: bool = False
    vision_final_chars: int | None = None
    vision_ds_chars: int | None = None
    vision_fidelity_ratio: float | None = None
    done_pages: int | None = None
    total_pages: int | None = None
    resume_from_checkpoint: bool = False
    force_restart: bool = False
    started_at: str = ""
    id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.source_kind:
            self.source_kind = kind_for_path(self.pdf_path) or KIND_PDF
        if not self.id:
            self.id = str(self.pdf_path.resolve())
        if not self.size_bytes and self.pdf_path.exists():
            self.size_bytes = self.pdf_path.stat().st_size

    @property
    def source_path(self) -> Path:
        return self.pdf_path

    @property
    def is_epub(self) -> bool:
        return self.source_kind == KIND_EPUB

    @property
    def name(self) -> str:
        return self.pdf_path.name

    def pages_display(self) -> str:
        """运行中、中断、失败、取消显示 已完成/总页数；空闲只显示总页数。"""
        total = self.total_pages if self.total_pages is not None else self.pages
        show_frac = self.status in (
            TaskStatus.RUNNING.value,
            TaskStatus.INTERRUPTED.value,
            TaskStatus.CANCELLED.value,
            TaskStatus.FAILED.value,
        ) or self.resume_from_checkpoint
        if show_frac and total:
            done = self.done_pages if self.done_pages is not None else 0
            return f"{done}/{total}"
        if self.pages is not None:
            return str(self.pages)
        if total is not None:
            return str(total)
        return "-"

    @property
    def size_label(self) -> str:
        b = self.size_bytes
        if b < 1024:
            return f"{b} B"
        if b < 1024 * 1024:
            return f"{b / 1024:.1f} KB"
        return f"{b / (1024 * 1024):.1f} MB"


def is_startable_status(status: str) -> bool:
    """开始转换时要跑的状态。已完成的不自动重跑，避免覆盖上次结果。"""
    return status in (
        TaskStatus.WAITING.value,
        TaskStatus.FAILED.value,
        TaskStatus.INTERRUPTED.value,
        TaskStatus.CANCELLED.value,
    )


def queue_skip_status(task: ConvertTask) -> tuple[str, str]:
    """队列里尚未开跑、因取消被跳过的任务应回到什么状态。"""
    if getattr(task, "resume_from_checkpoint", False):
        return TaskStatus.INTERRUPTED.value, "已中断"
    return TaskStatus.WAITING.value, "等待"
