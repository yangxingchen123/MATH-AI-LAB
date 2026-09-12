"""Docling 引擎：优先 Python API，默认走快速配置；模型优先用本地缓存。"""
from __future__ import annotations

import inspect
import os
import time
from pathlib import Path
from typing import Any, Callable

from app.parse_checkpoint import (
    BATCH_PAGE_THRESHOLD,
    ParseInterrupted,
    STATUS_DONE,
    adaptive_page_batch_size,
    append_batch,
    checkpoint_resumable,
    load_checkpoint,
    mark_checkpoint,
    new_checkpoint,
    partial_raw_path,
    resume_start_page,
    save_checkpoint,
    should_batch_pages,
    write_interrupt_draft,
)
from app.utils.paths import DOCLING_ARTIFACTS_DIR

ProgressCB = Callable[[str], None]
CancelledCB = Callable[[], bool]
PagesCB = Callable[[int, int], None]

# 复用转换器，避免每个 PDF 重复加载模型
_converter_cache: dict[tuple, object] = {}
_converter_create_count = 0

LOCAL_ARTIFACTS = DOCLING_ARTIFACTS_DIR


def _ensure_hf_mirror() -> None:
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    # 避免 transformers 误加载残缺 TensorFlow
    os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
    os.environ.setdefault("USE_TF", "0")
    os.environ.setdefault("USE_TORCH", "1")


def _build_pipeline(
    *,
    keep_images: bool,
    keep_tables: bool,
    keep_formulas: bool,
    ocr_mode: str,
    images_scale: float = 2.0,
):
    from docling.datamodel.pipeline_options import (
        AcceleratorDevice,
        AcceleratorOptions,
        PdfPipelineOptions,
        TableFormerMode,
        TableStructureOptions,
    )

    pipeline = PdfPipelineOptions()

    # 本地已缓存的 Docling 模型，避免运行时再去 HuggingFace 拉文件失败
    if LOCAL_ARTIFACTS.exists():
        pipeline.artifacts_path = LOCAL_ARTIFACTS

    # OCR：自动/禁用都先关；仅「强制 OCR」开启（文字层 PDF 开 OCR 极慢）
    pipeline.do_ocr = ocr_mode == "force"

    # 表格：需要时用 FAST 模式
    pipeline.do_table_structure = keep_tables
    if keep_tables:
        pipeline.table_structure_options = TableStructureOptions(
            mode=TableFormerMode.FAST
        )

    # 公式：开启后会跑 CodeFormula 模型，把公式图转成 LaTeX；关闭则留下 placeholder
    pipeline.do_formula_enrichment = bool(keep_formulas)
    pipeline.do_code_enrichment = False
    pipeline.do_picture_classification = False
    pipeline.do_picture_description = False
    if hasattr(pipeline, "do_chart_extraction"):
        pipeline.do_chart_extraction = False

    # 标题层级：用字号/字体粗细推断 heading level（不直接恢复正文粗体，但有助于结构）
    try:
        pipeline.heading_hierarchy_options.enabled = True
    except Exception:
        pass

    # 图片：scale 越大越清晰，也越慢（1=快速，2=标准，3=高清）
    scale = max(1.0, min(3.0, float(images_scale)))
    pipeline.generate_page_images = False
    pipeline.generate_picture_images = keep_images
    pipeline.images_scale = scale

    # 加速器：有 CUDA 用 GPU，否则拉满 CPU 线程
    threads = min(16, max(4, (os.cpu_count() or 8)))
    try:
        import torch

        use_cuda = bool(torch.cuda.is_available())
    except Exception:
        use_cuda = False

    pipeline.accelerator_options = AcceleratorOptions(
        num_threads=threads,
        device=AcceleratorDevice.CUDA if use_cuda else AcceleratorDevice.CPU,
    )
    return pipeline, use_cuda, threads


def _get_converter(
    *,
    keep_images: bool,
    keep_tables: bool,
    keep_formulas: bool,
    ocr_mode: str,
    images_scale: float = 2.0,
):
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption

    from app.engines.docling_telemetry import record_converter_access

    key = (
        keep_images,
        keep_tables,
        keep_formulas,
        ocr_mode,
        float(images_scale),
        str(LOCAL_ARTIFACTS),
    )
    key_s = ",".join(str(x) for x in key)
    cached = _converter_cache.get(key)
    if cached is not None:
        record_converter_access(created=False, key=key_s, init_seconds=0.0)
        # 缓存命中时仍回传设备信息，避免日志漏掉「加速设备」
        try:
            import torch

            use_cuda = bool(torch.cuda.is_available())
        except Exception:
            use_cuda = False
        threads = min(16, max(4, (os.cpu_count() or 8)))
        return cached, use_cuda, threads, True

    t_init = time.perf_counter()
    pipeline, use_cuda, threads = _build_pipeline(
        keep_images=keep_images,
        keep_tables=keep_tables,
        keep_formulas=keep_formulas,
        ocr_mode=ocr_mode,
        images_scale=images_scale,
    )
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline),
        }
    )
    init_s = time.perf_counter() - t_init
    _converter_cache[key] = converter
    global _converter_create_count
    _converter_create_count += 1
    record_converter_access(created=True, key=key_s, init_seconds=init_s)
    return converter, use_cuda, threads, False


