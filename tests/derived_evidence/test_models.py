"""Tests for derived evidence models."""

from __future__ import annotations

from tools.derived_evidence.constants import ASSISTANCE_CATEGORIES, OUTCOME_CATEGORIES
from tools.derived_evidence.models import (
    DerivedEvidenceSnapshot,
    ProblemEvidenceRollup,
    TargetEvidenceState,
    TargetKey,
    empty_assistance_counts,
    empty_outcome_counts,
)


def test_target_key_immutable_hashable() -> None:
    whole = TargetKey("P0002", None)
    part = TargetKey("P0002", "a")
    assert whole != part
    assert hash(whole) != hash(part)
    assert {whole, part}


def test_target_key_structural_equality() -> None:
    a = TargetKey("P0002", "a")
    b = TargetKey("P0002", "a")
    assert a == b


def test_empty_maps_complete() -> None:
    oc = empty_outcome_counts()
    ac = empty_assistance_counts()
    assert set(oc) == set(OUTCOME_CATEGORIES)
    assert set(ac) == set(ASSISTANCE_CATEGORIES)
    assert all(v == 0 for v in oc.values())
    assert all(v == 0 for v in ac.values())


def test_snapshot_fields() -> None:
    key = TargetKey("P0002", "a")
    state = TargetEvidenceState(
        target=key,
        attempt_ids=("A000002",),
        attempt_count=1,
        outcome_counts=empty_outcome_counts(),
        assistance_counts=empty_assistance_counts(),
    )
    rollup = ProblemEvidenceRollup(
        problem_id="P0002",
        attempt_ids=("A000002",),
        attempt_count=1,
        outcome_counts=empty_outcome_counts(),
        assistance_counts=empty_assistance_counts(),
        whole_problem_attempt_count=0,
        attempted_parts=("a",),
        part_attempt_counts={"a": 1},
    )
    snap = DerivedEvidenceSnapshot(target_states={key: state}, problem_rollups={"P0002": rollup})
    assert key in snap.target_states
    assert "P0002" in snap.problem_rollups
