"""Automated Normal Operation v1 acceptance (disposable temp workspaces only)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from tests.attempt_validator.conftest import attempt_record, write_ledger
from tests.latex_build.conftest import write_latex_project
from tests.normal_operation.conftest import delta, snapshot_project
from tests.normal_operation.test_operations import _setup_p0002
from tests.problem_validator.conftest import problem_md
from tools.normal_operation.operation_models import (
    ArtifactStatus,
    AttemptRecordStatus,
    PersistenceStatus,
)
from tools.normal_operation.operations import (
    persist_canonical_solution_op,
    publish_pdf_op,
    record_user_attempt_op,
    study_to_auto_op,
)
from tools.problem_solution.slots import count_slots_for_target, find_slot
from tools.workspace_indexer.models import IndexResultKind


def _ready_project(tmp_path: Path) -> None:
    _setup_p0002(tmp_path)
    (tmp_path / "12_方法库").mkdir(exist_ok=True)
    write_ledger(
        tmp_path,
        "P0002",
        [attempt_record(aid="A000001")],
        {"A000001": "existing attempt"},
    )


@pytest.fixture
def op_root(tmp_path: Path) -> Path:
    _ready_project(tmp_path)
    return tmp_path


def test_acceptance_existing_problem_no_op(op_root: Path) -> None:
    before = snapshot_project(op_root)
    path = op_root / "02_题目库" / "P0002.md"
    body = path.read_text(encoding="utf-8").split("---", 2)[2]
    slot = find_slot(body, problem_id="P0002", part="a")
    assert slot is not None
    result = persist_canonical_solution_op(
        op_root,
        problem_id="P0002",
        part="a",
        content=slot.content.strip(),
    )
    after = snapshot_project(op_root)
    d = delta(before, after)
    assert result.persistence == PersistenceStatus.NO_OP
    assert result.finalize is None
    assert result.workspace_sync_performed is False
    assert d["attempts"] == 0
    assert d["problems"] == 0
    assert count_slots_for_target(body, problem_id="P0002", part="a") == 1


def test_acceptance_existing_problem_upsert(op_root: Path) -> None:
    before = snapshot_project(op_root)
    result = persist_canonical_solution_op(
        op_root,
        problem_id="P0002",
        part="b",
        content="Part b canonical solution content.",
    )
    after = snapshot_project(op_root)
    d = delta(before, after)
    assert result.persistence == PersistenceStatus.WRITTEN
    assert result.finalize is not None
    assert result.finalize.overall_pass
    assert d["attempts"] == 0
    assert d["problems"] == 0
    text = (op_root / "02_题目库" / "P0002.md").read_text(encoding="utf-8")
    assert count_slots_for_target(text.split("---", 2)[2], problem_id="P0002", part="b") == 1


def test_acceptance_user_review_one_attempt(op_root: Path) -> None:
    before = snapshot_project(op_root)
    result = record_user_attempt_op(
        op_root,
        problem_id="P0002",
        record=attempt_record(
            aid="A000002",
            part="a",
            outcome="partial",
            assistance="independent",
            attempted_at="2026-08-20T04:00+08:00",
        ),
        narrative="User-authored solving episode.",
    )
    after = snapshot_project(op_root)
    d = delta(before, after)
    assert result.attempt == AttemptRecordStatus.CREATED
    assert d["attempts"] == 1
    assert d["problems"] == 0
    assert result.finalize is not None
    assert result.finalize.workspace_final == IndexResultKind.CURRENT.value


def test_acceptance_reference_review_no_attempt(op_root: Path) -> None:
    """Semantic decision already made: reference source → no evidence mutation."""
    before = snapshot_project(op_root)
    after = snapshot_project(op_root)
    d = delta(before, after)
    assert d["attempts"] == 0
    assert d["problems"] == 0
    assert d["knowledge"] == 0
    assert d["methods"] == 0


def test_acceptance_temporary_question_isolation(op_root: Path) -> None:
    before = snapshot_project(op_root)
    # Temporary solve: no production operation invoked.
    after = snapshot_project(op_root)
    d = delta(before, after)
    assert d["problems"] == 0
    assert d["attempts"] == 0
    assert d["knowledge"] == 0
    assert d["methods"] == 0


def test_acceptance_study_to_auto_chain(op_root: Path) -> None:
    before = snapshot_project(op_root)
    result = study_to_auto_op(
        op_root,
        problem_id="P0002",
        part="c",
        record=attempt_record(
            aid="A000003",
            part="c",
            outcome="unsolved",
            assistance="independent",
            attempted_at="2026-08-20T04:10+08:00",
        ),
        narrative="STUDY episode ended; user gave up.",
        solution_content="AUTO canonical solution for part c.",
    )
    after = snapshot_project(op_root)
    d = delta(before, after)
    assert result.attempt == AttemptRecordStatus.CREATED
    assert d["attempts"] == 1
    assert result.persistence == PersistenceStatus.WRITTEN
    assert result.finalize is not None
    assert "attempt" in result.changed_types
    assert "problem" in result.changed_types
    assert result.finalize.overall_pass


def test_acceptance_add_problem_and_solve(op_root: Path) -> None:
    before = snapshot_project(op_root)
    new_path = op_root / "02_题目库" / "P0003.md"
    new_path.write_text(
        problem_md(pid="P0003", title="New Problem", body="# New\n\n## 题目\n\nTask\n"),
        encoding="utf-8",
    )
    mid = snapshot_project(op_root)
    assert len(mid.problem_ids - before.problem_ids) == 1
    result = persist_canonical_solution_op(
        op_root,
        problem_id="P0003",
        part=None,
        content="Whole-problem solution.",
    )
    after = snapshot_project(op_root)
    d = delta(before, after)
    assert result.persistence == PersistenceStatus.WRITTEN
    assert d["problems"] == 1
    assert d["attempts"] == 0
    assert d["knowledge"] == 0
    assert result.finalize is not None
    assert result.finalize.overall_pass


def test_acceptance_explicit_pdf_integration(op_root: Path) -> None:
    project = write_latex_project(op_root, "专题讲义/smoke", with_entry=True)
    fake_pdf = op_root / "08_成果输出" / "PDF" / "专题讲义" / "smoke.pdf"
    fake_pdf.parent.mkdir(parents=True, exist_ok=True)

    from tools.latex_build.models import (
        CompileResult,
        InspectionResult,
        LatexBuildResult,
        PublishResult,
        PublishStatus,
        ResolvedLatexProject,
    )

    resolved = ResolvedLatexProject(
        project_dir=project,
        relative_project_path=Path("专题讲义/smoke"),
        main_tex=project / "smoke.tex",
        formal_pdf=fake_pdf,
    )
    build_result = LatexBuildResult(
        project=resolved,
        compile_result=CompileResult(
            success=True,
            return_code=0,
            compiler="xelatex",
            compiler_runs=1,
            stdout="",
            stderr="",
            log_text="",
            built_pdf=fake_pdf,
        ),
        inspection_result=InspectionResult(blocking_errors=(), warnings=()),
        publish_result=PublishResult(
            status=PublishStatus.CREATED,
            formal_pdf=fake_pdf,
            writes=1,
        ),
    )
    with patch("tools.normal_operation.operations.build_latex_project", return_value=build_result):
        result = publish_pdf_op(op_root, latex_project=project, changed_before_build=[])
    assert result.artifact == ArtifactStatus.COMPLETE
    assert result.artifact_path == str(fake_pdf)
