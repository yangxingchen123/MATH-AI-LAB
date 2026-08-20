"""Tests for compile log inspector."""

from __future__ import annotations

from pathlib import Path

from tools.latex_build.inspector import inspect_compile
from tools.latex_build.models import CompileResult, IssueSeverity


def _compile(log: str, *, code: int = 0, pdf: Path | None = None) -> CompileResult:
    return CompileResult(
        success=code == 0 and pdf is not None,
        return_code=code,
        compiler="xelatex",
        compiler_runs=1,
        stdout="",
        stderr="",
        log_text=log,
        built_pdf=pdf,
    )


def test_compiler_nonzero_blocking(tmp_path: Path) -> None:
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(b"pdf")
    result = inspect_compile(_compile("", code=1, pdf=pdf))
    assert any(i.code == "COMPILER_NONZERO_EXIT" for i in result.blocking_errors)


def test_missing_pdf_blocking() -> None:
    result = inspect_compile(_compile("ok", pdf=None))
    assert any(i.code == "OUTPUT_PDF_MISSING" for i in result.blocking_errors)


def test_undefined_control_sequence_blocking() -> None:
    log = "! Undefined control sequence.\n! Emergency stop."
    result = inspect_compile(_compile(log, pdf=Path("x.pdf")))
    assert not result.publish_allowed


def test_undefined_references_blocking(tmp_path: Path) -> None:
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(b"x")
    log = "LaTeX Warning: There were undefined references."
    result = inspect_compile(_compile(log, pdf=pdf))
    assert any(i.code == "UNDEFINED_REFERENCES" for i in result.blocking_errors)


def test_undefined_citations_blocking(tmp_path: Path) -> None:
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(b"x")
    log = "LaTeX Warning: There were undefined citations."
    result = inspect_compile(_compile(log, pdf=pdf))
    assert any(i.code == "UNDEFINED_CITATIONS" for i in result.blocking_errors)


def test_overfull_warning_only(tmp_path: Path) -> None:
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(b"x")
    log = "Overfull \\hbox (12.3pt too wide)"
    result = inspect_compile(_compile(log, pdf=pdf))
    assert result.publish_allowed
    assert any(i.code == "OVERFULL_BOX" for i in result.warnings)


def test_clean_log_passes(tmp_path: Path) -> None:
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(b"x")
    result = inspect_compile(_compile("Output written on main.pdf", pdf=pdf))
    assert result.publish_allowed
    assert not result.blocking_errors
