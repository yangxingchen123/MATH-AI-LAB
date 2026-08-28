"""Attach an external PDF→MD sidecar to a contest identity. Not MinerU."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from tools.reference_library.ingest import file_sha256
from tools.research_project.constants import REPO_ROOT

from .models import AttachResult


def _safe_segment(value: str) -> bool:
    if not value or value != value.strip():
        return False
    if any(item in value for item in ("/", "\\", "..", "\x00")):
        return False
    return True


def _upsert_field(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^- {re.escape(key)}:.*$", re.MULTILINE)
    line = f"- {key}: {value}"
    if pattern.search(text):
        return pattern.sub(line, text, count=1)
    if not text.endswith("\n"):
        text += "\n"
    parse = re.search(r"^- parse_status:.*\n", text, re.MULTILINE)
    if parse:
        return text[: parse.end()] + line + "\n" + text[parse.end() :]
    return text + line + "\n"


def attach_contest_md(
    *,
    contest: str,
    slug: str,
    md: Path,
    repo_root: Path | None = None,
) -> AttachResult:
    if not _safe_segment(contest) or not _safe_segment(slug):
        return AttachResult("REJECTED", "contest and slug must be single path segments")
    md = Path(md)
    if not md.is_file():
        return AttachResult("REJECTED", f"markdown not found: {md}")
    if not _safe_segment(md.name):
        return AttachResult("REJECTED", "markdown filename must be a single path segment")
    root = Path(repo_root or REPO_ROOT)
    dest_dir = root / "03_参考资料" / "竞赛" / contest / slug
    identity = dest_dir / "identity.md"
    if not identity.is_file():
        return AttachResult("REJECTED", "identity.md missing; ingest-contest first")
    digest = file_sha256(md)
    derived_dir = dest_dir / "derived"
    stored = derived_dir / md.name
    if stored.is_file() and file_sha256(stored) == digest:
        text = identity.read_text(encoding="utf-8")
        if f"derived_sha256: {digest}" in text:
            return AttachResult("NO_OP", "derived markdown already attached", stored, digest)
        text = _upsert_field(text, "derived_md", f"derived/{md.name}")
        text = _upsert_field(text, "derived_sha256", digest)
        identity.write_text(text, encoding="utf-8", newline="\n")
        return AttachResult(
            "WRITTEN",
            "updated identity for existing derived markdown",
            stored,
            digest,
        )
    derived_dir.mkdir(parents=True, exist_ok=True)
    if md.resolve() != stored.resolve():
        shutil.copy2(md, stored)
    text = identity.read_text(encoding="utf-8")
    text = _upsert_field(text, "derived_md", f"derived/{md.name}")
    text = _upsert_field(text, "derived_sha256", digest)
    identity.write_text(text, encoding="utf-8", newline="\n")
    return AttachResult("WRITTEN", "attached contest markdown sidecar", stored, digest)
