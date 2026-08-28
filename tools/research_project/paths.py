"""Path safety for production research project writes."""

from __future__ import annotations

from pathlib import Path

from .constants import PROJECTS_DIRNAME, TEMPLATE_DIRNAME
from .models import ResearchProjectOperationKind, ResearchProjectOperationResult

KNOWLEDGE_DIRNAME = "01_知识库"
ATTEMPT_DIRNAME = "11_学习证据"


def resolve_repo_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit).expanduser().resolve()
    from .constants import REPO_ROOT

    return REPO_ROOT


def projects_root(repo_root: Path) -> Path:
    return (Path(repo_root) / PROJECTS_DIRNAME).resolve()


def path_safety_error(project: Path, repo_root: Path) -> str | None:
    root = Path(repo_root).resolve()
    target = Path(project)
    try:
        resolved = target.resolve()
    except OSError as exc:
        return f"cannot resolve project path: {exc}"
    expected_parent = projects_root(root)
    try:
        relative = resolved.relative_to(expected_parent)
    except ValueError:
        return "project path must be under 07_项目/"
    parts = relative.parts
    if not parts:
        return "project path must be a directory under 07_项目/"
    if TEMPLATE_DIRNAME in resolved.parts:
        return "refusing to treat _模板 as a production project"
    if KNOWLEDGE_DIRNAME in resolved.parts or ATTEMPT_DIRNAME in resolved.parts:
        return "project path must not escape into 01_知识库/ or 11_学习证据/"
    return None


def rejected(message: str, project: Path | None = None) -> ResearchProjectOperationResult:
    return ResearchProjectOperationResult(
        kind=ResearchProjectOperationKind.REJECTED,
        message=message,
        project=project,
        touched_paths=(),
    )
