"""解析 OPF：metadata、manifest、spine 阅读顺序。"""
from __future__ import annotations

from dataclasses import dataclass, field
from xml.etree import ElementTree as ET

from app.epub.container import EpubError, EpubPackage, local_name, zip_join, zip_norm

_XHTML_TYPES = {
    "application/xhtml+xml",
    "text/html",
    "application/xml",
    "text/xml",
}


@dataclass
class SpineItem:
    idref: str
    href: str
    zip_path: str
    media_type: str
    linear: bool = True


@dataclass
class OpfDocument:
    opf_zip_path: str
    title: str = ""
    creator: str = ""
    language: str = ""
    spine: list[SpineItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_opf(package: EpubPackage) -> OpfDocument:
    opf_path = package.container_rootfile()
    text = package.read_text(opf_path)
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise EpubError("OPF 无法解析。") from e

    doc = OpfDocument(opf_zip_path=opf_path)
    _fill_metadata(root, doc)
    manifest = _parse_manifest(root, opf_path)
    _fill_spine(root, doc, manifest, package)
    if not doc.spine:
        raise EpubError("OPF spine 为空，没有可转换的章节。")
    return doc


def peek_spine_count(epub_path) -> int | None:
    """只读 spine 长度；失败返回 None（进队时用）。"""
    from pathlib import Path

    try:
        with EpubPackage(Path(epub_path), require_unencrypted=False) as pkg:
            return len(parse_opf(pkg).spine)
    except Exception:
        return None


def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def _fill_metadata(root: ET.Element, doc: OpfDocument) -> None:
    for el in root.iter():
        name = local_name(el.tag).lower()
        if name == "title" and not doc.title:
            doc.title = _text(el)
        elif name == "creator" and not doc.creator:
            doc.creator = _text(el)
        elif name == "language" and not doc.language:
            doc.language = _text(el)


def _parse_manifest(root: ET.Element, opf_path: str) -> dict[str, tuple[str, str]]:
    """id → (zip_path, media_type)"""
    items: dict[str, tuple[str, str]] = {}
    for el in root.iter():
        if local_name(el.tag).lower() != "item":
            continue
        item_id = (el.get("id") or "").strip()
        href = (el.get("href") or "").strip()
        media = (el.get("media-type") or "").strip()
        if not media:
            for k, v in el.attrib.items():
                if local_name(k).lower() == "media-type":
                    media = (v or "").strip()
                    break
        if not item_id or not href:
            continue
        zip_path = zip_join(opf_path, href)
        items[item_id] = (zip_path, media.lower())
    return items


def _looks_like_chapter(zip_path: str, media_type: str) -> bool:
    if media_type in _XHTML_TYPES:
        return True
    ext = zip_norm(zip_path).rsplit(".", 1)[-1].lower() if "." in zip_path else ""
    return ext in {"xhtml", "html", "htm", "xml"}


def _fill_spine(
    root: ET.Element,
    doc: OpfDocument,
    manifest: dict[str, tuple[str, str]],
    package: EpubPackage,
) -> None:
    for el in root.iter():
        if local_name(el.tag).lower() != "itemref":
            continue
        idref = (el.get("idref") or "").strip()
        if not idref:
            continue
        linear = (el.get("linear") or "yes").strip().lower() != "no"
        hit = manifest.get(idref)
        if hit is None:
            doc.warnings.append(f"spine 引用了不存在的 manifest 项：{idref}")
            continue
        zip_path, media = hit
        if not _looks_like_chapter(zip_path, media):
            doc.warnings.append(f"跳过非章节 spine 项：{idref} ({media or zip_path})")
            continue
        if package.resolve(zip_path) is None:
            doc.warnings.append(f"章节文件缺失：{zip_path}")
            continue
        href = zip_path
        doc.spine.append(
            SpineItem(
                idref=idref,
                href=href,
                zip_path=zip_path,
                media_type=media,
                linear=linear,
            )
        )
