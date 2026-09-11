"""按章拼接 raw.md，并套用导出硬规则。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.utils.md_postprocess import (
    ensure_figure_table_separation,
    normalize_display_math_multiline,
)


def assemble_markdown(
    chapter_bodies: list[str],
    *,
    title: str = "",
) -> str:
    parts: list[str] = []
    first = (chapter_bodies[0].lstrip() if chapter_bodies else "")
    if title and not first.startswith(f"# {title}"):
        parts.append(f"# {title}")
    for body in chapter_bodies:
        text = (body or "").strip()
        if text:
            parts.append(text)
    return "\n\n".join(parts).strip() + ("\n" if parts else "")


def apply_export_rules(md: str) -> str:
    """只跑与 PDF 共用的导出硬规则，不跑 Docling 残片修复。"""
    text = md or ""
    text = ensure_figure_table_separation(text)
    text = normalize_display_math_multiline(text)
    return text


def write_internal_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
