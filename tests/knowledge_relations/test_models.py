"""Tests for knowledge relation models."""

from __future__ import annotations

from tools.knowledge_relations.models import KnowledgeRelationSnapshot, RelationEdge


def test_relation_edge_identity() -> None:
    edge = RelationEdge(source_id="P0001", relation="knowledge", target_id="K0001")
    assert edge.source_id == "P0001"
    assert edge.relation == "knowledge"
    assert edge.target_id == "K0001"


def test_relation_edge_ordering() -> None:
    a = RelationEdge("P0001", "knowledge", "K0002")
    b = RelationEdge("P0001", "knowledge", "K0001")
    assert b < a


def test_snapshot_immutable_edges() -> None:
    snap = KnowledgeRelationSnapshot(
        edges=(
            RelationEdge("K0001", "prerequisites", "K0002"),
        )
    )
    assert len(snap.edges) == 1
