"""Source / template hash and LaTeX provenance helpers."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

GENERATOR_VERSION = "problem-artifact-v1.2"

TEMPLATE_FINGERPRINT_SEPARATOR = "\n--MATH-AI-LAB-TEMPLATE-FINGERPRINT--\n"

PROVENANCE_PROBLEM_RE = re.compile(r"^%\s*problem:\s*(\S+)\s*$", re.MULTILINE)
PROVENANCE_SOURCE_RE = re.compile(r"^%\s*source_sha256:\s*([0-9a-fA-F]+)\s*$", re.MULTILINE)
PROVENANCE_TEMPLATE_RE = re.compile(r"^%\s*template_sha256:\s*([0-9a-fA-F]+)\s*$", re.MULTILINE)
PROVENANCE_GEN_RE = re.compile(r"^%\s*generator_version:\s*(\S+)\s*$", re.MULTILINE)


def normalize_text_for_hash(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(normalize_text_for_hash(text).encode("utf-8")).hexdigest()


def problem_source_sha256(path: Path) -> str:
    return sha256_text(path.read_text(encoding="utf-8"))


def template_fingerprint(*, main_tex: str, cls_bytes: bytes) -> str:
    """Hash MATH-AI-LAB main.tex + pinned elegantbook.cls only (not vendor docs)."""
    payload = normalize_text_for_hash(main_tex).encode("utf-8") + TEMPLATE_FINGERPRINT_SEPARATOR.encode(
        "utf-8"
    ) + cls_bytes
    return hashlib.sha256(payload).hexdigest()


def template_files_sha256(template_dir: Path) -> str:
    """Legacy helper: hash main.tex in a template dir if present."""
    path = template_dir / "main.tex"
    if path.is_file():
        return sha256_text(path.read_text(encoding="utf-8"))
    return sha256_text("")


def render_provenance_header(
    *,
    problem_id: str,
    source_sha256: str,
    template_sha256: str,
    generator_version: str = GENERATOR_VERSION,
) -> str:
    return "\n".join(
        [
            "% MATH-AI-LAB GENERATED ARTIFACT",
            f"% problem: {problem_id}",
            f"% source_sha256: {source_sha256}",
            f"% template_sha256: {template_sha256}",
            f"% generator_version: {generator_version}",
            "",
        ]
    )


def parse_provenance(tex_text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    m = PROVENANCE_PROBLEM_RE.search(tex_text)
    if m:
        out["problem"] = m.group(1)
    m = PROVENANCE_SOURCE_RE.search(tex_text)
    if m:
        out["source_sha256"] = m.group(1).lower()
    m = PROVENANCE_TEMPLATE_RE.search(tex_text)
    if m:
        out["template_sha256"] = m.group(1).lower()
    m = PROVENANCE_GEN_RE.search(tex_text)
    if m:
        out["generator_version"] = m.group(1)
    return out
