"""从 EPUB 复制图片，并改写章节内 href。"""
from __future__ import annotations

import re
from pathlib import Path

from app.epub.container import EpubPackage, zip_join, zip_norm

_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}


class ResourceRewriter:
    def __init__(
        self,
        package: EpubPackage,
        *,
        chapter_zip_path: str,
        images_dir: Path,
        warnings: list[str],
        copied: dict[str, str] | None = None,
        used_names: set[str] | None = None,
    ) -> None:
        self.package = package
        self.chapter_zip_path = chapter_zip_path
        self.images_dir = images_dir
        self.warnings = warnings
        self._copied = copied if copied is not None else {}
        self._used_names = used_names if used_names is not None else set()

    def rewrite_image(self, src: str, alt: str) -> str:
        src = (src or "").strip()
        alt = (alt or "").strip()
        if not src:
            return alt
        if src.startswith(("http://", "https://", "data:")):
            self.warnings.append(f"跳过非本地图片：{src[:80]}")
            if src.startswith("data:"):
                return alt
            return f"![{alt}]({src})"
        zip_path = zip_join(self.chapter_zip_path, src)
        rel = self._copy_image(zip_path)
        if not rel:
            self.warnings.append(f"图片文件缺失：{src}")
            return f"![{alt}]({src})" if alt else ""
        return f"![{alt}]({rel})"

    def rewrite_href(self, href: str) -> str:
        href = (href or "").strip()
        if not href:
            return ""
        if href.startswith(("http://", "https://", "mailto:", "data:")):
            return href
        if href.startswith("#"):
            return href
        frag = ""
        path = href
        if "#" in href:
            path, frag = href.split("#", 1)
            frag = "#" + frag
        path = zip_norm(path)
        if not path:
            return frag
        # 章内 / 跨章：有片段用片段；否则用文件 stem 当锚点
        if frag:
            return frag
        stem = Path(path).stem
        stem = re.sub(r"[^\w\-]+", "-", stem, flags=re.UNICODE).strip("-")
        return f"#{stem}" if stem else ""

    def _copy_image(self, zip_path: str) -> str:
        real = self.package.resolve(zip_path)
        if real is None:
            return ""
        if real in self._copied:
            return self._copied[real]
        ext = Path(real).suffix.lower() or ".png"
        if ext not in _IMAGE_EXT:
            ext = ".png"
        base = Path(real).stem or "image"
        base = re.sub(r"[^\w\-]+", "_", base, flags=re.UNICODE).strip("_") or "image"
        name = f"{base}{ext}"
        n = 2
        while name.lower() in self._used_names:
            name = f"{base}_{n}{ext}"
            n += 1
        self._used_names.add(name.lower())
        dest = self.images_dir / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            dest.write_bytes(self.package.read(real))
        except Exception as e:
            self.warnings.append(f"无法写出图片 {real}：{e}")
            return ""
        rel = f"images/{name}"
        self._copied[real] = rel
        return rel