def _rewrite_image_paths(md_text: str, md_path: Path, *, relative: bool) -> str:
    """把 Markdown 图片链接改成相对或绝对路径。"""
    import re

    md_dir = md_path.parent.resolve()
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    def repl(m: re.Match[str]) -> str:
        alt, raw = m.group(1), m.group(2).strip().strip('"').strip("'")
        # 忽略 data URI / http(s)
        if raw.startswith(("http://", "https://", "data:")):
            return m.group(0)
        try:
            p = Path(raw)
            if not p.is_absolute():
                p = (md_dir / p).resolve()
            else:
                p = p.resolve()
        except Exception:
            return m.group(0)

        if relative:
            try:
                rel = os.path.relpath(p, md_dir)
            except ValueError:
                rel = str(p)
            # Markdown 通用正斜杠
            link = rel.replace("\\", "/")
        else:
            link = str(p)
        return f"![{alt}]({link})"

    return pattern.sub(repl, md_text)


def _export_markdown(
    result,
    md_path: Path,
    keep_images: bool,
    *,
    image_path_mode: str = "relative",
) -> None:
    """仅导出解析器原始 Markdown，不做智能修复。"""
    images_dir = md_path.parent / "images"
    text: str | None = None
    if keep_images:
        images_dir.mkdir(parents=True, exist_ok=True)
        try:
            from docling_core.types.doc import ImageRefMode

            result.document.save_as_markdown(
                md_path,
                image_mode=ImageRefMode.REFERENCED,
                artifacts_dir=images_dir,
            )
            text = md_path.read_text(encoding="utf-8")
            text = _rewrite_image_paths(
                text,
                md_path,
                relative=(image_path_mode != "absolute"),
            )
        except Exception:
            text = None
    if text is None:
        text = result.document.export_to_markdown()
    md_path.write_text(text, encoding="utf-8")


def _looks_like_table_model_failure(exc: BaseException) -> bool:
    """仅在错误明确与 TableFormer / 表格结构模型相关时，才允许关闭表格重试。

    旧逻辑把任意 HuggingFace/Hub 失败都当成「表格不可用」，会在公式/布局
    模型短暂联网失败时误关表格（与 AssetPipeline 无关的历史问题）。
    """
    msg = str(exc).lower()
    name = type(exc).__name__.lower()
    markers = (
        "tableformer",
        "table_structure",
        "table structure",
        "model_artifacts/tableformer",
        "tableformer_fast",
        "tableformer_accurate",
        "/tableformer/",
    )
    if any(m in msg for m in markers):
        return True
    hub_hit = (
        "huggingface" in msg
        or "localentrynotfound" in name
        or "filemetadataerror" in name
        or "hf_hub" in msg
        or "hf hub" in msg
    )
    return bool(hub_hit and "table" in msg)


def converter_supports_page_range(converter: Any) -> bool:
    """探测 convert() 是否接受 page_range；禁止靠耗时伪造页码。"""
    fn = getattr(converter, "convert", None)
    if not callable(fn):
        return False
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return False
    return "page_range" in sig.parameters


def _pdf_page_count(pdf_path: Path, fallback: int | None = None) -> int | None:
    if fallback and int(fallback) > 0:
        return int(fallback)
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(pdf_path)).pages)
    except Exception:
        return None


def _call_convert(converter: Any, pdf_path: Path, page_range: tuple[int, int] | None):
    if page_range is None:
        return converter.convert(str(pdf_path))
    return converter.convert(str(pdf_path), page_range=page_range)


