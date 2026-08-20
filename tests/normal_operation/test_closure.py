"""Tests for completion, naming, freshness, workflow, reconcile."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from tests.attempt_validator.conftest import attempt_record, write_ledger
from tests.latex_build.conftest import install_pinned_vendor
from tests.problem_validator.conftest import problem_md, write_project
from tools.normal_operation.artifact import FreshnessState, inspect_artifact, materialize_problem_latex
from tools.normal_operation.completion import inspect_problem_completion
from tools.normal_operation.freshness import sha256_text
from tools.normal_operation.naming import artifact_stem, sanitize_windows_filename
from tools.normal_operation.operation_models import PersistenceStatus
from tools.normal_operation.operations import persist_canonical_solution_op
from tools.normal_operation.reconcile import reconcile_problem
from tools.normal_operation.workflow import move_problem_to_workflow
from tools.problem_solution.slots import wrap_slot_content
from tools.problem_solution.writer import upsert_canonical_solution


def _kb(root: Path) -> None:
    write_project(root)
    (root / "12_方法库").mkdir(exist_ok=True)
    (root / "01_知识库" / "K0001.md").write_text(
        """---
schema_version: 1
id: K0001
type: knowledge
title: K
aliases: []
status: reviewed
created: 2026-08-19
updated: 2026-08-19
domain: 线性代数
prerequisites: []
related: []
---

