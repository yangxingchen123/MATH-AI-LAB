"""源格式注册表：后缀 → kind → 能力。跨格式判断只放这里。"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

KIND_PDF = "pdf"
KIND_EPUB = "epub"

_SUFFIX_TO_KIND = {
    ".pdf": KIND_PDF,
    ".epub": KIND_EPUB,
}


@dataclass(frozen=True)
class FormatCapabilities:
    kind: str
    vision: bool
    formula_ocr: bool
    engines: bool
    unit: str  # pdf_pages | spine_chapters


_CAPABILITIES = {
    KIND_PDF: FormatCapabilities(
        kind=KIND_PDF,
        vision=True,
        formula_ocr=True,
        engines=True,
        unit="pdf_pages",
    ),
    KIND_EPUB: FormatCapabilities(
        kind=KIND_EPUB,
        vision=False,
        formula_ocr=False,
        engines=False,
        unit="spine_chapters",
    ),
}


def kind_for_path(path: Path | str) -> str | None:
    suffix = Path(path).suffix.lower()
    return _SUFFIX_TO_KIND.get(suffix)


def accepts_file(path: Path | str) -> bool:
    p = Path(path)
    return p.is_file() and kind_for_path(p) is not None


def capabilities(kind: str) -> FormatCapabilities:
    cap = _CAPABILITIES.get(kind)
    if cap is None:
        raise KeyError(kind)
    return cap


def iter_input_files(path: Path | str) -> list[Path]:
    """文件或文件夹 → 已支持的输入路径（去重、保持发现顺序）。"""
    root = Path(path)
    found: list[Path] = []
    seen: set[str] = set()

    def add(p: Path) -> None:
        try:
            key = str(p.resolve())
        except OSError:
            key = str(p)
        if key in seen:
            return
        seen.add(key)
        found.append(p)

    if root.is_file():
        if kind_for_path(root) is not None:
            add(root)
        return found
    if not root.is_dir():
        return found
    for p in sorted(root.rglob("*")):
        if p.is_file() and kind_for_path(p) is not None:
            add(p)
    return found
