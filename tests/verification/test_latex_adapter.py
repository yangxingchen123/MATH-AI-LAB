"""LaTeX smoke adapter tests using fake P9 results. No TeX required."""

from __future__ import annotations

from pathlib import Path

from tools.latex_build.models import (
    BuildIssue,
    CompileResult,
    InspectionResult,
    IssueSeverity,
    LatexBuildResult,
    ResolvedLatexProject,
)
from tools.latex_build.resolver import LatexBuildError
from tools.verification.checks import run_latex_smoke
from tools.verification.models import FailureCategory, VerificationStatus


def _result(*, success: bool, blocking=(), warnings=(), compile_issues=()) -> LatexBuildResult:
    project = ResolvedLatexProject(
        project_dir=Path("/fake/proj"),
        relative_project_path=Path("专题讲义/x"),
        main_tex=Path("/fake/proj/x.tex"),
        formal_pdf=Path("/fake/out.pdf"),
    )
    compile_result = CompileResult(
        success=success,
        return_code=0 if success else 1,
        compiler="xelatex",
        compiler_runs=1 if success else 0,
        stdout="",
        stderr="",
        log_text="",
        built_pdf=Path("/tmp/x.pdf") if success else None,
        issues=tuple(compile_issues),
    )
    inspection = InspectionResult(blocking_errors=tuple(blocking), warnings=tuple(warnings))
    return LatexBuildResult(
        project=project,
        compile_result=compile_result,
        inspection_result=inspection,
        publish_result=None,
    )


def test_latex_adapter_pass(tmp_path: Path) -> None:
    check = run_latex_smoke(tmp_path, "proj", check_fn=lambda *_a, **_k: _result(success=True))
    assert check.status == VerificationStatus.PASS
    assert check.category is None


def test_latex_adapter_warnings(tmp_path: Path) -> None:
    warning = BuildIssue(IssueSeverity.WARNING, "UNDERFULL_BOX", "underfull")
    check = run_latex_smoke(
        tmp_path,
        "proj",
        check_fn=lambda *_a, **_k: _result(success=True, warnings=(warning,)),
    )
    assert check.status == VerificationStatus.PASS_WITH_WARNINGS


def test_latex_adapter_fail(tmp_path: Path) -> None:
    blocking = BuildIssue(IssueSeverity.ERROR, "LATEX_FATAL_ERROR", "boom")
    check = run_latex_smoke(
        tmp_path,
        "proj",
        check_fn=lambda *_a, **_k: _result(success=False, blocking=(blocking,)),
    )
    assert check.status == VerificationStatus.FAIL
    assert check.category == FailureCategory.LATEX_FAILURE


def test_latex_adapter_toolchain_missing(tmp_path: Path) -> None:
    issue = BuildIssue(IssueSeverity.ERROR, "TOOLCHAIN_MISSING", "xelatex executable not found")
    blocking = BuildIssue(IssueSeverity.ERROR, "COMPILER_NONZERO_EXIT", "127")
    check = run_latex_smoke(
        tmp_path,
        "proj",
        check_fn=lambda *_a, **_k: _result(
            success=False,
            blocking=(blocking, issue),
            compile_issues=(issue,),
        ),
    )
    assert check.status == VerificationStatus.BLOCKED
    assert check.category == FailureCategory.TOOLCHAIN_MISSING


def test_latex_adapter_does_not_set_publish(tmp_path: Path) -> None:
    seen = {"publish": None}

    def checker(project, repo_root=None):
        result = _result(success=True)
        seen["publish"] = result.publish_result
        return result

    check = run_latex_smoke(tmp_path, "proj", check_fn=checker)
    assert seen["publish"] is None
    assert check.status == VerificationStatus.PASS


def test_latex_resolver_error(tmp_path: Path) -> None:
    def checker(project, repo_root=None):
        raise LatexBuildError("PROJECT_ENTRYPOINT_MISSING")

    check = run_latex_smoke(tmp_path, "proj", check_fn=checker)
    assert check.status == VerificationStatus.FAIL
    assert check.category == FailureCategory.LATEX_FAILURE