def convert_pdf(
    pdf_path: Path,
    out_dir: Path,
    *,
    keep_images: bool = True,
    keep_tables: bool = True,
    keep_formulas: bool = True,
    ocr_mode: str = "auto",
    images_scale: float = 2.0,
    image_path_mode: str = "relative",
    progress: ProgressCB | None = None,
    cancelled: CancelledCB | None = None,
    resume: bool = False,
    on_pages: PagesCB | None = None,
    total_pages: int | None = None,
    converter: Any | None = None,
    page_batch_size: int | None = None,
    page_batch_threshold: int = BATCH_PAGE_THRESHOLD,
    force_restart: bool = False,
):
    """将 PDF 转为原始 Markdown，返回 ConversionResult。

    大文档（≥ threshold 页）且 convert 支持 page_range 时按批解析，
    每批写入 checkpoint / partial，取消后可从 next_page 续跑。
    未指定 page_batch_size 时按页数自适应：40–79 页每批 8 页，更厚每批 10 页。
    """
    from app.engines.base import ConversionResult
    from app.parse_checkpoint import page_batches

    _ensure_hf_mirror()

    def emit(msg: str) -> None:
        if progress:
            progress(msg)

    def stop_requested() -> bool:
        return bool(cancelled and cancelled())

    pdf_path = Path(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = pdf_path.stem
    raw_path = out_dir / f"{stem}.raw.md"
    emit("正在加载 Docling...")

    from app.engines.docling_telemetry import record_convert_phases

    t_init0 = time.perf_counter()
    reused = True
    use_cuda = None
    threads = 0
    injected_converter = converter is not None
    if not injected_converter:
        converter, use_cuda, threads, reused = _get_converter(
            keep_images=keep_images,
            keep_tables=keep_tables,
            keep_formulas=keep_formulas,
            ocr_mode=ocr_mode,
            images_scale=images_scale,
        )
    init_seconds = time.perf_counter() - t_init0
    if use_cuda is not None:
        device = "CUDA GPU" if use_cuda else f"CPU ({threads} threads)"
        emit(f"加速设备：{device}")
    emit(
        "Docling converter："
        + ("复用缓存" if reused else f"新建（init {init_seconds:.1f}s）")
    )
    emit("公式识别：" + ("开启" if keep_formulas else "关闭"))
    emit("表格结构：" + ("开启" if keep_tables else "关闭"))
    if keep_images:
        emit(f"图片质量：scale={float(images_scale):.1f}")
        emit(
            "图片路径："
            + ("相对路径" if image_path_mode != "absolute" else "绝对路径")
        )

    n_pages = _pdf_page_count(pdf_path, total_pages)
    resolved_batch = (
        max(1, int(page_batch_size))
        if page_batch_size is not None
        else adaptive_page_batch_size(n_pages)
    )
    supported = converter_supports_page_range(converter)
    use_batches = should_batch_pages(
        n_pages, supported=supported, threshold=page_batch_threshold
    )
    if force_restart:
        resume = False
        if use_batches:
            emit("按重试从头解析，忽略上次中断进度")
    elif use_batches and n_pages:
        ok, nxt = checkpoint_resumable(out_dir, stem)
        if ok:
            resume = True
            emit(
                f"发现未完成进度：已完成 {nxt - 1}/{n_pages} 页，"
                f"从第 {nxt} 页继续（不整本重跑）"
            )

    def convert_once(page_range: tuple[int, int] | None):
        nonlocal converter
        try:
            return _call_convert(converter, pdf_path, page_range)
        except Exception as e:
            if (
                keep_tables
                and not injected_converter
                and _looks_like_table_model_failure(e)
            ):
                emit(f"TableFormer 模型不可用，改为无表格结构重试：{e}")
                _converter_cache.clear()
                converter, _, _, _ = _get_converter(
                    keep_images=keep_images,
                    keep_tables=False,
                    keep_formulas=keep_formulas,
                    ocr_mode=ocr_mode,
                    images_scale=images_scale,
                )
                return _call_convert(converter, pdf_path, page_range)
            raise

    def warn_undecoded(path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8")
            n = text.count("<!-- formula-not-decoded -->")
            if n:
                emit(f"警告：仍有 {n} 处公式未解码（formula-not-decoded）")
        except Exception:
            pass

    t0 = time.time()
    t_conv0 = time.perf_counter()
    export_seconds = 0.0

    if not use_batches:
        if n_pages:
            emit(f"解析中，共 {n_pages} 页")
            if on_pages:
                on_pages(0, n_pages)
        else:
            emit("正在解析 PDF...")
        result = convert_once(None)
        convert_seconds = time.perf_counter() - t_conv0
        emit("正在生成原始 Markdown...")
        t_exp0 = time.perf_counter()
        _export_markdown(
            result,
            raw_path,
            keep_images,
            image_path_mode=image_path_mode,
        )
        export_seconds = time.perf_counter() - t_exp0
        warn_undecoded(raw_path)
        if n_pages and on_pages:
            on_pages(n_pages, n_pages)
        mark_checkpoint(out_dir, STATUS_DONE, next_page=(n_pages or 0) + 1)
    else:
        assert n_pages is not None
        start_page = resume_start_page(out_dir, stem) if resume else 1
        partial = partial_raw_path(out_dir, stem)
        if start_page <= 1:
            start_page = 1
            if partial.exists():
                partial.unlink()
            save_checkpoint(
                out_dir,
                new_checkpoint(
                    total_pages=n_pages,
                    raw_md=partial.name,
                    pdf_path=str(pdf_path),
                    next_page=1,
                ),
            )
        elif not load_checkpoint(out_dir):
            save_checkpoint(
                out_dir,
                new_checkpoint(
                    total_pages=n_pages,
                    raw_md=partial.name,
                    pdf_path=str(pdf_path),
                    next_page=start_page,
                ),
            )
        done_so_far = max(0, start_page - 1)
        if on_pages:
            on_pages(done_so_far, n_pages)
        if done_so_far:
            emit(
                f"续跑：已完成 {done_so_far}/{n_pages} 页，"
                f"从第 {start_page} 页接着转换"
            )
            emit(f"解析 {done_so_far}/{n_pages}")
        else:
            emit(f"从头解析，共 {n_pages} 页")
            emit(f"解析 0/{n_pages}")

        batches = page_batches(
            n_pages, start_page=start_page, batch_size=resolved_batch
        )
        emit(
            f"分页解析：每批 {resolved_batch} 页，"
            f"从第 {start_page} 页起共 {len(batches)} 批"
        )
        for a, b in batches:
            if stop_requested():
                draft = write_interrupt_draft(out_dir, stem)
                raise ParseInterrupted(
                    f"解析已中断，已完成 {a - 1}/{n_pages} 页",
                    next_page=a,
                    draft_path=draft,
                )
            t_batch0 = time.perf_counter()
            result = convert_once((a, b))
            t_exp0 = time.perf_counter()
            tmp = out_dir / f".batch_{a}_{b}.md"
            try:
                _export_markdown(
                    result,
                    tmp,
                    keep_images,
                    image_path_mode=image_path_mode,
                )
                chunk = tmp.read_text(encoding="utf-8") if tmp.is_file() else ""
            finally:
                try:
                    if tmp.is_file():
                        tmp.unlink()
                except OSError:
                    pass
            export_seconds += time.perf_counter() - t_exp0
            if chunk:
                existing = partial.is_file() and partial.stat().st_size > 0
                with partial.open("a", encoding="utf-8") as fh:
                    if existing:
                        fh.write("\n\n")
                    fh.write(chunk)
            append_batch(
                out_dir,
                start=a,
                end=b,
                chars=len(chunk),
                raw_md=partial.name,
                total_pages=n_pages,
                pdf_path=str(pdf_path),
            )
            if on_pages:
                on_pages(b, n_pages)
            batch_s = time.perf_counter() - t_batch0
            emit(
                f"本批第 {a}–{b} 页完成，累计 {b}/{n_pages}，耗时 {batch_s:.1f}s"
            )
            emit(f"解析 {b}/{n_pages}")

        convert_seconds = time.perf_counter() - t_conv0
        if partial.is_file():
            raw_path.write_text(partial.read_text(encoding="utf-8"), encoding="utf-8")
            emit(f"已将中断草稿合并为 {raw_path.name}")
        else:
            raw_path.write_text("", encoding="utf-8")
        warn_undecoded(raw_path)
        mark_checkpoint(
            out_dir,
            STATUS_DONE,
            next_page=n_pages + 1,
            raw_md=raw_path.name,
        )
        try:
            if partial.is_file():
                partial.unlink()
        except OSError:
            pass

    artifacts = out_dir / "images"
    elapsed = time.time() - t0
    phases = record_convert_phases(
        init_seconds=init_seconds,
        convert_seconds=convert_seconds,
        export_seconds=export_seconds,
    )
    emit(
        f"解析完成，耗时 {elapsed:.1f}s "
        f"(init {phases['docling_init_seconds']}s / "
        f"convert {phases['docling_convert_seconds']}s / "
        f"export {phases['docling_export_seconds']}s，"
        f"reused={phases['converter_reused']}) → {raw_path.name}"
    )
    return ConversionResult(
        markdown_path=raw_path,
        parser="docling",
        artifacts_dir=artifacts if artifacts.exists() else None,
        pages=n_pages,
        metadata={
            "elapsed_sec": elapsed,
            "keep_formulas": keep_formulas,
            "keep_tables": keep_tables,
            "images_scale": images_scale,
            "docling": phases,
            "batched": use_batches,
            "page_batch_size": resolved_batch if use_batches else None,
        },
    )
