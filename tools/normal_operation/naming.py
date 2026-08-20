"""Windows-safe artifact naming (deterministic, no Schema fields)."""

from __future__ import annotations

import re

_ILLEGAL = re.compile(r'[<>:"/\\|?*]')
_WS = re.compile(r"\s+")
_DEVICE = re.compile(
    r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)",
    re.IGNORECASE,
)


def sanitize_windows_filename(name: str, *, max_len: int = 120) -> str:
    """Sanitize a single path segment for Windows filesystems."""
    text = name.replace("\r", " ").replace("\n", " ")
    text = _ILLEGAL.sub("_", text)
    text = _WS.sub("_", text).strip(" ._")
    if not text:
        text = "untitled"
    if _DEVICE.match(text):
        text = f"_{text}"
    if len(text) > max_len:
        text = text[:max_len].rstrip(" ._")
    return text or "untitled"


def artifact_stem(problem_id: str, title: str) -> str:
    """Formal Problem artifact stem: <PID>_<sanitized title>."""
    safe_title = sanitize_windows_filename(title)
    return f"{problem_id}_{safe_title}"
