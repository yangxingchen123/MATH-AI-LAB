"""EPUB 引擎：解包 / spine / XHTML→MD / 抽图，返回 ConversionResult。"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from app.engines.base import ConversionResult
from app.epub.assemble import assemble_markdown, write_internal_manifest
from app.epub.container import EpubPackage
from app.epub.html_convert import xhtml_to_markdown
from app.epub.opf import parse_opf
from app.epub.resources import ResourceRewriter
from app.parse_checkpoint import ParseInterrupted

ProgressCB = Callable[[str], None]
CancelledCB = Callable[[], bool]
PagesCB = Callable[[int, int], None]


def convert_epub(
    epub_path: Path,
    out_dir: Path,
    *,
    progress: ProgressCB | None = None,
    cancelled: CancelledCB | None = None,
    on_pages: PagesCB | None = None,
) -> ConversionResult:
    """将 EPUB 转为原始 Markdown，不做 PDF 公式/视觉修复。"""
    epub_path = Path(epub_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    def emit(msg: str) -> None:
        if progress:
            progress(msg)

    emit("EPUB：解包并校验…")
    images_dir = out_dir / "images"
    internal_dir = out_dir / ".epub"
    images_dir.mkdir(parents=True, exist_ok=True)
    internal_dir.mkdir(parents=True, exist_ok=True)

    warnings: list[str] = []
    chapter_rows: list[dict] = []
    bodies: list[str] = []

    with EpubPackage(epub_path, require_unencrypted=True) as pkg:
        opf = parse_opf(pkg)
        warnings.extend(opf.warnings)
        emit(f"EPUB：书名「{opf.title or epub_path.stem}」· {len(opf.spine)} 章")
        n = len(opf.spine)
        copied: dict[str, str] = {}
        used_names: set[str] = set()
        for i, item in enumerate(opf.spine, start=1):
            if cancelled and cancelled():
                raw_md = assemble_markdown(bodies, title=opf.title)
                draft = out_dir / f"{epub_path.stem}.partial.md"
                draft.write_text(
                    raw_md if raw_md.endswith("\n") else raw_md + "\n",
                    encoding="utf-8",
                )
                raise ParseInterrupted(
                    f"EPUB 已中断，已完成 {i - 1}/{n} 章",
                    next_page=i,
                    draft_path=draft,
                )
            emit(f"EPUB：解析章节 {i}/{n}")
            if on_pages:
                on_pages(i, n)
            html = pkg.read_text(item.zip_path)
            rewriter = ResourceRewriter(
                pkg,
                chapter_zip_path=item.zip_path,
                images_dir=images_dir,
                warnings=warnings,
                copied=copied,
                used_names=used_names,
            )
            body = xhtml_to_markdown(
                html,
                rewrite_href=rewriter.rewrite_href,
                rewrite_image=rewriter.rewrite_image,
            )
            chapter_name = f"chapter_{i:03d}.md"
            chapter_path = internal_dir / chapter_name
            chapter_path.write_text(body + ("\n" if body and not body.endswith("\n") else ""), encoding="utf-8")
            bodies.append(body)
            chapter_rows.append(
                {
                    "index": i,
                    "idref": item.idref,
                    "href": item.href,
                    "file": chapter_name,
                    "linear": item.linear,
                }
            )

    raw_md = assemble_markdown(bodies, title=opf.title)
    raw_path = out_dir / f"{epub_path.stem}.raw.md"
    raw_path.write_text(raw_md if raw_md.endswith("\n") else raw_md + "\n", encoding="utf-8")

    write_internal_manifest(
        internal_dir / "manifest.json",
        {
            "source": epub_path.name,
            "title": opf.title,
            "creator": opf.creator,
            "language": opf.language,
            "chapters": chapter_rows,
            "warnings": warnings,
        },
    )
    for w in warnings[:12]:
        emit(f"EPUB 提示：{w}")

    return ConversionResult(
        markdown_path=raw_path,
        parser="epub",
        artifacts_dir=images_dir,
        pages=len(chapter_rows),
        metadata={
            "title": opf.title,
            "creator": opf.creator,
            "language": opf.language,
            "warnings": warnings,
            "chapter_count": len(chapter_rows),
        },
    )
