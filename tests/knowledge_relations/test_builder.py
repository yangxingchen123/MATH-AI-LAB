"""Tests for Formal Knowledge Relation builder."""

from __future__ import annotations

from tools.knowledge_relations.builder import build_knowledge_relations
from tools.knowledge_relations.models import RelationEdge

from .conftest import method_doc, problem_doc


def test_problem_knowledge_edge(knowledge_registry) -> None:
    problems = {"P0001": problem_doc(pid="P0001", knowledge=["K0001", "K0002"])}
    snap = build_knowledge_relations(knowledge_registry, problems, {})
    assert RelationEdge("P0001", "knowledge", "K0001") in snap.edges
    assert RelationEdge("P0001", "knowledge", "K0002") in snap.edges


def test_omitted_knowledge_field_produces_no_edge(knowledge_registry) -> None:
    problems = {"P0002": problem_doc(pid="P0002", knowledge=None)}
    snap = build_knowledge_relations(knowledge_registry, problems, {})
    problem_edges = [e for e in snap.edges if e.source_id == "P0002"]
    assert problem_edges == []


def test_knowledge_prerequisites_and_related(knowledge_registry) -> None:
    snap = build_knowledge_relations(knowledge_registry, {}, {})
    assert RelationEdge("K0001", "prerequisites", "K0002") in snap.edges
    assert RelationEdge("K0002", "related", "K0001") in snap.edges


def test_method_knowledge_edge(knowledge_registry) -> None:
    methods = {"M0001": method_doc(mid="M0001", knowledge=["K0001"])}
    snap = build_knowledge_relations(knowledge_registry, {}, methods)
    assert RelationEdge("M0001", "knowledge", "K0001") in snap.edges


def test_duplicate_targets_deduped(knowledge_registry) -> None:
    problems = {"P0001": problem_doc(pid="P0001", knowledge=["K0001", "K0001"])}
    snap = build_knowledge_relations(knowledge_registry, problems, {})
    matches = [e for e in snap.edges if e.source_id == "P0001" and e.target_id == "K0001"]
    assert len(matches) == 1


def test_deterministic_ordering(knowledge_registry) -> None:
    problems = {"P0001": problem_doc(pid="P0001", knowledge=["K0002", "K0001"])}
    snap_a = build_knowledge_relations(knowledge_registry, problems, {})
    snap_b = build_knowledge_relations(knowledge_registry, problems, {})
    assert snap_a == snap_b
    targets = [e.target_id for e in snap_a.edges if e.source_id == "P0001"]
    assert targets == ["K0001", "K0002"]


def test_attempt_not_consumed(knowledge_registry) -> None:
    snap_before = build_knowledge_relations(knowledge_registry, {}, {})
    # Attempt registry is not an input — snapshot unchanged regardless of external evidence.
    snap_after = build_knowledge_relations(knowledge_registry, {}, {})
    assert snap_before == snap_after


def test_empty_registries() -> None:
    snap = build_knowledge_relations({}, {}, {})
    assert snap.edges == ()


def test_body_inference_not_consumed(knowledge_registry) -> None:
    problem = problem_doc(pid="P0001", knowledge=None)
    problem.body = "本题使用 K0009"
    problems = {"P0001": problem}
    snap = build_knowledge_relations(knowledge_registry, problems, {})
    problem_edges = [e for e in snap.edges if e.source_id == "P0001"]
    assert problem_edges == []


def test_registry_insertion_order_irrelevant(knowledge_registry) -> None:
    p1 = problem_doc(pid="P0001", knowledge=["K0001"])
    p2 = problem_doc(pid="P0002", knowledge=["K0002"])
    snap_a = build_knowledge_relations(
        knowledge_registry,
        {"P0002": p2, "P0001": p1},
        {},
    )
    snap_b = build_knowledge_relations(
        knowledge_registry,
        {"P0001": p1, "P0002": p2},
        {},
    )
    assert snap_a == snap_b
