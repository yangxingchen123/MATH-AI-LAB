"""Real repository projection test for knowledge relations."""

from __future__ import annotations

from pathlib import Path

from tools.attempt_validator import validate_project as validate_attempt_project
from tools.knowledge_relations import build_knowledge_relations
from tools.knowledge_relations.models import RelationEdge
from tools.knowledge_validator import validate_project as validate_knowledge_project
from tools.method_validator import validate_project as validate_method_project
from tools.problem_validator import validate_project as validate_problem_project


def test_real_repo_formal_relations() -> None:
    root = Path(__file__).resolve().parents[2]
    kr = validate_knowledge_project(root=root)
    pr = validate_problem_project(root=root, knowledge_result=kr)
    validate_attempt_project(root=root, problem_result=pr)
    mr = validate_method_project(root=root, knowledge_result=kr)

    assert kr.summary.errors == 0
    assert pr.summary.errors == 0
    assert mr.summary.errors == 0

    knowledge_registry = {d.object_id: d for d in kr.documents if d.object_id}
    problem_registry = {d.object_id: d for d in pr.documents if d.object_id}
    method_registry = {d.object_id: d for d in mr.documents if d.object_id}

    snap = build_knowledge_relations(
        knowledge_registry,
        problem_registry,
        method_registry,
    )

    assert RelationEdge("K0001", "prerequisites", "K0002") in snap.edges
    assert RelationEdge("P0001", "knowledge", "K0001") in snap.edges
    assert RelationEdge("P0001", "knowledge", "K0002") in snap.edges
    assert RelationEdge("M0001", "knowledge", "K0001") in snap.edges
    assert len(snap.edges) == 4
