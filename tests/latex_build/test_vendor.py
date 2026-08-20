"""Pinned ElegantBook vendor resolution tests."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.latex_build.conftest import install_pinned_vendor, write_latex_project
from tools.latex_build.builder import compile_project
from tools.latex_build.constants import PINNED_ELEGANTBOOK_PROVIDES_CLASS, PINNED_ELEGANTBOOK_TAG
from tools.latex_build.models import ResolvedLatexProject
from tools.latex_build.vendor import (
    parse_provides_class,
    pinned_vendor_cls,
    pinned_vendor_cls_exists,
    pinned_vendor_dir,
    texinputs_with_vendor,
    xelatex_env_with_vendor,
)

PRODUCTION_ROOT = Path(r"C:\MATH-AI-LAB")


def test_vendor_discovery(repo_root: Path) -> None:
    install_pinned_vendor(repo_root)
    assert pinned_vendor_cls_exists(repo_root)
    cls = pinned_vendor_cls(repo_root)
    assert cls.is_file()
    assert cls.stat().st_size > 0


def test_vendor_missing_fails_fast(repo_root: Path) -> None:
    project_dir = write_latex_project(repo_root, "p")
    project = ResolvedLatexProject(
        project_dir=project_dir,
        relative_project_path=Path("p"),
        main_tex=project_dir / "p.tex",
        formal_pdf=repo_root / "08_成果输出/PDF/p.pdf",
    )
    result = compile_project(project, repo_root=repo_root)
    assert not result.success
    assert any(i.code == "TEMPLATE_DEPENDENCY_MISSING" for i in result.issues)


def test_vendor_class_provides_class_from_pin(repo_root: Path) -> None:
    install_pinned_vendor(repo_root)
    text = pinned_vendor_cls(repo_root).read_text(encoding="utf-8")
    provides = parse_provides_class(text)
    assert provides is not None
    assert PINNED_ELEGANTBOOK_TAG == "v4.7"
    assert "ElegantBook" in provides
    # Official tag v4.7 archive still labels ProvidesClass as v4.6.
    assert PINNED_ELEGANTBOOK_PROVIDES_CLASS in text


def test_texinputs_contains_pinned_vendor(repo_root: Path) -> None:
    vendor = install_pinned_vendor(repo_root)
    value = texinputs_with_vendor(vendor, "")
    assert str(vendor.resolve()) in value
    assert value.endswith(os.pathsep)
    env = xelatex_env_with_vendor(vendor, base_env={"PATH": "/bin"})
    assert str(vendor.resolve()) in env["TEXINPUTS"]
    assert "PATH" in env


def test_default_runner_injects_texinputs(repo_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vendor = install_pinned_vendor(repo_root)
    project_dir = write_latex_project(repo_root, "p")
    project = ResolvedLatexProject(
        project_dir=project_dir,
        relative_project_path=Path("p"),
        main_tex=project_dir / "p.tex",
        formal_pdf=repo_root / "08_成果输出/PDF/p.pdf",
    )
    captured: dict = {}

    def fake(cmd, *, cwd, env=None):
        captured["env"] = env
        outdir = Path(cmd[4].split("=", 1)[1])
        outdir.mkdir(parents=True, exist_ok=True)
        pdf_name = Path(cmd[-1]).with_suffix(".pdf").name
        (outdir / pdf_name).write_bytes(b"PDF")
        (outdir / Path(cmd[-1]).with_suffix(".log").name).write_text(
            f"Output written on {pdf_name}", encoding="utf-8"
        )
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("tools.latex_build.builder.default_command_runner", fake)
    result = compile_project(project, repo_root=repo_root, compiler_executable="xelatex")
    assert result.success
    assert captured["env"] is not None
    assert str(vendor.resolve()) in captured["env"]["TEXINPUTS"]


def test_production_vendor_class_file() -> None:
    assert pinned_vendor_cls_exists(PRODUCTION_ROOT)
    cls = pinned_vendor_cls(PRODUCTION_ROOT)
    text = cls.read_text(encoding="utf-8")
    provides = parse_provides_class(text)
    assert provides == PINNED_ELEGANTBOOK_PROVIDES_CLASS
    assert PINNED_ELEGANTBOOK_TAG == "v4.7"
    assert cls.stat().st_size > 0


def test_kpsewhich_resolves_pinned_vendor_when_available() -> None:
    kpse = shutil.which("kpsewhich")
    if kpse is None:
        pytest.skip("kpsewhich not installed")
    env = xelatex_env_with_vendor(pinned_vendor_dir(PRODUCTION_ROOT))
    proc = subprocess.run(
        [kpse, "elegantbook.cls"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    resolved = Path(proc.stdout.strip())
    assert resolved.is_file()
    assert resolved.resolve() == pinned_vendor_cls(PRODUCTION_ROOT).resolve()

