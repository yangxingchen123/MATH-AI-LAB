"""Problem → LaTeX materialization and artifact freshness (P9 reuse)."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from tools.latex_build import build_latex_project
from tools.latex_build.constants import DEFAULT_TEMPLATE_REL
from tools.latex_build.models import PublishStatus
from tools.latex_build.vendor import pinned_vendor_cls, pinned_vendor_cls_exists
from tools.problem_solution.slots import parse_canonical_slots, parse_legacy_part_slots
from tools.problem_solution.writer import find_problem_file
from tools.problem_validator.parser import extract_front_matter, parse_yaml_mapping

from .completion import inspect_problem_completion
from .freshness import (
    GENERATOR_VERSION,
    parse_provenance,
    problem_source_sha256,
    render_provenance_header,
    template_fingerprint,
)
from .naming import artifact_stem

ARTIFACT_KIND = "题目解答"
DEFAULT_DOMAIN = "未分类"
TEMPLATE_DEPENDENCY_MISSING = "TEMPLATE_DEPENDENCY_MISSING"
NON_CANONICAL_LOCAL_CLASS = "NON-CANONICAL LOCAL CLASS"
# Hashes of auto-copied cls files that may be removed after vendor injection.
KNOWN_GENERATED_CLS_SHA256 = frozenset(
    {
        # Template-root stub v1.2 previously copied into some fixtures
        "9c142fc7bff3ae5c7591e86948cb0c841c5aef4a1264dddfd483de1845118e97",
        # Pre-vendor auto-copy of the lecture-project working class
        "d95a279b5238901eb5423dfed10650d5064ea9d5feb6194701a68e30e3e2ccd3",
        # Official GitHub tag v4.7 archive elegantbook.cls
        "01c64c1e479d8a21e8cf5b7b6cf907449caa5b5c8a6f8241c1812a77ab3a4b7f",
    }
)


def template_sha_for_project(project_root: Path) -> str | None:
    """Fingerprint MATH-AI-LAB main.tex + pinned vendor cls. None if vendor missing."""
    if not pinned_vendor_cls_exists(project_root):
        return None
    main = project_root / DEFAULT_TEMPLATE_REL / "main.tex"
    main_text = main.read_text(encoding="utf-8") if main.is_file() else ""
    return template_fingerprint(
        main_tex=main_text,
        cls_bytes=pinned_vendor_cls(project_root).read_bytes(),
    )


def maybe_remove_generated_local_cls(project_dir: Path, repo_root: Path) -> str | None:
    """Remove auto-copied elegantbook.cls. Unknown hashes are not deleted."""
    local = project_dir / "elegantbook.cls"
    if not local.is_file():
        return None
    digest = hashlib.sha256(local.read_bytes()).hexdigest()
    known = set(KNOWN_GENERATED_CLS_SHA256)
    vendor = pinned_vendor_cls(repo_root)
    if vendor.is_file():
        known.add(hashlib.sha256(vendor.read_bytes()).hexdigest())
    if digest in known:
        local.unlink()
        return None
    return NON_CANONICAL_LOCAL_CLASS


class FreshnessState(str, Enum):
    MISSING = "MISSING"
    CURRENT = "CURRENT"
    STALE = "STALE"
    FAILED = "FAILED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    SKIPPED = "SKIPPED"


@dataclass
class ArtifactPaths:
    stem: str
    project_dir: Path
    entry_tex: Path
    formal_pdf: Path
    domain: str


@dataclass
class ArtifactInspect:
    latex: FreshnessState
    pdf: FreshnessState
    paths: ArtifactPaths | None = None
    source_sha256: str | None = None
    template_sha256: str | None = None
    error: str | None = None


@dataclass
class MaterializeResult:
    written: bool
    paths: ArtifactPaths | None
    error: str | None = None


@dataclass
class ArtifactReconcileResult:
    latex: FreshnessState
    pdf: FreshnessState
    latex_writes: int = 0
    builds: int = 0
    pdf_replaces: int = 0
    paths: ArtifactPaths | None = None
    error: str | None = None


def find_existing_artifact_paths(root: Path, problem_id: str) -> ArtifactPaths | None:
    """Discover an existing generated project by provenance comment."""
    base = root / "04_LATEX" / ARTIFACT_KIND
    if not base.is_dir():
        return None
    for tex in base.rglob("*.tex"):
        try:
            text = tex.read_text(encoding="utf-8")
        except OSError:
            continue
        prov = parse_provenance(text)
        if prov.get("problem") == problem_id:
            project_dir = tex.parent
            try:
                rel = project_dir.relative_to(base)
            except ValueError:
                continue
            parts = rel.parts
            domain = parts[0] if len(parts) >= 2 else DEFAULT_DOMAIN
            stem = project_dir.name
            formal_pdf = root / "08_成果输出" / "PDF" / ARTIFACT_KIND / domain / f"{stem}.pdf"
            return ArtifactPaths(
                stem=stem,
                project_dir=project_dir,
                entry_tex=tex,
                formal_pdf=formal_pdf,
                domain=str(domain),
            )
    return None


def resolve_artifact_paths(
    root: Path,
    *,
    problem_id: str,
    title: str,
    domain: str | None = None,
) -> ArtifactPaths:
    domain_name = (domain or DEFAULT_DOMAIN).strip() or DEFAULT_DOMAIN
    stem = artifact_stem(problem_id, title)
    project_dir = root / "04_LATEX" / ARTIFACT_KIND / domain_name / stem
    entry = project_dir / f"{stem}.tex"
    formal_pdf = (
        root / "08_成果输出" / "PDF" / ARTIFACT_KIND / domain_name / f"{stem}.pdf"
    )
    return ArtifactPaths(
        stem=stem,
        project_dir=project_dir,
        entry_tex=entry,
        formal_pdf=formal_pdf,
        domain=domain_name,
    )


def _escape_tex_text(text: str) -> str:
    """Escape a few LaTeX specials outside math; never escape backslash."""
    parts: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("$$", i):
            j = text.find("$$", i + 2)
            if j < 0:
                parts.append(text[i:])
                break
            parts.append(text[i : j + 2])
            i = j + 2
            continue
        if text[i] == "$":
            j = text.find("$", i + 1)
            if j < 0:
                parts.append(text[i:])
                break
            parts.append(text[i : j + 1])
            i = j + 1
            continue
        ch = text[i]
        if ch in "#%&":
            parts.append("\\" + ch)
        elif ch == "~":
            parts.append("\\textasciitilde{}")
        else:
            parts.append(ch)
        i += 1
    return "".join(parts)


def _strip_md_noise(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"^---+\s*$", r"\\par", text, flags=re.MULTILINE)
    return text.strip()


def _md_blocks_to_tex(text: str) -> str:
    cleaned = _strip_md_noise(text)
    cleaned = re.sub(
        r"\$\$(.+?)\$\$",
        lambda m: "\\[\n" + m.group(1).strip() + "\n\\]",
        cleaned,
        flags=re.DOTALL,
    )
    in_display = False
    lines: list[str] = []
    for line in cleaned.split("\n"):
        stripped = line.strip()
        if stripped.startswith("\\["):
            in_display = True
            lines.append(line)
            if "\\]" in line:
                in_display = False
            continue
        if in_display:
            lines.append(line)
            if "\\]" in stripped:
                in_display = False
            continue
        lines.append(_escape_tex_text(line))
    return "\n".join(lines)


def build_problem_latex_body(body: str, problem_id: str, title: str) -> str:
    """Generate LaTeX body sections from Problem Markdown Source."""
    sections: list[str] = []
    sections.append(f"\\chapter{{{_escape_tex_text(title)}}}")
    sections.append("")
    sections.append("\\section{题目}")
    # Extract ## 题目 section if present
    m = re.search(r"^##\s*题目\s*$", body, re.MULTILINE)
    if m:
        start = m.end()
        nxt = re.search(r"^##\s+", body[start:], re.MULTILINE)
        chunk = body[start : start + nxt.start()] if nxt else body[start:]
        sections.append(_md_blocks_to_tex(chunk))
    sections.append("")
    sections.append("\\section{解答}")
    canonical_slots = parse_canonical_slots(body).slots
    emitted: set[str] = set()
    for slot in canonical_slots:
        sections.append(f"\\subsection{{{_escape_tex_text(slot.target)}}}")
        sections.append(_md_blocks_to_tex(slot.content))
        sections.append("")
        emitted.add(slot.target)
    for slot in parse_legacy_part_slots(body, problem_id):
        if slot.target in emitted:
            continue
        sections.append(f"\\subsection{{{_escape_tex_text(slot.target)}}}")
        sections.append(_md_blocks_to_tex(slot.content))
        sections.append("")
        emitted.add(slot.target)
    return "\n".join(sections)


def render_problem_tex(
    *,
    problem_id: str,
    title: str,
    body: str,
    source_sha256: str,
    template_sha256: str,
    latex_body: str | None = None,
) -> str:
    header = render_provenance_header(
        problem_id=problem_id,
        source_sha256=source_sha256,
        template_sha256=template_sha256,
    )
    content = latex_body if latex_body is not None else build_problem_latex_body(body, problem_id, title)
    return (
        header
        + "% !TeX program = xelatex\n"
        + "\\documentclass[\n"
        + "    lang=cn,\n"
        + "    color=blue,\n"
        + "    mode=fancy,\n"
        + "    thmcnt=section,\n"
        + "    scheme=chinese\n"
        + "]{elegantbook}\n\n"
        + "\\usepackage{amsmath}\n"
        + "\\usepackage{amssymb}\n"
        + "\\usepackage{mathtools}\n\n"
        + f"\\title{{{_escape_tex_text(title)}}}\n"
        + f"\\subtitle{{{_escape_tex_text(problem_id)}}}\n"
        + "\\author{}\n"
        + "\\institute{}\n"
        + "\\date{\\today}\n"
        + "\\version{1.0}\n\n"
        + "\\begin{document}\n"
        + "\\maketitle\n"
        + "\\mainmatter\n\n"
        + content
        + "\n\n\\end{document}\n"
    )


def materialize_problem_latex(
    root: Path | str,
    *,
    problem_id: str,
    artifact_domain: str | None = None,
    latex_body: str | None = None,
) -> MaterializeResult:
    project_root = Path(root).resolve()
    path = find_problem_file(project_root, problem_id)
    if path is None:
        return MaterializeResult(written=False, paths=None, error="problem not found")

    text = path.read_text(encoding="utf-8")
    raw_yaml, body, _ = extract_front_matter(text)
    data, issues = parse_yaml_mapping(raw_yaml) if raw_yaml else (None, [])
    if issues or not data:
        return MaterializeResult(written=False, paths=None, error="problem YAML invalid")

    title = str(data.get("title") or problem_id)
    existing = find_existing_artifact_paths(project_root, problem_id)
    if existing is not None and artifact_domain in {None, existing.domain}:
        paths = existing
    else:
        paths = resolve_artifact_paths(
            project_root,
            problem_id=problem_id,
            title=title,
            domain=artifact_domain,
        )
    if not pinned_vendor_cls_exists(project_root):
        return MaterializeResult(
            written=False,
            paths=paths,
            error=TEMPLATE_DEPENDENCY_MISSING,
        )

    src_hash = problem_source_sha256(path)
    tpl_hash = template_sha_for_project(project_root)
    assert tpl_hash is not None
    tex = render_problem_tex(
        problem_id=problem_id,
        title=title,
        body=body,
        source_sha256=src_hash,
        template_sha256=tpl_hash,
        latex_body=latex_body,
    )

    paths.project_dir.mkdir(parents=True, exist_ok=True)
    local_cls_issue = maybe_remove_generated_local_cls(paths.project_dir, project_root)
    if local_cls_issue:
        return MaterializeResult(written=False, paths=paths, error=local_cls_issue)

    if paths.entry_tex.is_file() and paths.entry_tex.read_text(encoding="utf-8") == tex:
        return MaterializeResult(written=False, paths=paths)

    paths.entry_tex.write_text(tex, encoding="utf-8")
    return MaterializeResult(written=True, paths=paths)


def inspect_artifact(
    root: Path | str,
    *,
    problem_id: str,
    artifact_domain: str | None = None,
) -> ArtifactInspect:
    project_root = Path(root).resolve()
    completion = inspect_problem_completion(project_root, problem_id)
    if not completion.complete:
        return ArtifactInspect(
            latex=FreshnessState.NOT_APPLICABLE,
            pdf=FreshnessState.NOT_APPLICABLE,
            error="canonical incomplete",
        )

    path = find_problem_file(project_root, problem_id)
    assert path is not None
    text = path.read_text(encoding="utf-8")
    raw_yaml, _, _ = extract_front_matter(text)
    data, _ = parse_yaml_mapping(raw_yaml) if raw_yaml else (None, [])
    title = str((data or {}).get("title") or problem_id)
    existing = find_existing_artifact_paths(project_root, problem_id)
    if existing is not None and artifact_domain in {None, existing.domain}:
        paths = existing
    else:
        paths = resolve_artifact_paths(
            project_root,
            problem_id=problem_id,
            title=title,
            domain=artifact_domain,
        )
    src_hash = problem_source_sha256(path)
    tpl_hash = template_sha_for_project(project_root)
    if tpl_hash is None:
        return ArtifactInspect(
            latex=FreshnessState.FAILED,
            pdf=FreshnessState.FAILED,
            paths=paths,
            source_sha256=src_hash,
            template_sha256=None,
            error=TEMPLATE_DEPENDENCY_MISSING,
        )

    if not paths.entry_tex.is_file():
        return ArtifactInspect(
            latex=FreshnessState.MISSING,
            pdf=FreshnessState.MISSING,
            paths=paths,
            source_sha256=src_hash,
            template_sha256=tpl_hash,
        )

    prov = parse_provenance(paths.entry_tex.read_text(encoding="utf-8"))
    latex_current = (
        prov.get("source_sha256") == src_hash
        and prov.get("template_sha256") == tpl_hash
        and prov.get("problem") == problem_id
        and prov.get("generator_version") == GENERATOR_VERSION
    )
    latex_state = FreshnessState.CURRENT if latex_current else FreshnessState.STALE

    if not paths.formal_pdf.is_file() or paths.formal_pdf.stat().st_size == 0:
        pdf_state = FreshnessState.MISSING
    elif latex_state != FreshnessState.CURRENT:
        pdf_state = FreshnessState.STALE
    elif paths.entry_tex.stat().st_mtime_ns > paths.formal_pdf.stat().st_mtime_ns:
        pdf_state = FreshnessState.STALE
    else:
        pdf_state = FreshnessState.CURRENT

    return ArtifactInspect(
        latex=latex_state,
        pdf=pdf_state,
        paths=paths,
        source_sha256=src_hash,
        template_sha256=tpl_hash,
    )


def reconcile_artifact(
    root: Path | str,
    *,
    problem_id: str,
    artifact_domain: str | None = None,
    latex_body: str | None = None,
    auto_artifact: bool = True,
) -> ArtifactReconcileResult:
    project_root = Path(root).resolve()
    if not auto_artifact:
        return ArtifactReconcileResult(
            latex=FreshnessState.SKIPPED,
            pdf=FreshnessState.SKIPPED,
        )

    inspect = inspect_artifact(project_root, problem_id=problem_id, artifact_domain=artifact_domain)
    if inspect.latex == FreshnessState.FAILED and inspect.error == TEMPLATE_DEPENDENCY_MISSING:
        return ArtifactReconcileResult(
            latex=FreshnessState.FAILED,
            pdf=FreshnessState.FAILED,
            paths=inspect.paths,
            error=TEMPLATE_DEPENDENCY_MISSING,
        )
    if inspect.latex == FreshnessState.NOT_APPLICABLE:
        return ArtifactReconcileResult(
            latex=FreshnessState.NOT_APPLICABLE,
            pdf=FreshnessState.NOT_APPLICABLE,
            error=inspect.error,
        )

    latex_writes = 0
    builds = 0
    pdf_replaces = 0
    paths = inspect.paths

    need_materialize = inspect.latex in {FreshnessState.MISSING, FreshnessState.STALE}
    if need_materialize:
        mat = materialize_problem_latex(
            project_root,
            problem_id=problem_id,
            artifact_domain=artifact_domain,
            latex_body=latex_body,
        )
        if mat.error:
            return ArtifactReconcileResult(
                latex=FreshnessState.FAILED,
                pdf=FreshnessState.FAILED,
                paths=mat.paths,
                error=mat.error,
            )
        if mat.written:
            latex_writes = 1
        paths = mat.paths

    assert paths is not None
    inspect2 = inspect_artifact(project_root, problem_id=problem_id, artifact_domain=artifact_domain)
    need_build = inspect2.pdf in {FreshnessState.MISSING, FreshnessState.STALE} or need_materialize

    if not need_build and inspect2.latex == FreshnessState.CURRENT and inspect2.pdf == FreshnessState.CURRENT:
        return ArtifactReconcileResult(
            latex=FreshnessState.CURRENT,
            pdf=FreshnessState.CURRENT,
            latex_writes=latex_writes,
            builds=0,
            pdf_replaces=0,
            paths=paths,
        )

    # Preserve old PDF path for failure recovery
    old_pdf_bytes = paths.formal_pdf.read_bytes() if paths.formal_pdf.is_file() else None

    try:
        build = build_latex_project(paths.project_dir, repo_root=project_root)
        builds = 1
        published = (
            build.compile_result.success
            and build.publish_result is not None
            and build.publish_result.status
            in {PublishStatus.CREATED, PublishStatus.UPDATED, PublishStatus.UP_TO_DATE}
        )
        if not published:
            if old_pdf_bytes is not None and (
                not paths.formal_pdf.is_file() or paths.formal_pdf.read_bytes() != old_pdf_bytes
            ):
                # publisher should preserve, but ensure
                paths.formal_pdf.parent.mkdir(parents=True, exist_ok=True)
                paths.formal_pdf.write_bytes(old_pdf_bytes)
            return ArtifactReconcileResult(
                latex=FreshnessState.CURRENT if paths.entry_tex.is_file() else FreshnessState.FAILED,
                pdf=FreshnessState.FAILED,
                latex_writes=latex_writes,
                builds=builds,
                pdf_replaces=0,
                paths=paths,
                error="LaTeX build/publish failed",
            )
        if build.publish_result and build.publish_result.writes:
            pdf_replaces = build.publish_result.writes
        return ArtifactReconcileResult(
            latex=FreshnessState.CURRENT,
            pdf=FreshnessState.CURRENT,
            latex_writes=latex_writes,
            builds=builds,
            pdf_replaces=pdf_replaces,
            paths=paths,
        )
    except Exception as exc:
        if old_pdf_bytes is not None:
            paths.formal_pdf.parent.mkdir(parents=True, exist_ok=True)
            paths.formal_pdf.write_bytes(old_pdf_bytes)
        return ArtifactReconcileResult(
            latex=FreshnessState.FAILED,
            pdf=FreshnessState.FAILED,
            latex_writes=latex_writes,
            builds=builds,
            pdf_replaces=0,
            paths=paths,
            error=str(exc),
        )
