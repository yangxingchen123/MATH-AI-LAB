"""Tests for LaTeX builder with fake command runner."""

from __future__ import annotations

import subprocess
from pathlib import Path

from tools.latex_build.builder import compile_project
from tools.latex_build.models import ResolvedLatexProject


def _project(repo: Path) -> ResolvedLatexProject:
    project_dir = repo / "04_LATEX" / "p"
    project_dir.mkdir(parents=True, exist_ok=True)
    entry = project_dir / "p.tex"
    entry.write_text("\\documentclass{article}\\begin{document}x\\end{document}", encoding="utf-8")
    return ResolvedLatexProject(
        project_dir=project_dir,
        relative_project_path=Path("p"),
        main_tex=entry,
        formal_pdf=repo / "08_成果输出/PDF/p.pdf",
    )


def test_fake_runner_success(repo_root: Path, tmp_path: Path) -> None:
    def runner(cmd, *, cwd):
        outdir = Path(cmd[4].split("=", 1)[1])
        outdir.mkdir(parents=True, exist_ok=True)
        pdf_name = Path(cmd[-1]).with_suffix(".pdf").name
        (outdir / pdf_name).write_bytes(b"PDF")
        (outdir / Path(cmd[-1]).with_suffix(".log").name).write_text(
            f"Output written on {pdf_name}", encoding="utf-8"
        )
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    result = compile_project(_project(repo_root), command_runner=runner, compiler_executable="xelatex")
    assert result.success
    assert result.built_pdf is not None
    assert result.built_pdf.read_bytes() == b"PDF"


def test_fake_runner_failure(repo_root: Path) -> None:
    def runner(cmd, *, cwd):
        outdir = Path(cmd[4].split("=", 1)[1])
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / Path(cmd[-1]).with_suffix(".log").name).write_text(
            "! Undefined control sequence", encoding="utf-8"
        )
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="")

    result = compile_project(_project(repo_root), command_runner=runner, compiler_executable="xelatex")
    assert not result.success
    assert result.built_pdf is None


def test_stale_source_pdf_not_used(repo_root: Path) -> None:
    project = _project(repo_root)
    stale = project.project_dir / "p.pdf"
    stale.write_bytes(b"STALE")

    def runner(cmd, *, cwd):
        outdir = Path(cmd[4].split("=", 1)[1])
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / Path(cmd[-1]).with_suffix(".log").name).write_text(
            "! Emergency stop", encoding="utf-8"
        )
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="")

    result = compile_project(project, command_runner=runner, compiler_executable="xelatex")
    assert result.built_pdf is None
    assert stale.read_bytes() == b"STALE"


def test_toolchain_missing(repo_root: Path) -> None:
    result = compile_project(_project(repo_root), compiler_executable="", command_runner=lambda *a, **k: None)
    assert not result.success
    assert any(i.code == "TOOLCHAIN_MISSING" for i in result.issues)
