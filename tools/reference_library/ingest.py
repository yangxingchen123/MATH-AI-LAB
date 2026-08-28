"""Paper identity ingest. PDF→MD remains a Sidecar; missing engine is DEGRADED."""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

from .constants import IDENTITY_TEMPLATE, REFERENCE_ROOT, REPO_ROOT


@dataclass(frozen=True)
class IngestResult:
    status: str
    path: Path | None
    message: str
    parse_status: str = "NONE"
    source_sha256: str = ""


def _safe_segment(value: str) -> bool:
    if not value or value != value.strip():
        return False
    if any(item in value for item in ("/", "\\", "..", "\x00")):
        return False
    return True


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ingest_paper(
    *,
    slug: str,
    title: str,
    domain: str,
    pdf: Path | None = None,
    repo_root: Path | None = None,
) -> IngestResult:
    if not _safe_segment(slug) or not _safe_segment(domain):
        return IngestResult("REJECTED", None, "slug and domain must be single path segments")
    root = Path(repo_root or REPO_ROOT)
    dest = root / "03_参考资料" / "论文" / domain / slug
    identity_path = dest / "identity.md"
    if identity_path.is_file():
        return IngestResult("NO_OP", identity_path, "identity.md already exists")
    source_path = ""
    source_sha = ""
    parse_status = "NONE"
    dest.mkdir(parents=True, exist_ok=True)
    if pdf is not None:
        pdf = Path(pdf)
        if not pdf.is_file():
            shutil.rmtree(dest, ignore_errors=True)
            return IngestResult("REJECTED", None, f"pdf not found: {pdf}")
        source_sha = file_sha256(pdf)
        stored = dest / "source.pdf"
        if pdf.resolve() != stored.resolve():
            shutil.copy2(pdf, stored)
        source_path = str(stored)
        parse_status = "DEGRADED"
    template = IDENTITY_TEMPLATE.read_text(encoding="utf-8")
    if repo_root is not None:
        candidate = root / "03_参考资料" / "_模板" / "文献条目_v1.md"
        if candidate.is_file():
            template = candidate.read_text(encoding="utf-8")
    text = (
        template.replace("{{TITLE}}", title)
        .replace("{{SLUG}}", slug)
        .replace("{{DOMAIN}}", domain)
        .replace("{{IDENTITY_KIND}}", "LOCAL")
        .replace("{{SOURCE_PATH}}", source_path)
        .replace("{{SOURCE_SHA256}}", source_sha)
        .replace("parse_status: NONE", f"parse_status: {parse_status}")
    )
    identity_path.write_text(text, encoding="utf-8", newline="\n")
    return IngestResult(
        "WRITTEN",
        identity_path,
        "registered paper identity; PDF→MD sidecar not invoked",
        parse_status=parse_status,
        source_sha256=source_sha,
    )


def ingest_contest(
    *,
    contest: str,
    slug: str,
    title: str,
    pdf: Path | None = None,
    repo_root: Path | None = None,
) -> IngestResult:
    if not _safe_segment(contest) or not _safe_segment(slug):
        return IngestResult("REJECTED", None, "contest and slug must be single path segments")
    root = Path(repo_root or REPO_ROOT)
    dest = root / "03_参考资料" / "竞赛" / contest / slug
    identity_path = dest / "identity.md"
    if identity_path.is_file():
        return IngestResult("NO_OP", identity_path, "identity.md already exists")
    source_path = ""
    source_sha = ""
    parse_status = "NONE"
    dest.mkdir(parents=True, exist_ok=True)
    if pdf is not None:
        pdf = Path(pdf)
        if not pdf.is_file():
            shutil.rmtree(dest, ignore_errors=True)
            return IngestResult("REJECTED", None, f"pdf not found: {pdf}")
        source_sha = file_sha256(pdf)
        stored = dest / "source.pdf"
        if pdf.resolve() != stored.resolve():
            shutil.copy2(pdf, stored)
        source_path = str(stored)
        parse_status = "DEGRADED"
    template = IDENTITY_TEMPLATE.read_text(encoding="utf-8")
    candidate = root / "03_参考资料" / "_模板" / "文献条目_v1.md"
    if candidate.is_file():
        template = candidate.read_text(encoding="utf-8")
    text = (
        template.replace("{{TITLE}}", title)
        .replace("{{SLUG}}", slug)
        .replace("{{DOMAIN}}", contest)
        .replace("{{IDENTITY_KIND}}", "LOCAL")
        .replace("{{SOURCE_PATH}}", source_path)
        .replace("{{SOURCE_SHA256}}", source_sha)
        .replace("parse_status: NONE", f"parse_status: {parse_status}")
    )
    identity_path.write_text(text, encoding="utf-8", newline="\n")
    return IngestResult(
        "WRITTEN",
        identity_path,
        "registered contest problem identity; PDF→MD sidecar not invoked",
        parse_status=parse_status,
        source_sha256=source_sha,
    )


def doctor(*, repo_root: Path | None = None) -> dict:
    root = Path(repo_root or REPO_ROOT)
    base = root / "03_参考资料"
    missing = [name for name in ("教材", "论文", "竞赛", "讲义") if not (base / name).is_dir()]
    return {
        "status": "PASS" if not missing else "DEGRADED",
        "core_impact": False,
        "contract_version": "0.1",
        "missing_taxonomy": missing,
        "reference_root": str(base if base.is_dir() else REFERENCE_ROOT),
        "note": "Identity ingest only. MinerU PDF→MD is a Sidecar and must not fail Core.",
    }
