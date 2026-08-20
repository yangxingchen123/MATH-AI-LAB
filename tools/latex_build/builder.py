"""Compile LaTeX projects with isolated build output."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Protocol

from .constants import MAX_XELATEX_PASSES, RERUN_SIGNALS, XELATEX_ARGS
from .models import BuildIssue, CompileResult, IssueSeverity, ResolvedLatexProject
from .vendor import pinned_vendor_cls_exists, pinned_vendor_dir, xelatex_env_with_vendor


class CommandRunner(Protocol):
    def __call__(
        self,
        cmd: list[str],
        *,
        cwd: Path,
    ) -> subprocess.CompletedProcess[str]: ...


def default_command_runner(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    kwargs: dict = dict(
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if env is not None:
        kwargs["env"] = env
    return subprocess.run(cmd, **kwargs)


def _needs_rerun(log_text: str) -> bool:
    return any(signal in log_text for signal in RERUN_SIGNALS)


def compile_project(
    project: ResolvedLatexProject,
    *,
    command_runner: CommandRunner | None = None,
    compiler_executable: str | None = None,
    repo_root: Path | None = None,
) -> CompileResult:
    if command_runner is None:
        if repo_root is None or not pinned_vendor_cls_exists(repo_root):
            return CompileResult(
                success=False,
                return_code=2,
                compiler="xelatex",
                compiler_runs=0,
                stdout="",
                stderr="",
                log_text="",
                built_pdf=None,
                issues=(
                    BuildIssue(
                        severity=IssueSeverity.ERROR,
                        code="TEMPLATE_DEPENDENCY_MISSING",
                        message="pinned ElegantBook vendor class is missing",
                    ),
                ),
            )
        vendor_env = xelatex_env_with_vendor(pinned_vendor_dir(repo_root))

        def runner(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
            return default_command_runner(cmd, cwd=cwd, env=vendor_env)

    else:
        runner = command_runner
    if compiler_executable is not None:
        compiler = compiler_executable
    else:
        compiler = shutil.which("xelatex")
    if not compiler:
        return CompileResult(
            success=False,
            return_code=127,
            compiler="xelatex",
            compiler_runs=0,
            stdout="",
            stderr="",
            log_text="",
            built_pdf=None,
            issues=(
                BuildIssue(
                    severity=IssueSeverity.ERROR,
                    code="TOOLCHAIN_MISSING",
                    message="xelatex executable not found",
                ),
            ),
        )

    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    log_text = ""
    return_code = 0
    runs = 0
    exported_pdf: Path | None = None

    with tempfile.TemporaryDirectory(prefix="latex_build_") as tmp:
        build_dir = Path(tmp)
        cmd_base = [compiler, *XELATEX_ARGS, f"-output-directory={build_dir.as_posix()}", project.main_tex.name]

        for _ in range(MAX_XELATEX_PASSES):
            runs += 1
            proc = runner(cmd_base, cwd=project.project_dir)
            stdout_parts.append(proc.stdout or "")
            stderr_parts.append(proc.stderr or "")
            return_code = proc.returncode
            log_path = build_dir / project.main_tex.with_suffix(".log").name
            if log_path.is_file():
                log_text = log_path.read_text(encoding="utf-8", errors="replace")
            else:
                log_text = (proc.stdout or "") + (proc.stderr or "")

            if return_code != 0:
                break
            if not _needs_rerun(log_text):
                break

        candidate = build_dir / f"{project.main_tex.stem}.pdf"
        if candidate.is_file() and candidate.stat().st_size > 0:
            handle = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="latex_built_")
            handle.close()
            exported_pdf = Path(handle.name)
            shutil.copy2(candidate, exported_pdf)

    success = return_code == 0 and exported_pdf is not None and exported_pdf.is_file()
    return CompileResult(
        success=success,
        return_code=return_code,
        compiler="xelatex",
        compiler_runs=runs,
        stdout="".join(stdout_parts),
        stderr="".join(stderr_parts),
        log_text=log_text,
        built_pdf=exported_pdf,
    )
