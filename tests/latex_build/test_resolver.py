"""Tests for LaTeX project resolver."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.latex_build.resolver import LatexBuildError, resolve_latex_project

from .conftest import write_latex_project


def test_legendre_resolves_topic_entrypoint(repo_root: Path) -> None:
    project = write_latex_project(repo_root, "专题讲义/数学变换/勒让德变换")
    resolved = resolve_latex_project(project, repo_root=repo_root)
    assert resolved.main_tex.name == "勒让德变换.tex"
    assert resolved.formal_pdf == (
        repo_root / "08_成果输出/PDF/专题讲义/数学变换/勒让德变换.pdf"
    ).resolve()


def test_svd_resolves_topic_entrypoint(repo_root: Path) -> None:
    project = write_latex_project(repo_root, "专题讲义/线性代数/奇异值分解")
    resolved = resolve_latex_project(project, repo_root=repo_root)
    assert resolved.main_tex.name == "奇异值分解.tex"
    assert resolved.formal_pdf.name == "奇异值分解.pdf"


def test_main_tex_only_without_topic_entrypoint_fails(repo_root: Path) -> None:
    project = write_latex_project(
        repo_root,
        "专题讲义/数学变换/勒让德变换",
        with_entry=False,
        legacy_main_only=True,
    )
    with pytest.raises(LatexBuildError, match="PROJECT_ENTRYPOINT_MISSING"):
        resolve_latex_project(project, repo_root=repo_root)


def test_missing_entrypoint(repo_root: Path) -> None:
    project = write_latex_project(repo_root, "专题讲义/x", with_entry=False)
    with pytest.raises(LatexBuildError, match="PROJECT_ENTRYPOINT_MISSING"):
        resolve_latex_project(project, repo_root=repo_root)


def test_outside_latex_root(repo_root: Path) -> None:
    outside = repo_root / "08_成果输出" / "x"
    outside.mkdir(parents=True)
    (outside / "x.tex").write_text("x", encoding="utf-8")
    with pytest.raises(LatexBuildError, match="PROJECT_OUTSIDE_LATEX_ROOT"):
        resolve_latex_project(outside, repo_root=repo_root)


def test_template_excluded(repo_root: Path) -> None:
    project = repo_root / "04_LATEX" / "模板" / "数学讲义模板_v1"
    project.mkdir(parents=True)
    (project / "main.tex").write_text("template", encoding="utf-8")
    with pytest.raises(LatexBuildError, match="PROJECT_EXCLUDED"):
        resolve_latex_project(project, repo_root=repo_root)


def test_relative_project_string(repo_root: Path) -> None:
    write_latex_project(repo_root, "专题讲义/a/b")
    resolved = resolve_latex_project("04_LATEX/专题讲义/a/b", repo_root=repo_root)
    assert resolved.main_tex.name == "b.tex"
    assert resolved.formal_pdf.name == "b.pdf"
