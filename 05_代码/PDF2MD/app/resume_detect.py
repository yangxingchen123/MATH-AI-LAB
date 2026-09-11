# -*- coding: utf-8 -*-
"""探测 output 里未完成的 Docling / 视觉任务，供入队和「继续」使用。"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.parse_checkpoint import checkpoint_resumable, load_checkpoint
from app.task_model import WorkflowChoice
from app.utils.paths import task_output_dir, vision_task_output_dir


@dataclass(frozen=True)
class ResumeHint:
    kind: str  # docling | vision
    out_dir: Path
    done: int
    total: int
    workflow: str


def find_output_markdown(
    out_dir: Path | None,
    stem: str,
    extra: Path | None = None,
) -> Path | None:
    """在候选里取最近改过的一份，避免打开旧的完整 md、漏掉更新的草稿。"""
    found: list[Path] = []
    seen: set[str] = set()

    def _add(path: Path | None) -> None:
        if path is None:
            return
        p = Path(path)
        try:
            key = str(p.resolve()) if p.exists() else str(p)
        except OSError:
            key = str(p)
        if key in seen or not p.is_file():
            return
        seen.add(key)
        found.append(p)

    _add(Path(extra) if extra else None)
    if out_dir:
        d = Path(out_dir)
        for name in (
            f"{stem}.md",
            f"{stem}.partial.md",
            f"{stem}.raw.md",
            f"{stem}.raw.partial.md",
        ):
            _add(d / name)
    if not found:
        return None
    return max(found, key=lambda p: p.stat().st_mtime)


def vision_resume_hint(out_dir: Path) -> ResumeHint | None:
    from app.vision_transcribe.manifest import load_manifest
    from app.vision_transcribe.models import BatchStatus

    if not out_dir or not Path(out_dir).is_dir():
        return None
    try:
        m = load_manifest(out_dir)
    except Exception:
        return None
    if m is None or not m.batches:
        return None
    if m.all_batches_accepted():
        return None
    done = 0
    for b in m.get_batches():
        if b.status == BatchStatus.ACCEPTED.value:
            start = int(b.start_page or 0)
            end = int(b.end_page or 0)
            if end >= start > 0:
                done += end - start + 1
    total = int(m.page_count or 0)
    return ResumeHint(
        kind="vision",
        out_dir=Path(out_dir),
        done=done,
        total=total,
        workflow=WorkflowChoice.VISION.value,
    )


def docling_resume_hint(out_dir: Path, stem: str) -> ResumeHint | None:
    ok, nxt = checkpoint_resumable(out_dir, stem)
    if not ok:
        return None
    data = load_checkpoint(out_dir) or {}
    total = int(data.get("total_pages") or 0)
    return ResumeHint(
        kind="docling",
        out_dir=Path(out_dir),
        done=max(0, nxt - 1),
        total=total,
        workflow=WorkflowChoice.STRUCTURED.value,
    )


def detect_unfinished(
    output_root: Path,
    pdf_path: Path,
    *,
    per_folder: bool,
    prefer_vision: bool = False,
    prefer_workflow: str | None = None,
) -> ResumeHint | None:
    """两种进度都在时，跟任务自己的路线走，不被当前 UI 带跑偏。"""
    vis_dir = vision_task_output_dir(output_root, pdf_path)
    struct_dir = task_output_dir(output_root, pdf_path, per_folder)
    vis = vision_resume_hint(vis_dir)
    doc = docling_resume_hint(struct_dir, pdf_path.stem)
    if prefer_workflow is not None:
        prefer_vision = prefer_workflow == WorkflowChoice.VISION.value
    if vis and doc:
        return vis if prefer_vision else doc
    return vis or doc


def record_can_resume(rec: dict) -> bool:
    """历史记录是否适合点「继续」。"""
    from app.task_model import TaskStatus

    status = str(rec.get("status") or "")
    if status in (
        TaskStatus.INTERRUPTED.value,
        TaskStatus.CANCELLED.value,
        TaskStatus.RUNNING.value,
        TaskStatus.FAILED.value,
    ):
        return True
    raw = rec.get("output_dir")
    if not raw:
        return False
    out = Path(str(raw))
    stem = Path(str(rec.get("path") or rec.get("name") or "doc")).stem
    if docling_resume_hint(out, stem):
        return True
    return vision_resume_hint(out) is not None


def partition_pdf_run_queue(
    tasks: list,
    *,
    vision_value: str = WorkflowChoice.VISION.value,
) -> list[tuple[str, list]]:
    """中断续跑优先，且按任务自己的路线拆队列，避免被当前 UI 模式带跑偏。"""
    resume_s: list = []
    resume_v: list = []
    fresh_s: list = []
    fresh_v: list = []
    for t in tasks:
        vis = getattr(t, "workflow", "") == vision_value
        res = bool(getattr(t, "resume_from_checkpoint", False))
        if res and vis:
            resume_v.append(t)
        elif res:
            resume_s.append(t)
        elif vis:
            fresh_v.append(t)
        else:
            fresh_s.append(t)
    out: list[tuple[str, list]] = []
    for kind, group in (
        ("structured", resume_s),
        ("vision", resume_v),
        ("structured", fresh_s),
        ("vision", fresh_v),
    ):
        if group:
            out.append((kind, group))
    return out


@dataclass(frozen=True)
class PdfRunDecision:
    workflow: str
    engine: str
    resume: bool
    vision_force_rerun: bool


def plan_pdf_run(
    *,
    workflow: str,
    engine: str,
    force_restart: bool,
    resume_requested: bool,
    ui_workflow: str,
    ui_engine: str,
    hint: ResumeHint | None,
    vision_should_force: bool = False,
) -> PdfRunDecision:
    """决定这一本怎么跑：重试保任务路线，续跑跟磁盘走，新任务才跟当前 UI。"""
    if force_restart:
        return PdfRunDecision(
            workflow=workflow,
            engine=engine,
            resume=False,
            vision_force_rerun=workflow == WorkflowChoice.VISION.value,
        )
    if hint is not None:
        return PdfRunDecision(
            workflow=hint.workflow,
            engine=engine,
            resume=True,
            vision_force_rerun=False,
        )
    if resume_requested:
        return PdfRunDecision(
            workflow=workflow,
            engine=engine,
            resume=True,
            vision_force_rerun=False,
        )
    return PdfRunDecision(
        workflow=ui_workflow,
        engine=ui_engine,
        resume=False,
        vision_force_rerun=(
            ui_workflow == WorkflowChoice.VISION.value and vision_should_force
        ),
    )


def apply_resume_hint(task, hint: ResumeHint) -> None:
    task.resume_from_checkpoint = True
    task.output_dir = hint.out_dir
    task.done_pages = hint.done
    if hint.total:
        task.total_pages = hint.total
        if getattr(task, "pages", None) is None:
            task.pages = hint.total
    task.workflow = hint.workflow
