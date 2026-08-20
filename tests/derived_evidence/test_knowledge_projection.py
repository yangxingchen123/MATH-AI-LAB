"""Tests for Knowledge Associated Evidence Projection v1."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.derived_evidence import (
    DerivedEvidenceBuildError,
    TargetKey,
    build_derived_evidence,
    build_knowledge_associated_evidence,
)
from tools.derived_evidence.constants import ASSISTANCE_CATEGORIES, OUTCOME_CATEGORIES
from tools.derived_evidence.models import (
    DerivedEvidenceSnapshot,
    KnowledgeAssociatedEvidenceRollup,
    KnowledgeAssociatedEvidenceSnapshot,
)
from tools.knowledge_validator.models import KnowledgeDocument

from .conftest import attempt_doc, problem_doc, validated_registries


def knowledge_doc(kid: str = "K0001", title: str = "Concept") -> KnowledgeDocument:
    return KnowledgeDocument(
        path=Path(f"/fake/{kid}.md"),
        relative_path=f"01_知识库/test/{kid}.md",
        data={
            "schema_version": 1,
            "id": kid,
            "type": "knowledge",
            "title": title,
            "status": "reviewed",
            "domain": "test",
        },
        object_id=kid,
        status="reviewed",
        domain="test",
    )


def _problems(*docs) -> dict:
    return {d.object_id: d for d in docs if d.object_id}


def _attempts(*docs) -> dict:
    return {d.object_id: d for d in docs if d.object_id}


def _knowledge(*docs) -> dict:
    return {d.object_id: d for d in docs if d.object_id}


def test_rollup_exact_fields() -> None:
    rollup = KnowledgeAssociatedEvidenceRollup(
        knowledge_id="K0001",
        associated_attempt_ids=("A000001",),
        associated_attempt_count=1,
        associated_outcome_counts={n: int(n == "correct") for n in OUTCOME_CATEGORIES},
        associated_assistance_counts={n: int(n == "independent") for n in ASSISTANCE_CATEGORIES},
    )
    assert rollup.knowledge_id == "K0001"
    assert rollup.associated_attempt_count == 1


def test_snapshot_knowledge_rollups_only() -> None:
    snap = KnowledgeAssociatedEvidenceSnapshot(knowledge_rollups={})
    assert snap.knowledge_rollups == {}


def test_eligible_whole_projection() -> None:
    p1 = problem_doc(pid="P0001", knowledge=["K0001"])
    a1 = attempt_doc(aid="A000001", problem="P0001", part=None, outcome="correct", assistance="independent")
    derived = build_derived_evidence(_problems(p1), _attempts(a1))
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001")),
        _problems(p1),
        _attempts(a1),
        derived,
    )
    assert "K0001" in snap.knowledge_rollups
    r = snap.knowledge_rollups["K0001"]
    assert r.associated_attempt_ids == ("A000001",)
    assert r.associated_attempt_count == 1
    assert r.associated_outcome_counts["correct"] == 1
    assert r.associated_assistance_counts["independent"] == 1


def test_multi_k_association() -> None:
    p1 = problem_doc(pid="P0001", knowledge=["K0001", "K0002", "K0003"])
    a1 = attempt_doc(aid="A000001", problem="P0001", part=None)
    derived = build_derived_evidence(_problems(p1), _attempts(a1))
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001"), knowledge_doc("K0002"), knowledge_doc("K0003")),
        _problems(p1),
        _attempts(a1),
        derived,
    )
    for kid in ("K0001", "K0002", "K0003"):
        assert snap.knowledge_rollups[kid].associated_attempt_ids == ("A000001",)
    assert sum(r.associated_attempt_count for r in snap.knowledge_rollups.values()) == 3


def test_multi_a_same_k() -> None:
    p1 = problem_doc(pid="P0001", knowledge=["K0001"])
    attempts = [
        attempt_doc(aid="A000001", problem="P0001", part=None, outcome="correct"),
        attempt_doc(aid="A000002", problem="P0001", part=None, outcome="partial"),
        attempt_doc(aid="A000003", problem="P0001", part=None, outcome="incorrect"),
    ]
    derived = build_derived_evidence(_problems(p1), _attempts(*attempts))
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001")),
        _problems(p1),
        _attempts(*attempts),
        derived,
    )
    r = snap.knowledge_rollups["K0001"]
    assert r.associated_attempt_ids == ("A000001", "A000002", "A000003")
    assert r.associated_attempt_count == 3
    assert r.associated_outcome_counts["correct"] == 1
    assert r.associated_outcome_counts["partial"] == 1
    assert r.associated_outcome_counts["incorrect"] == 1


def test_part_attempt_not_projected() -> None:
    p1 = problem_doc(pid="P0001", knowledge=["K0001", "K0002"])
    a1 = attempt_doc(aid="A000001", problem="P0001", part="a")
    derived = build_derived_evidence(_problems(p1), _attempts(a1))
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001"), knowledge_doc("K0002")),
        _problems(p1),
        _attempts(a1),
        derived,
    )
    assert snap.knowledge_rollups == {}


def test_mixed_whole_and_part() -> None:
    p1 = problem_doc(pid="P0001", parts=["a", "b"], knowledge=["K0001"])
    attempts = [
        attempt_doc(aid="A000001", problem="P0001", part=None, outcome="correct"),
        attempt_doc(aid="A000002", problem="P0001", part="a", outcome="partial"),
        attempt_doc(aid="A000003", problem="P0001", part="b", outcome="incorrect"),
    ]
    derived = build_derived_evidence(_problems(p1), _attempts(*attempts))
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001")),
        _problems(p1),
        _attempts(*attempts),
        derived,
    )
    r = snap.knowledge_rollups["K0001"]
    assert r.associated_attempt_ids == ("A000001",)
    assert r.associated_attempt_count == 1


def test_omitted_knowledge_no_projection() -> None:
    p1 = problem_doc(pid="P0001")
    a1 = attempt_doc(aid="A000001", problem="P0001", part=None)
    derived = build_derived_evidence(_problems(p1), _attempts(a1))
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001")),
        _problems(p1),
        _attempts(a1),
        derived,
    )
    assert snap.knowledge_rollups == {}


def test_incorrect_still_associated() -> None:
    p1 = problem_doc(pid="P0001", knowledge=["K0001"])
    a1 = attempt_doc(aid="A000001", problem="P0001", part=None, outcome="incorrect")
    derived = build_derived_evidence(_problems(p1), _attempts(a1))
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001")),
        _problems(p1),
        _attempts(a1),
        derived,
    )
    assert snap.knowledge_rollups["K0001"].associated_outcome_counts["incorrect"] == 1


def test_unassessed_still_associated() -> None:
    p1 = problem_doc(pid="P0001", knowledge=["K0001"])
    a1 = attempt_doc(aid="A000001", problem="P0001", part=None, outcome="unassessed")
    derived = build_derived_evidence(_problems(p1), _attempts(a1))
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001")),
        _problems(p1),
        _attempts(a1),
        derived,
    )
    assert snap.knowledge_rollups["K0001"].associated_outcome_counts["unassessed"] == 1


def test_assistance_omitted_bucket() -> None:
    p1 = problem_doc(pid="P0001", knowledge=["K0001"])
    a1 = attempt_doc(aid="A000001", problem="P0001", part=None, assistance=None)
    derived = build_derived_evidence(_problems(p1), _attempts(a1))
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001")),
        _problems(p1),
        _attempts(a1),
        derived,
    )
    assert snap.knowledge_rollups["K0001"].associated_assistance_counts["omitted"] == 1


def test_no_zero_k_materialization() -> None:
    p1 = problem_doc(pid="P0001", knowledge=["K0001"])
    a1 = attempt_doc(aid="A000001", problem="P0001", part=None)
    derived = build_derived_evidence(_problems(p1), _attempts(a1))
    snap = build_knowledge_associated_evidence(
        _knowledge(
            knowledge_doc("K0001"),
            knowledge_doc("K0002"),
            knowledge_doc("K0003"),
        ),
        _problems(p1),
        _attempts(a1),
        derived,
    )
    assert set(snap.knowledge_rollups) == {"K0001"}


def test_deterministic_ordering() -> None:
    p1 = problem_doc(pid="P0001", knowledge=["K0002", "K0001"])
    p2 = problem_doc(pid="P0002", knowledge=["K0001"])
    attempts = [
        attempt_doc(aid="A000002", problem="P0001", part=None),
        attempt_doc(aid="A000001", problem="P0002", part=None),
    ]
    derived = build_derived_evidence(_problems(p1, p2), _attempts(*attempts))
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001"), knowledge_doc("K0002")),
        _problems(p1, p2),
        _attempts(*attempts),
        derived,
    )
    assert list(snap.knowledge_rollups.keys()) == ["K0001", "K0002"]
    assert snap.knowledge_rollups["K0001"].associated_attempt_ids == ("A000001", "A000002")


def test_problem_rollup_not_used_for_projection() -> None:
    """Regression: part attempts in Problem rollup must not leak into K association."""
    p1 = problem_doc(pid="P0001", parts=["a"], knowledge=["K0001"])
    attempts = [
        attempt_doc(aid="A000001", problem="P0001", part="a", outcome="correct"),
    ]
    derived = build_derived_evidence(_problems(p1), _attempts(*attempts))
    assert derived.problem_rollups["P0001"].outcome_counts["correct"] == 1
    snap = build_knowledge_associated_evidence(
        _knowledge(knowledge_doc("K0001")),
        _problems(p1),
        _attempts(*attempts),
        derived,
    )
    assert snap.knowledge_rollups == {}


def test_no_interpretive_fields_on_models() -> None:
    forbidden = {
        "success_rate",
        "mastery",
        "weakness",
        "latest_attempted_at",
        "latest_outcome",
        "recency",
        "coverage",
        "review_priority",
    }
    rollup_fields = {f.name for f in KnowledgeAssociatedEvidenceRollup.__dataclass_fields__.values()}
    assert forbidden.isdisjoint(rollup_fields)


def test_real_project_empty_projection(project: Path) -> None:
    from tests.workspace_indexer.conftest import write_attempt, write_problem

    write_problem(
        project,
        "02_题目库/研究中/P0002_x.md",
        pid="P0002",
        extras="parts:\n  - a\n  - b\n  - c\n",
    )
    write_attempt(project, "11_学习证据/尝试记录/A000001.md", aid="A000001", problem="P0002", part="b")
    write_attempt(project, "11_学习证据/尝试记录/A000002.md", aid="A000002", problem="P0002", part="a")
    from tools.knowledge_validator import validate_project as validate_knowledge_project

    kr = validate_knowledge_project(root=project)
    pr, ar = validated_registries(project)
    derived = build_derived_evidence(
        {d.object_id: d for d in pr.documents if d.object_id},
        dict(ar.registry) if ar.registry else {},
    )
    snap = build_knowledge_associated_evidence(
        {d.object_id: d for d in kr.documents if d.object_id},
        {d.object_id: d for d in pr.documents if d.object_id},
        dict(ar.registry) if ar.registry else {},
        derived,
    )
    assert snap.knowledge_rollups == {}
