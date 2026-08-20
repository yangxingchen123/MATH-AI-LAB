"""Tests for problem rollup and invariants."""

from __future__ import annotations

from tools.derived_evidence import TargetKey, build_derived_evidence

from .conftest import attempt_doc, problem_doc


def test_p0002_rollup() -> None:
    attempts = {
        "A000001": attempt_doc(aid="A000001", part="b"),
        "A000002": attempt_doc(aid="A000002", part="a", outcome="partial", assistance="independent"),
    }
    problems = [problem_doc(parts=["a", "b", "c"])]
    snap = build_derived_evidence(problems, attempts)
    rollup = snap.problem_rollups["P0002"]
    assert rollup.attempt_ids == ("A000001", "A000002")
    assert rollup.attempt_count == 2
    assert rollup.whole_problem_attempt_count == 0
    assert rollup.attempted_parts == ("a", "b")
    assert rollup.part_attempt_counts == {"a": 1, "b": 1}
    assert rollup.outcome_counts["correct"] == 1
    assert rollup.outcome_counts["partial"] == 1
    assert rollup.assistance_counts["independent"] == 1
    assert rollup.assistance_counts["assisted"] == 1


def test_whole_and_part_attempts() -> None:
    attempts = {
        "A000001": attempt_doc(aid="A000001", part=None),
        "A000002": attempt_doc(aid="A000002", part="a", outcome="partial", assistance="independent"),
    }
    snap = build_derived_evidence([problem_doc(parts=["a", "b"])], attempts)
    assert TargetKey("P0002", None) in snap.target_states
    rollup = snap.problem_rollups["P0002"]
    assert rollup.whole_problem_attempt_count == 1
    assert rollup.part_attempt_counts == {"a": 1}
    assert rollup.attempt_count == 2


def test_part_order_follows_problem_declared_order() -> None:
    attempts = {
        "A000002": attempt_doc(aid="A000002", part="b", outcome="partial", assistance="independent"),
        "A000003": attempt_doc(aid="A000003", part="a", outcome="incorrect", assistance="omitted"),
    }
    attempts["A000003"].data.pop("assistance")
    snap = build_derived_evidence([problem_doc(parts=["a", "b", "c"])], attempts)
    rollup = snap.problem_rollups["P0002"]
    assert rollup.attempted_parts == ("a", "b")
    assert list(rollup.part_attempt_counts.keys()) == ["a", "b"]


def test_zero_evidence_problem_absent() -> None:
    snap = build_derived_evidence([problem_doc(), problem_doc(pid="P0001")], {})
    assert "P0002" not in snap.problem_rollups
    assert "P0001" not in snap.problem_rollups


def test_deletion_removes_target_and_rollup() -> None:
    attempts = {"A000001": attempt_doc()}
    snap1 = build_derived_evidence([problem_doc()], attempts)
    assert TargetKey("P0002", "b") in snap1.target_states
    snap2 = build_derived_evidence([problem_doc()], {})
    assert TargetKey("P0002", "b") not in snap2.target_states
    assert "P0002" not in snap2.problem_rollups


def test_part_c_absent_when_no_evidence() -> None:
    attempts = {
        "A000001": attempt_doc(aid="A000001", part="b"),
        "A000002": attempt_doc(aid="A000002", part="a", outcome="partial", assistance="independent"),
    }
    snap = build_derived_evidence([problem_doc(parts=["a", "b", "c"])], attempts)
    assert TargetKey("P0002", "c") not in snap.target_states
    assert "c" not in snap.problem_rollups["P0002"].part_attempt_counts
