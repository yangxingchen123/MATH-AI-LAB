"""Orchestration for LaTeX build check/build."""

from __future__ import annotations

from pathlib import Path

from tools.knowledge_validator.discovery import resolve_project_root

from .builder import CommandRunner, compile_project
from .inspector import inspect_compile
from .models import LatexBuildResult, PublishStatus
from .publisher import publish_formal_pdf
from .resolver import LatexBuildError, resolve_latex_project


def check_latex_project(
    project: Path | str,
    *,
    repo_root: Path | None = None,
    command_runner: CommandRunner | None = None,
) -> LatexBuildResult:
    return _run(project, repo_root=repo_root, publish=False, command_runner=command_runner)


def build_latex_project(
    project: Path | str,
    *,
    repo_root: Path | None = None,
    command_runner: CommandRunner | None = None,
) -> LatexBuildResult:
    return _run(project, repo_root=repo_root, publish=True, command_runner=command_runner)


def _run(
    project: Path | str,
    *,
    repo_root: Path | None,
    publish: bool,
    command_runner: CommandRunner | None,
) -> LatexBuildResult:
    root = resolve_project_root(repo_root)
    resolved = resolve_latex_project(project, repo_root=root)
    compile_result = compile_project(
        resolved, command_runner=command_runner, repo_root=root
    )
    inspection = inspect_compile(compile_result)

    publish_result = None
    if publish:
        built = compile_result.built_pdf
        if built is None:
            from .models import PublishResult

            publish_result = PublishResult(
                status=PublishStatus.BLOCKED,
                formal_pdf=resolved.formal_pdf,
                writes=0,
                message="No built PDF to publish",
            )
        else:
            try:
                publish_result = publish_formal_pdf(
                    built_pdf=built,
                    formal_pdf=resolved.formal_pdf,
                    publish_allowed=inspection.publish_allowed,
                )
            finally:
                if built.is_file():
                    built.unlink(missing_ok=True)
    elif compile_result.built_pdf is not None and compile_result.built_pdf.is_file():
        compile_result.built_pdf.unlink(missing_ok=True)

    return LatexBuildResult(
        project=resolved,
        compile_result=compile_result,
        inspection_result=inspection,
        publish_result=publish_result,
    )


def resolve_or_raise(project: Path | str, *, repo_root: Path | None = None):
    root = resolve_project_root(repo_root)
    try:
        return resolve_latex_project(project, repo_root=root)
    except LatexBuildError as exc:
        raise exc
