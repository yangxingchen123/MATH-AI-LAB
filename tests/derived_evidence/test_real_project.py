"""Real project derived evidence tests."""

from __future__ import annotations

from pathlib import Path

from tools.derived_evidence import TargetKey, build_derived_evidence_from_validation_results

from .conftest import validated_registries


def test_real_p0002_states(project: Path) -> None:
    from tests.workspace_indexer.conftest import write_attempt, write_problem

    write_problem(
        project,
        "02_题目库/研究中/P0002_x.md",
        pid="P0002",
        title="线性映射",
        extras="parts:\n  - a\n  - b\n  - c\n",
    )
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000001.md",
        aid="A000001",
        problem="P0002",
        part="b",
        outcome="correct",
        assistance="assisted",
    )
    write_attempt(
        project,
        "11_学习证据/尝试记录/A000002.md",
        aid="A000002",
        problem="P0002",
        part="a",
        outcome="partial",
        assistance="independent",
    )
    pr, ar = validated_registries(project)
    assert ar.summary.errors == 0
    snap = build_derived_evidence_from_validation_results(pr, ar)

    a_state = snap.target_states[TargetKey("P0002", "a")]
    assert a_state.attempt_ids == ("A000002",)
    assert a_state.outcome_counts["partial"] == 1
    assert a_state.assistance_counts["independent"] == 1

    b_state = snap.target_states[TargetKey("P0002", "b")]
    assert b_state.attempt_ids == ("A000001",)
    assert b_state.outcome_counts["correct"] == 1
    assert b_state.assistance_counts["assisted"] == 1

    assert TargetKey("P0002", "c") not in snap.target_states
    assert TargetKey("P0002", None) not in snap.target_states

    rollup = snap.problem_rollups["P0002"]
    assert rollup.attempt_count == 2
    assert rollup.whole_problem_attempt_count == 0
    assert rollup.attempted_parts == ("a", "b")
