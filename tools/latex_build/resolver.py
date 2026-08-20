"""Resolve LaTeX project paths and formal artifact destinations."""

from __future__ import annotations

from pathlib import Path

from .constants import EXCLUDED_LATEX_PREFIXES, FORMAL_PDF_PREFIX, LATEX_ROOT, OUTPUT_ROOT
from .models import ResolvedLatexProject


class LatexBuildError(Exception):
    """Raised when project resolution fails."""


def _is_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _topic_entrypoint(project_dir: Path) -> Path:
    return project_dir / f"{project_dir.name}.tex"


def resolve_latex_project(
    project: Path | str,
    *,
    repo_root: Path,
    output_override: Path | None = None,
) -> ResolvedLatexProject:
    repo_root = repo_root.resolve()
    latex_root = (repo_root / LATEX_ROOT).resolve()
    output_root = (repo_root / OUTPUT_ROOT).resolve()

    project_dir = Path(project)
    if not project_dir.is_absolute():
        project_dir = (repo_root / project_dir).resolve()
    else:
        project_dir = project_dir.resolve()

    if not _is_under(project_dir, latex_root):
        raise LatexBuildError("PROJECT_OUTSIDE_LATEX_ROOT")

    rel = project_dir.relative_to(latex_root)
    rel_posix = rel.as_posix()
    for prefix in EXCLUDED_LATEX_PREFIXES:
        if rel_posix == prefix.rstrip("/") or rel_posix.startswith(prefix):
            raise LatexBuildError("PROJECT_EXCLUDED")

    if not project_dir.is_dir():
        raise LatexBuildError("PROJECT_NOT_FOUND")

    entry_tex = _topic_entrypoint(project_dir)
    if not entry_tex.is_file():
        raise LatexBuildError("PROJECT_ENTRYPOINT_MISSING")

    if output_override is not None:
        formal_pdf = Path(output_override)
        if not formal_pdf.is_absolute():
            formal_pdf = (repo_root / formal_pdf).resolve()
        else:
            formal_pdf = formal_pdf.resolve()
        if not _is_under(formal_pdf.parent, output_root):
            raise LatexBuildError("OUTPUT_OUTSIDE_FORMAL_ROOT")
    else:
        formal_pdf = (
            output_root / FORMAL_PDF_PREFIX / rel.parent / f"{rel.name}.pdf"
        ).resolve()
        if not _is_under(formal_pdf, output_root):
            raise LatexBuildError("OUTPUT_OUTSIDE_FORMAL_ROOT")

    return ResolvedLatexProject(
        project_dir=project_dir,
        relative_project_path=rel,
        main_tex=entry_tex,
        formal_pdf=formal_pdf,
    )
