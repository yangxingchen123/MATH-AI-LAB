"""Tests for target-level derived evidence builder."""

from __future__ import annotations

from tools.derived_evidence import TargetKey, build_derived_evidence
from tools.derived_evidence.constants import ASSISTANCE_CATEGORIES, OUTCOME_CATEGORIES

from .conftest import attempt_doc, problem_doc


def test_one_partial_independent() -> None:
    attempts = {"A000002": attempt_doc(aid="A000002", part="a", outcome="partial", assistance="independent")}
    snap = build_derived_evidence([problem_doc(parts=["a", "b", "c"])], attempts)
    key = TargetKey("P0002", "a")
    state = snap.target_states[key]
    assert state.attempt_ids == ("A000002",)
    assert state.attempt_count == 1
    assert state.outcome_counts["partial"] == 1
    assert sum(state.outcome_counts.values()) == 1
    assert state.assistance_counts["independent"] == 1


def test_one_correct_assisted() -> None:
    attempts = {"A000001": attempt_doc()}
    snap = build_derived_evidence([problem_doc()], attempts)
    key = TargetKey("P0002", "b")
    state = snap.target_states[key]
    assert state.outcome_counts["correct"] == 1
    assert state.assistance_counts["assisted"] == 1


def test_same_target_two_a_ids() -> None:
    attempts = {
        "A000001": attempt_doc(aid="A000001"),
        "A000003": attempt_doc(aid="A000003", outcome="partial", assistance="independent"),
    }
    snap = build_derived_evidence([problem_doc()], attempts)
    state = snap.target_states[TargetKey("P0002", "b")]
    assert state.attempt_count == 2
    assert state.attempt_ids == ("A000001", "A000003")


def test_correction_still_one_count() -> None:
    doc = attempt_doc()
    doc.data["corrections"] = [{"at": "2026-08-19", "note": "fix"}, {"at": "2026-08-20", "note": "fix2"}]
    snap = build_derived_evidence([problem_doc()], {"A000001": doc})
    state = snap.target_states[TargetKey("P0002", "b")]
    assert state.attempt_count == 1


def test_unassessed_creates_state() -> None:
    attempts = {"A000001": attempt_doc(outcome="unassessed", assistance=None)}
    snap = build_derived_evidence([problem_doc()], attempts)
    state = snap.target_states[TargetKey("P0002", "b")]
    assert state.outcome_counts["unassessed"] == 1


def test_assistance_omitted_bucket() -> None:
    attempts = {"A000001": attempt_doc(assistance=None)}
    snap = build_derived_evidence([problem_doc()], attempts)
    state = snap.target_states[TargetKey("P0002", "b")]
    assert state.assistance_counts["omitted"] == 1
    assert state.assistance_counts["independent"] == 0


def test_complete_outcome_and_assistance_maps() -> None:
    snap = build_derived_evidence([problem_doc()], {"A000001": attempt_doc()})
    state = snap.target_states[TargetKey("P0002", "b")]
    assert set(state.outcome_counts) == set(OUTCOME_CATEGORIES)
    assert set(state.assistance_counts) == set(ASSISTANCE_CATEGORIES)


def test_attempt_ids_ascending_not_chronological() -> None:
    attempts = {
        "A000010": attempt_doc(aid="A000010"),
        "A000002": attempt_doc(aid="A000002", outcome="partial", assistance="independent"),
    }
    snap = build_derived_evidence([problem_doc()], attempts)
    assert snap.target_states[TargetKey("P0002", "b")].attempt_ids == ("A000002", "A000010")


def test_no_attempt_no_target_state() -> None:
    snap = build_derived_evidence([problem_doc()], {})
    assert snap.target_states == {}


def test_body_only_same_metadata_same_snapshot() -> None:
    a = attempt_doc()
    b = attempt_doc()
    b.body = "different body text"
    s1 = build_derived_evidence([problem_doc()], {"A000001": a})
    s2 = build_derived_evidence([problem_doc()], {"A000001": b})
    assert s1 == s2
