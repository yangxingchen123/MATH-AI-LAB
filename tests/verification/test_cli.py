"""CLI dispatch, exit codes, and verbose reporting tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.verification.cli import run
from tools.verification.models import FailureCategory, VerificationCheckResult, VerificationRunResult, VerificationStatus
from tools.verification.report import exit_code, format_report


def test_exit_pass_zero() -> None:
    run_result = VerificationRunResult(
        profile="core",
        checks=(VerificationCheckResult(name="x", status=VerificationStatus.PASS, layer="SOURCE INTEGRITY"),),
        overall_status=VerificationStatus.PASS,
        duration_seconds=1.0,
    )
    assert exit_code(run_result) == 0


def test_exit_warning_zero() -> None:
    run_result = VerificationRunResult(
        profile="core",
        checks=(
            VerificationCheckResult(
                name="x",
                status=VerificationStatus.PASS_WITH_WARNINGS,
                layer="SOURCE INTEGRITY",
            ),
        ),
        overall_status=VerificationStatus.PASS_WITH_WARNINGS,
        duration_seconds=1.0,
    )
    assert exit_code(run_result) == 0


def test_exit_fail_nonzero() -> None:
    run_result = VerificationRunResult(
        profile="core",
        checks=(VerificationCheckResult(name="x", status=VerificationStatus.FAIL, layer="SOURCE INTEGRITY"),),
        overall_status=VerificationStatus.FAIL,
        duration_seconds=1.0,
    )
    assert exit_code(run_result) == 1


def test_exit_blocked_nonzero() -> None:
    run_result = VerificationRunResult(
        profile="core",
        checks=(VerificationCheckResult(name="x", status=VerificationStatus.BLOCKED, layer="DERIVED INTEGRITY"),),
        overall_status=VerificationStatus.BLOCKED,
        duration_seconds=1.0,
    )
    assert exit_code(run_result) == 1


def test_report_failure_fields() -> None:
    run_result = VerificationRunResult(
        profile="core",
        checks=(
            VerificationCheckResult(
                name="Workspace Indexer",
                status=VerificationStatus.FAIL,
                category=FailureCategory.GENERATED_STALE,
                summary="Generated files are stale.",
                suggested_action="python -m tools.workspace_indexer sync",
                layer="DERIVED INTEGRITY",
            ),
        ),
        overall_status=VerificationStatus.FAIL,
        duration_seconds=1.23,
    )
    text = format_report(run_result)
    assert "Workspace Indexer" in text
    assert "GENERATED_STALE" in text
    assert "python -m tools.workspace_indexer sync" in text
    assert "Overall" in text


def test_verbose_includes_environment() -> None:
    run_result = VerificationRunResult(
        profile="core",
        checks=(VerificationCheckResult(name="pytest", status=VerificationStatus.PASS, layer="SOFTWARE INTEGRITY"),),
        overall_status=VerificationStatus.PASS,
        duration_seconds=0.5,
        environment={"Python": "3.13.0", "Platform": "win32"},
    )
    text = format_report(run_result, verbose=True)
    assert "Environment" in text
    assert "Python" in text


def test_cli_core_dispatch(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "元数据规范.md").write_text("x", encoding="utf-8")
    (tmp_path / "01_知识库").mkdir()
    captured = {}

    def fake_run(profile, *, root=None, latex_project=None, verbose=False, hooks=None):
        captured["profile"] = profile
        captured["verbose"] = verbose
        captured["latex_project"] = latex_project
        return VerificationRunResult(
            profile=profile,
            checks=(VerificationCheckResult(name="pytest", status=VerificationStatus.PASS, layer="SOFTWARE INTEGRITY"),),
            overall_status=VerificationStatus.PASS,
            duration_seconds=0.1,
            environment={"Python": "3.13"} if verbose else None,
        )

    monkeypatch.setattr("tools.verification.cli.run_verification", fake_run)
    code = run(["--root", str(tmp_path), "core"])
    assert code == 0
    assert captured["profile"] == "core"
    assert captured["latex_project"] is None


def test_cli_verbose_flag(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "元数据规范.md").write_text("x", encoding="utf-8")
    (tmp_path / "01_知识库").mkdir()

    def fake_run(profile, *, root=None, latex_project=None, verbose=False, hooks=None):
        assert verbose is True
        return VerificationRunResult(
            profile=profile,
            checks=(),
            overall_status=VerificationStatus.PASS,
            duration_seconds=0.1,
            environment={"Python": "3.13"},
        )

    monkeypatch.setattr("tools.verification.cli.run_verification", fake_run)
    assert run(["--root", str(tmp_path), "--verbose", "core"]) == 0


def test_cli_latex_smoke_requires_project() -> None:
    with pytest.raises(SystemExit) as exc:
        run(["latex-smoke"])
    assert exc.value.code != 0


def test_cli_all_requires_project() -> None:
    with pytest.raises(SystemExit) as exc:
        run(["all"])
    assert exc.value.code != 0


def test_cli_latex_smoke_dispatch(tmp_path: Path, monkeypatch) -> None:
    captured = {}

    def fake_run(profile, *, root=None, latex_project=None, verbose=False, hooks=None):
        captured["profile"] = profile
        captured["latex_project"] = latex_project
        return VerificationRunResult(
            profile=profile,
            checks=(VerificationCheckResult(name="LaTeX Smoke", status=VerificationStatus.PASS, layer="ARTIFACT INTEGRITY"),),
            overall_status=VerificationStatus.PASS,
            duration_seconds=0.1,
        )

    monkeypatch.setattr("tools.verification.cli.run_verification", fake_run)
    code = run(["--root", str(tmp_path), "latex-smoke", "04_LATEX/专题讲义/数学变换/勒让德变换"])
    assert code == 0
    assert captured["profile"] == "latex-smoke"
    assert captured["latex_project"].endswith("勒让德变换")


def test_cli_all_dispatch(tmp_path: Path, monkeypatch) -> None:
    captured = {}

    def fake_run(profile, *, root=None, latex_project=None, verbose=False, hooks=None):
        captured["profile"] = profile
        captured["project"] = latex_project
        return VerificationRunResult(
            profile=profile,
            checks=(),
            overall_status=VerificationStatus.PASS_WITH_WARNINGS,
            duration_seconds=0.1,
        )

    monkeypatch.setattr("tools.verification.cli.run_verification", fake_run)
    assert run(["all", "04_LATEX/x"]) == 0
    assert captured["profile"] == "all"


def test_cli_fail_exit(monkeypatch) -> None:
    def fake_run(profile, *, root=None, latex_project=None, verbose=False, hooks=None):
        return VerificationRunResult(
            profile=profile,
            checks=(),
            overall_status=VerificationStatus.FAIL,
            duration_seconds=0.1,
        )

    monkeypatch.setattr("tools.verification.cli.run_verification", fake_run)
    assert run(["core"]) == 1


def test_cli_blocked_exit(monkeypatch) -> None:
    def fake_run(profile, *, root=None, latex_project=None, verbose=False, hooks=None):
        return VerificationRunResult(
            profile=profile,
            checks=(),
            overall_status=VerificationStatus.BLOCKED,
            duration_seconds=0.1,
        )

    monkeypatch.setattr("tools.verification.cli.run_verification", fake_run)
    assert run(["core"]) == 1
