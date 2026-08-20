"""Tests for LaTeX build service orchestration."""

from __future__ import annotations

import subprocess
from pathlib import Path

from tools.latex_build.models import PublishStatus
from tools.latex_build.service import build_latex_project, check_latex_project

from .conftest import write_latex_project


def _runner_factory(outdir_holder: dict):
    def runner(cmd, *, cwd):
        outdir = Path(cmd[4].split("=", 1)[1])
        outdir.mkdir(parents=True, exist_ok=True)
        outdir_holder["dir"] = outdir
        pdf_name = Path(cmd[-1]).with_suffix(".pdf").name
        (outdir / pdf_name).write_bytes(b"PDF")
        (outdir / Path(cmd[-1]).with_suffix(".log").name).write_text(
            f"Output written on {pdf_name}", encoding="utf-8"
        )
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    return runner


def test_check_does_not_publish(repo_root: Path) -> None:
    write_latex_project(repo_root, "专题讲义/x")
    formal = repo_root / "08_成果输出/PDF/专题讲义/x.pdf"
    result = check_latex_project(
        "04_LATEX/专题讲义/x",
        repo_root=repo_root,
        command_runner=_runner_factory({}),
    )
    assert result.publish_result is None
    assert not formal.exists()


def test_build_publishes(repo_root: Path) -> None:
    write_latex_project(repo_root, "专题讲义/x")
    formal = repo_root / "08_成果输出/PDF/专题讲义/x.pdf"
    result = build_latex_project(
        "04_LATEX/专题讲义/x",
        repo_root=repo_root,
        command_runner=_runner_factory({}),
    )
    assert result.publish_result is not None
    assert result.publish_result.status in {PublishStatus.CREATED, PublishStatus.UPDATED}
    assert formal.is_file()


def test_build_repeat_up_to_date(repo_root: Path) -> None:
    write_latex_project(repo_root, "专题讲义/x")
    runner = _runner_factory({})
    build_latex_project("04_LATEX/专题讲义/x", repo_root=repo_root, command_runner=runner)
    second = build_latex_project("04_LATEX/专题讲义/x", repo_root=repo_root, command_runner=runner)
    assert second.publish_result is not None
    assert second.publish_result.status == PublishStatus.UP_TO_DATE
    assert second.publish_result.writes == 0


def test_build_blocking_keeps_old_formal(repo_root: Path) -> None:
    write_latex_project(repo_root, "专题讲义/x")
    formal = repo_root / "08_成果输出/PDF/专题讲义/x.pdf"
    formal.parent.mkdir(parents=True, exist_ok=True)
    formal.write_bytes(b"GOOD")

    def failing_runner(cmd, *, cwd):
        outdir = Path(cmd[4].split("=", 1)[1])
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / Path(cmd[-1]).with_suffix(".log").name).write_text(
            "! Emergency stop", encoding="utf-8"
        )
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="")

    result = build_latex_project(
        "04_LATEX/专题讲义/x",
        repo_root=repo_root,
        command_runner=failing_runner,
    )
    assert result.publish_result is not None
    assert result.publish_result.status == PublishStatus.BLOCKED
    assert formal.read_bytes() == b"GOOD"
