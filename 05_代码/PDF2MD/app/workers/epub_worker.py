"""EPUB 后台 Worker（QThread）：EpubEngine → 导出硬规则 → 最终 Markdown。

不调用 Docling / RepairPipeline / FormulaPipeline / 视觉转录。
"""
from __future__ import annotations

import time
import traceback
from pathlib import Path

from PySide6.QtCore import QMutex, QThread, Signal

from app.engines.epub_engine import convert_epub
from app.epub.assemble import apply_export_rules
from app.parse_checkpoint import ParseInterrupted
from app.task_model import ConvertTask, TaskStatus, queue_skip_status
from app.ui.pipeline_classify import classify_pipeline_stage
from app.utils.logger import get_logger, new_run_id, write_task_log
from app.utils.paths import task_output_dir


class EpubConversionWorker(QThread):
    task_status = Signal(str, str, str)
    task_finished = Signal(str, bool, str, str, str, float)
    task_progress = Signal(str, int, int)
    log_line = Signal(str)
    stage = Signal(str)
    pipeline_stage = Signal(str)

    def __init__(
        self,
        tasks: list[ConvertTask],
        *,
        output_root: Path,
        per_folder: bool,
        export_md: bool = True,
        export_raw_md: bool = False,
        export_conversion_log: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._tasks = list(tasks)
        self._output_root = Path(output_root)
        self._per_folder = bool(per_folder)
        self._export_md = bool(export_md)
        self._export_raw_md = bool(export_raw_md)
        self._export_conversion_log = bool(export_conversion_log)
        self._cancel = False
        self._mutex = QMutex()

    def request_cancel(self) -> None:
        self._mutex.lock()
        self._cancel = True
        self._mutex.unlock()

    def _cancelled(self) -> bool:
        self._mutex.lock()
        v = self._cancel
        self._mutex.unlock()
        return v

    def run(self) -> None:
        log = get_logger()
        for task in self._tasks:
            if self._cancelled():
                st, msg = queue_skip_status(task)
                self.task_status.emit(task.id, st, msg)
                continue

            self.task_status.emit(task.id, TaskStatus.RUNNING.value, "开始转换")
            self.stage.emit(f"正在转换：{task.name}")
            self.pipeline_stage.emit("parse")
            self.log_line.emit(f"开始转换 {task.name}（EPUB）")
            log.info("开始转换 %s 引擎=EPUB", task.name)

            src = task.source_path
            out_dir = task_output_dir(self._output_root, src, self._per_folder)
            out_dir.mkdir(parents=True, exist_ok=True)
            t0 = time.time()
            run_id = new_run_id()

            def progress(msg: str) -> None:
                self.stage.emit(msg)
                self.log_line.emit(msg)
                kind = classify_pipeline_stage(msg)
                if kind:
                    self.pipeline_stage.emit(kind)
                if self._export_conversion_log:
                    write_task_log(out_dir, msg, run_id=run_id)
                    write_task_log(out_dir, f"[{run_id}] {msg}")

            def on_pages(done: int, total: int) -> None:
                self.task_progress.emit(task.id, int(done), int(total))

            try:
                parsed = convert_epub(
                    src,
                    out_dir,
                    progress=progress,
                    cancelled=self._cancelled,
                    on_pages=on_pages,
                )
                progress(f"解析器：{parsed.parser} → {parsed.markdown_path.name}")
                self.pipeline_stage.emit("repair")
                raw_text = parsed.markdown_path.read_text(encoding="utf-8")
                final_text = apply_export_rules(raw_text)
                final_path = out_dir / f"{src.stem}.md"
                if self._export_md:
                    final_path.write_text(final_text, encoding="utf-8")
                    progress(f"已写出 {final_path.name}")
                if not self._export_raw_md:
                    try:
                        if parsed.markdown_path.is_file() and parsed.markdown_path.name.endswith(
                            ".raw.md"
                        ):
                            parsed.markdown_path.unlink()
                    except OSError:
                        pass
                if not self._export_conversion_log:
                    for p in [out_dir / "conversion.log", *out_dir.glob("conversion_*.log")]:
                        try:
                            if p.is_file():
                                p.unlink()
                        except OSError:
                            pass
                elapsed = time.time() - t0
                md_str = str(final_path) if self._export_md and final_path.is_file() else ""
                self.task_finished.emit(task.id, True, md_str, str(out_dir), "", elapsed)
                self.log_line.emit(f"完成 {task.name}")
                log.info("完成 %s -> %s", task.name, out_dir)
            except ParseInterrupted as e:
                elapsed = time.time() - t0
                md = str(e.draft_path) if e.draft_path else ""
                self.task_status.emit(task.id, TaskStatus.INTERRUPTED.value, "已中断")
                self.task_finished.emit(
                    task.id, False, md, str(out_dir), "INTERRUPTED", elapsed
                )
                self.log_line.emit(f"中断 {task.name}（已保留已完成章节）")
            except Exception as e:
                elapsed = time.time() - t0
                err = f"{e}\n{traceback.format_exc()}"
                if self._export_conversion_log:
                    write_task_log(out_dir, err, run_id=run_id)
                    write_task_log(out_dir, f"[{run_id}] FAILED: {e}")
                self.task_finished.emit(task.id, False, "", str(out_dir), str(e), elapsed)
                self.log_line.emit(f"失败 {task.name}: {e}")
                log.exception("失败 %s", task.name)

        self.stage.emit("空闲")
        self.pipeline_stage.emit("idle")
