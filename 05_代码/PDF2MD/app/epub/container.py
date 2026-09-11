"""打开 EPUB ZIP、校验 mimetype / container.xml、检测 DRM。"""
from __future__ import annotations

import posixpath
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


class EpubError(Exception):
    """EPUB 无法作为未加密书籍打开。"""


class EpubEncryptedError(EpubError):
    def __init__(self, path: Path | None = None) -> None:
        loc = f"（{path.name}）" if path is not None else ""
        super().__init__(f"该 EPUB{loc} 受 DRM 加密保护，无法转换。")


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def zip_norm(name: str) -> str:
    return name.replace("\\", "/").lstrip("/")


def zip_join(base_file: str, rel: str) -> str:
    rel = zip_norm(rel.split("?", 1)[0].split("#", 1)[0])
    if not rel:
        return zip_norm(base_file)
    directory = posixpath.dirname(zip_norm(base_file))
    return posixpath.normpath(posixpath.join(directory, rel))


class EpubPackage:
    """一本打开的 EPUB。用作 context manager。"""

    def __init__(self, path: Path, *, require_unencrypted: bool = True) -> None:
        self.path = Path(path)
        self.require_unencrypted = require_unencrypted
        self._zip: ZipFile | None = None
        self._names_lower: dict[str, str] = {}

    def __enter__(self) -> "EpubPackage":
        if not self.path.is_file():
            raise EpubError(f"找不到文件：{self.path}")
        try:
            self._zip = ZipFile(self.path)
        except BadZipFile as e:
            raise EpubError("不是有效的 EPUB（无法作为 ZIP 打开）。") from e
        self._names_lower = {zip_norm(n).lower(): zip_norm(n) for n in self._zip.namelist()}
        if self.require_unencrypted and self.is_encrypted():
            self.close()
            raise EpubEncryptedError(self.path)
        self._check_mimetype()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        if self._zip is not None:
            try:
                self._zip.close()
            except OSError:
                pass
            self._zip = None

    @property
    def zip(self) -> ZipFile:
        if self._zip is None:
            raise EpubError("EPUB 未打开。")
        return self._zip

    def resolve(self, name: str) -> str | None:
        key = zip_norm(name).lower()
        return self._names_lower.get(key)

    def has(self, name: str) -> bool:
        return self.resolve(name) is not None

    def read(self, name: str) -> bytes:
        real = self.resolve(name)
        if real is None:
            raise EpubError(f"EPUB 内缺少文件：{name}")
        return self.zip.read(real)

    def read_text(self, name: str) -> str:
        raw = self.read(name)
        for enc in ("utf-8-sig", "utf-8", "utf-16"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")

    def is_encrypted(self) -> bool:
        return self.has("META-INF/encryption.xml")

    def container_rootfile(self) -> str:
        if not self.has("META-INF/container.xml"):
            raise EpubError("不是有效的 EPUB（缺少 META-INF/container.xml）。")
        text = self.read_text("META-INF/container.xml")
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            raise EpubError("container.xml 无法解析。") from e
        for el in root.iter():
            if local_name(el.tag).lower() != "rootfile":
                continue
            full = (el.get("full-path") or "").strip()
            if full:
                resolved = self.resolve(full)
                if resolved is None:
                    raise EpubError(f"OPF 不存在：{full}")
                return resolved
        raise EpubError("container.xml 未声明 OPF rootfile。")

    def _check_mimetype(self) -> None:
        if not self.has("mimetype"):
            raise EpubError("不是有效的 EPUB（缺少 mimetype）。")
        raw = self.read("mimetype").decode("ascii", errors="replace").strip()
        compact = "".join(raw.split()).lower()
        if compact != "application/epub+zip":
            raise EpubError(f"不是有效的 EPUB（mimetype={raw!r}）。")