body
""",
        encoding="utf-8",
    )


def _multipart_body(*, a: str | None = "a-ans", b: str | None = None, c: str | None = "c-ans") -> str:
    chunks = ["# T\n\n## 题目\n\nQ\n\n## 解答\n"]
    if a is not None:
        chunks.append(wrap_slot_content("P0002/a", a))
    if b is not None:
        chunks.append(wrap_slot_content("P0002/b", b))
    if c is not None:
        chunks.append(wrap_slot_content("P0002/c", c))
    return "\n\n".join(chunks) + "\n"


def _write_p0002(root: Path, body: str, *, workflow: str = "研究中") -> Path:
    _kb(root)
    dest = root / "02_题目库" / workflow
    dest.mkdir(parents=True, exist_ok=True)
    (root / "11_学习证据" / "尝试记录").mkdir(parents=True, exist_ok=True)
    path = dest / "P0002.md"
    path.write_text(
        problem_md(
            pid="P0002",
            title="线性映射测试",
            extras="parts:\n  - a\n  - b\n  - c\n",
            body=body,
        ),
        encoding="utf-8",
    )
    return path


def test_completion_incomplete_missing_b(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b=None))
    insp = inspect_problem_completion(tmp_path, "P0002")
    assert insp.complete is False
    assert insp.missing_targets == ["P0002/b"]
    assert "P0002/a" in insp.present_targets
    assert "P0002/c" in insp.present_targets


def test_completion_complete_multipart(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b-ans"))
    insp = inspect_problem_completion(tmp_path, "P0002")
    assert insp.complete is True
    assert insp.missing_targets == []


def test_attempt_does_not_count_as_canonical(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b=None))
    write_ledger(
        tmp_path,
        "P0002",
        [attempt_record(aid="A000001", part="b", outcome="correct")],
        {"A000001": "correct attempt narrative"},
    )
    insp = inspect_problem_completion(tmp_path, "P0002")
    assert "P0002/b" in insp.missing_targets
    assert insp.complete is False


def test_legacy_heading_is_not_canonical_coverage(tmp_path: Path) -> None:
    body = (
        "# T\n\n## 题目\n\nQ\n\n## 研究记录\n\n"
        "### (a) AI-generated Solution\n\nlegacy-a\n\n"
        + wrap_slot_content("P0002/b", "b-ans")
        + "\n\n"
        + wrap_slot_content("P0002/c", "c-ans")
        + "\n"
    )
    _write_p0002(tmp_path, body)
    insp = inspect_problem_completion(tmp_path, "P0002")
    assert "P0002/a" in insp.missing_targets
    assert insp.complete is False


def test_naming_sanitizer_illegal_chars() -> None:
    assert "<" not in sanitize_windows_filename('a<b>:"/\\|?*c')
    assert artifact_stem("P0002", 'φ(X)=AX-XB?').startswith("P0002_")
    assert sanitize_windows_filename("CON") == "_CON"


def test_hash_stable() -> None:
    assert sha256_text("a\r\nb") == sha256_text("a\nb")


def test_auto_archive_when_complete(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"))
    # Copy minimal template so artifact path can run; mock build
    install_pinned_vendor(tmp_path)

    with patch("tools.normal_operation.artifact.build_latex_project") as build:
        from tools.latex_build.models import (
            CompileResult,
            InspectionResult,
            LatexBuildResult,
            PublishResult,
            PublishStatus,
            ResolvedLatexProject,
        )

        def _fake_build(project, repo_root=None):
            paths = Path(project)
            pdf = tmp_path / "08_成果输出" / "PDF" / "题目解答" / "未分类" / f"{paths.name}.pdf"
            pdf.parent.mkdir(parents=True, exist_ok=True)
            pdf.write_bytes(b"%PDF-1.4\n%%EOF\n")
            return LatexBuildResult(
                project=ResolvedLatexProject(
                    project_dir=paths,
                    relative_project_path=paths.relative_to(tmp_path / "04_LATEX"),
                    main_tex=paths / f"{paths.name}.tex",
                    formal_pdf=pdf,
                ),
                compile_result=CompileResult(
                    success=True,
                    return_code=0,
                    compiler="xelatex",
                    compiler_runs=1,
                    stdout="",
                    stderr="",
                    log_text="",
                    built_pdf=pdf,
                ),
                inspection_result=InspectionResult(blocking_errors=(), warnings=()),
                publish_result=PublishResult(
                    status=PublishStatus.CREATED,
                    formal_pdf=pdf,
                    writes=1,
                ),
            )

        build.side_effect = _fake_build
        recon = reconcile_problem(tmp_path, problem_id="P0002", artifact_domain="未分类")

    assert recon.workflow_after == "已解决"
    assert recon.counters.workflow_moves == 1
    assert (tmp_path / "02_题目库" / "已解决" / "P0002.md").is_file()


def test_opt_out_keeps_researching(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"))
    recon = reconcile_problem(tmp_path, problem_id="P0002", auto_close=False, auto_artifact=False)
    assert recon.workflow_after == "研究中"
    assert recon.skipped_archive is True


def test_no_op_still_reconciles(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"))
    with patch("tools.normal_operation.reconcile.reconcile_problem") as recon:
        from tools.normal_operation.reconcile import ReconcileResult
        from tools.normal_operation.completion import CompletionInspection

        recon.return_value = ReconcileResult(
            problem_id="P0002",
            completion=CompletionInspection(
                problem_id="P0002",
                problem_path="x",
                required_targets=["P0002/a", "P0002/b", "P0002/c"],
                present_targets=["P0002/a", "P0002/b", "P0002/c"],
                complete=True,
            ),
            workflow_before="研究中",
            workflow_after="研究中",
        )
        result = persist_canonical_solution_op(
            tmp_path,
            problem_id="P0002",
            part="a",
            content="a-ans",
            auto_reconcile=True,
            auto_artifact=False,
            auto_close=False,
        )
    recon.assert_called_once()
    assert result.persistence == PersistenceStatus.NO_OP


def test_second_reconcile_zero_writes(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"), workflow="已解决")
    install_pinned_vendor(tmp_path)

    # First: materialize only, mock build
    with patch("tools.normal_operation.artifact.build_latex_project") as build:
        from tools.latex_build.models import (
            CompileResult,
            InspectionResult,
            LatexBuildResult,
            PublishResult,
            PublishStatus,
            ResolvedLatexProject,
        )

        def _fake_build(project, repo_root=None):
            paths = Path(project)
            pdf = tmp_path / "08_成果输出" / "PDF" / "题目解答" / "未分类" / f"{paths.name}.pdf"
            pdf.parent.mkdir(parents=True, exist_ok=True)
            pdf.write_bytes(b"%PDF-1.4\n%%EOF\n")
            return LatexBuildResult(
                project=ResolvedLatexProject(
                    project_dir=paths,
                    relative_project_path=paths.relative_to(tmp_path / "04_LATEX"),
                    main_tex=paths / f"{paths.name}.tex",
                    formal_pdf=pdf,
                ),
                compile_result=CompileResult(
                    success=True,
                    return_code=0,
                    compiler="xelatex",
                    compiler_runs=1,
                    stdout="",
                    stderr="",
                    log_text="",
                    built_pdf=pdf,
                ),
                inspection_result=InspectionResult(blocking_errors=(), warnings=()),
                publish_result=PublishResult(status=PublishStatus.CREATED, formal_pdf=pdf, writes=1),
            )

        build.side_effect = _fake_build
        first = reconcile_problem(tmp_path, problem_id="P0002")
        assert first.counters.builds >= 1

    second = reconcile_problem(tmp_path, problem_id="P0002")
    assert second.counters.source_writes == 0
    assert second.counters.workflow_moves == 0
    assert second.counters.latex_writes == 0
    assert second.counters.builds == 0
    assert second.counters.pdf_replaces == 0
    assert second.counters.workspace_syncs == 0


def test_solved_correction_stays_solved(tmp_path: Path) -> None:
    path = _write_p0002(tmp_path, _multipart_body(b="b"), workflow="已解决")
    install_pinned_vendor(tmp_path)
    move = move_problem_to_workflow(tmp_path, "P0002", target_workflow="已解决")
    assert move.moved is False
    upsert_canonical_solution(tmp_path, problem_id="P0002", part="b", content="corrected b")
    # still under 已解决
    assert (tmp_path / "02_题目库" / "已解决" / "P0002.md").is_file()
    insp = inspect_artifact(tmp_path, problem_id="P0002")
    # after correction without materialize, latex missing or stale
    assert insp.latex in {FreshnessState.MISSING, FreshnessState.STALE}


def _fake_success_build(tmp_path: Path):
    from tools.latex_build.models import (
        CompileResult,
        InspectionResult,
        LatexBuildResult,
        PublishResult,
        PublishStatus,
        ResolvedLatexProject,
    )

    def _fake_build(project, repo_root=None):
        paths = Path(project)
        pdf = tmp_path / "08_成果输出" / "PDF" / "题目解答" / "未分类" / f"{paths.name}.pdf"
        pdf.parent.mkdir(parents=True, exist_ok=True)
        if not pdf.is_file():
            pdf.write_bytes(b"%PDF-1.4\n%%EOF\n")
        return LatexBuildResult(
            project=ResolvedLatexProject(
                project_dir=paths,
                relative_project_path=paths.relative_to(tmp_path / "04_LATEX"),
                main_tex=paths / f"{paths.name}.tex",
                formal_pdf=pdf,
            ),
            compile_result=CompileResult(
                success=True,
                return_code=0,
                compiler="xelatex",
                compiler_runs=1,
                stdout="",
                stderr="",
                log_text="",
                built_pdf=pdf,
            ),
            inspection_result=InspectionResult(blocking_errors=(), warnings=()),
            publish_result=PublishResult(
                status=PublishStatus.CREATED if pdf.stat().st_size > 0 else PublishStatus.UPDATED,
                formal_pdf=pdf,
                writes=1,
            ),
        )

    return _fake_build


def test_complete_missing_latex_materializes(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"), workflow="已解决")
    install_pinned_vendor(tmp_path)
    mat = materialize_problem_latex(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert mat.written is True
    assert mat.paths is not None
    assert mat.paths.entry_tex.is_file()
    assert not (mat.paths.project_dir / "elegantbook.cls").exists()


def test_source_hash_unchanged_keeps_latex_current(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"), workflow="已解决")
    install_pinned_vendor(tmp_path)
    materialize_problem_latex(tmp_path, problem_id="P0002", artifact_domain="未分类")
    insp = inspect_artifact(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert insp.latex == FreshnessState.CURRENT


def test_source_change_marks_latex_stale(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"), workflow="已解决")
    install_pinned_vendor(tmp_path)
    materialize_problem_latex(tmp_path, problem_id="P0002", artifact_domain="未分类")
    upsert_canonical_solution(tmp_path, problem_id="P0002", part="a", content="changed-a")
    insp = inspect_artifact(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert insp.latex == FreshnessState.STALE


def test_xelatex_failure_keeps_solved_and_old_pdf(tmp_path: Path) -> None:
    _write_p0002(tmp_path, _multipart_body(b="b"), workflow="已解决")
    install_pinned_vendor(tmp_path)
    with patch("tools.normal_operation.artifact.build_latex_project") as build:
        build.side_effect = _fake_success_build(tmp_path)
        first = reconcile_problem(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert first.workflow_after == "已解决"
    pdf = first.artifact.paths.formal_pdf
    old = pdf.read_bytes()
    upsert_canonical_solution(tmp_path, problem_id="P0002", part="b", content="stale-b")

    from tools.latex_build.models import (
        CompileResult,
        InspectionResult,
        LatexBuildResult,
        PublishResult,
        PublishStatus,
        ResolvedLatexProject,
    )

    def _fail(project, repo_root=None):
        paths = Path(project)
        return LatexBuildResult(
            project=ResolvedLatexProject(
                project_dir=paths,
                relative_project_path=paths.relative_to(tmp_path / "04_LATEX"),
                main_tex=paths / f"{paths.name}.tex",
                formal_pdf=pdf,
            ),
            compile_result=CompileResult(
                success=False,
                return_code=1,
                compiler="xelatex",
                compiler_runs=1,
                stdout="",
                stderr="fail",
                log_text="! Emergency stop",
                built_pdf=None,
            ),
            inspection_result=InspectionResult(blocking_errors=(), warnings=()),
            publish_result=PublishResult(status=PublishStatus.BLOCKED, formal_pdf=pdf, writes=0),
        )

    with patch("tools.normal_operation.artifact.build_latex_project", side_effect=_fail):
        failed = reconcile_problem(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert (tmp_path / "02_题目库" / "已解决" / "P0002.md").is_file()
    assert failed.workflow_after == "已解决"
    assert failed.artifact.pdf == FreshnessState.FAILED
    assert pdf.read_bytes() == old

    with patch("tools.normal_operation.artifact.build_latex_project") as build:
        build.side_effect = _fake_success_build(tmp_path)
        recovered = reconcile_problem(tmp_path, problem_id="P0002", artifact_domain="未分类")
    assert recovered.artifact.pdf == FreshnessState.CURRENT
    assert recovered.artifact.builds >= 1
    assert pdf.is_file()
    assert pdf.stat().st_size > 0
