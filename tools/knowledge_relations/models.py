"""Data models for Formal Knowledge Relation projection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class RelationEdge:
    """Canonical formal relation edge — identity (source_id, relation, target_id)."""

    source_id: str
    relation: str
    target_id: str


@dataclass(frozen=True)
class KnowledgeRelationSnapshot:
    """Immutable derived snapshot of validated formal static relations."""

    edges: tuple[RelationEdge, ...] = ()
