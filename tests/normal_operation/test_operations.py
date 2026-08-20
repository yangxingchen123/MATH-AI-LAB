"""Unit tests for mutation → finalizer orchestration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from tests.attempt_validator.conftest import attempt_record, setup_p0002_multipart, write_ledger
from tests.problem_validator.conftest import problem_md, write_project
from tools.normal_operation.operation_models import AttemptRecordStatus, PersistenceStatus
from tools.normal_operation.operations import persist_canonical_solution_op, record_user_attempt_op
from tools.problem_solution.slots import wrap_slot_content


def _setup_p0002(root: Path) -> None:
    write_project(root)
    (root / "12_方法库").mkdir(exist_ok=True)
    kb = root / "01_知识库"
    (kb / "K0001.md").write_text(
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
    setup_p0002_multipart(root)
    body = (
        "# T\n\n## 题目\n\nQ\n\n## 解答\n\n"
        + wrap_slot_content("P0002/a", "existing")
        + "\n"
    )
    (root / "02_题目库" / "P0002.md").write_text(
        problem_md(pid="P0002", extras="parts:\n  - a\n  - b\n  - c\n", body=body),
        encoding="utf-8",
    )


def test_no_op_skips_finalizer(tmp_path: Path) -> None:
    _setup_p0002(tmp_path)
    with patch("tools.normal_operation.operations.finalize") as fin:
        result = persist_canonical_solution_op(
            tmp_path,
            problem_id="P0002",
            part="a",
            content="existing",
            auto_reconcile=False,
        )
    fin.assert_not_called()
    assert result.persistence == PersistenceStatus.NO_OP
    assert result.finalize is None


def test_written_triggers_finalizer_with_problem_changed(tmp_path: Path) -> None:
    _setup_p0002(tmp_path)
    with patch("tools.normal_operation.operations.finalize") as fin:
        from tools.normal_operation.models import FinalizeResult, LayerStatus

        fin.return_value = FinalizeResult(changed_types=["problem"], validation_status=LayerStatus.PASS)
        result = persist_canonical_solution_op(
            tmp_path,
            problem_id="P0002",
            part="b",
            content="new part b solution",
            auto_reconcile=False,
        )
    fin.assert_called_once()
    assert fin.call_args.kwargs["changed"] == ["problem"]
    assert result.persistence == PersistenceStatus.WRITTEN
    assert result.changed_types == ["problem"]


def test_update_is_corrected(tmp_path: Path) -> None:
    _setup_p0002(tmp_path)
    with patch("tools.normal_operation.operations.finalize") as fin:
        from tools.normal_operation.models import FinalizeResult, LayerStatus

        fin.return_value = FinalizeResult(changed_types=["problem"], validation_status=LayerStatus.PASS)
        result = persist_canonical_solution_op(
            tmp_path,
            problem_id="P0002",
            part="a",
            content="updated a",
            auto_reconcile=False,
        )
    fin.assert_called_once()
    assert result.persistence == PersistenceStatus.CORRECTED


def test_attempt_append_auto_finalizer(tmp_path: Path) -> None:
    _setup_p0002(tmp_path)
    write_ledger(tmp_path, "P0002", [attempt_record()], {"A000001": "body"})
    with patch("tools.normal_operation.operations.finalize") as fin:
        from tools.normal_operation.models import FinalizeResult, LayerStatus

        fin.return_value = FinalizeResult(changed_types=["attempt"], validation_status=LayerStatus.PASS)
        result = record_user_attempt_op(
            tmp_path,
            problem_id="P0002",
            record=attempt_record(aid="A000002", part="a", attempted_at="2026-08-19T22:05+08:00"),
            narrative="user work",
        )
    fin.assert_called_once()
    assert fin.call_args.kwargs["changed"] == ["attempt"]
    assert result.attempt == AttemptRecordStatus.CREATED
