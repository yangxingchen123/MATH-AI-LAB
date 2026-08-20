"""Pinned ElegantBook vendor resolution for P9 (no network, no global fallback)."""

from __future__ import annotations

import os
import re
from pathlib import Path

from .constants import (
    DEFAULT_TEMPLATE_REL,
    PINNED_ELEGANTBOOK_DIR,
)

PROVIDES_CLASS_RE = re.compile(
    r"\\ProvidesClass\{elegantbook\}\[([^\]]+)\]",
    re.MULTILINE,
)


def template_dir(repo_root: Path) -> Path:
    return Path(repo_root).resolve() / DEFAULT_TEMPLATE_REL


def pinned_vendor_dir(repo_root: Path) -> Path:
    return template_dir(repo_root) / PINNED_ELEGANTBOOK_DIR


def pinned_vendor_cls(repo_root: Path) -> Path:
    return pinned_vendor_dir(repo_root) / "elegantbook.cls"


def pinned_vendor_cls_exists(repo_root: Path) -> bool:
    path = pinned_vendor_cls(repo_root)
    return path.is_file() and path.stat().st_size > 0


def parse_provides_class(cls_text: str) -> str | None:
    m = PROVIDES_CLASS_RE.search(cls_text)
    return m.group(1).strip() if m else None


def texinputs_with_vendor(vendor_dir: Path, existing: str | None = None) -> str:
    """Prepend vendor dir; trailing os.pathsep keeps kpathsea default search path."""
    prefix = str(Path(vendor_dir).resolve())
    existing = existing or ""
    if existing:
        value = prefix + os.pathsep + existing
    else:
        value = prefix
    if not value.endswith(os.pathsep):
        value += os.pathsep
    return value


def xelatex_env_with_vendor(vendor_dir: Path, base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base_env if base_env is not None else os.environ)
    env["TEXINPUTS"] = texinputs_with_vendor(vendor_dir, env.get("TEXINPUTS", ""))
    return env
