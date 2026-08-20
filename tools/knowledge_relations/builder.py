"""Pure builder for Formal Knowledge Relation projection (P5 v1)."""

from __future__ import annotations

from collections.abc import Mapping

from tools.knowledge_validator.models import KnowledgeDocument
from tools.method_validator.models import MethodDocument
from tools.problem_validator.models import ProblemDocument

from .models import KnowledgeRelationSnapshot, RelationEdge

KNOWLEDGE_RELATIONS: frozenset[str] = frozenset({"prerequisites", "related"})
OBJECT_KNOWLEDGE_RELATION = "knowledge"

_ALLOWED_RELATIONS: frozenset[str] = KNOWLEDGE_RELATIONS | {OBJECT_KNOWLEDGE_RELATION}


class KnowledgeRelationBuildError(Exception):
    """Raised when formal relation invariants cannot be satisfied."""


def _id_prefix(object_id: str) -> str:
    if len(object_id) >= 1:
        return object_id[0]
    return ""


def _list_targets(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _add_edge(
    edges: set[tuple[str, str, str]],
    *,
    source_id: str,
    relation: str,
    target_id: str,
    knowledge_registry: Mapping[str, KnowledgeDocument],
    source_registry: Mapping[str, object],
) -> None:
    if relation not in _ALLOWED_RELATIONS:
        raise KnowledgeRelationBuildError(f"Unsupported relation: {relation!r}")
    if source_id not in source_registry:
        raise KnowledgeRelationBuildError(f"Unknown source ID: {source_id!r}")
    if target_id not in knowledge_registry:
        raise KnowledgeRelationBuildError(f"Unknown Knowledge target: {target_id!r}")

    prefix = _id_prefix(source_id)
    if relation in KNOWLEDGE_RELATIONS and prefix != "K":
        raise KnowledgeRelationBuildError(
            f"Relation {relation!r} requires Knowledge source, got {source_id!r}"
        )
    if relation == OBJECT_KNOWLEDGE_RELATION and prefix not in {"P", "M"}:
        raise KnowledgeRelationBuildError(
            f"Relation knowledge requires Problem/Method source, got {source_id!r}"
        )

    edges.add((source_id, relation, target_id))


def build_knowledge_relations(
    validated_knowledge: Mapping[str, KnowledgeDocument],
    validated_problems: Mapping[str, ProblemDocument],
    validated_methods: Mapping[str, MethodDocument],
) -> KnowledgeRelationSnapshot:
    """Project validated formal static relations into an immutable snapshot."""
    edge_keys: set[tuple[str, str, str]] = set()

    for kid in sorted(validated_knowledge):
        doc = validated_knowledge[kid]
        for target in _list_targets(doc.prerequisites if doc.prerequisites is not None else doc.data.get("prerequisites")):
            _add_edge(
                edge_keys,
                source_id=kid,
                relation="prerequisites",
                target_id=target,
                knowledge_registry=validated_knowledge,
                source_registry=validated_knowledge,
            )
        for target in _list_targets(doc.related if doc.related is not None else doc.data.get("related")):
            _add_edge(
                edge_keys,
                source_id=kid,
                relation="related",
                target_id=target,
                knowledge_registry=validated_knowledge,
                source_registry=validated_knowledge,
            )

    for pid in sorted(validated_problems):
        doc = validated_problems[pid]
        if "knowledge" not in doc.data:
            continue
        for target in _list_targets(doc.knowledge):
            _add_edge(
                edge_keys,
                source_id=pid,
                relation=OBJECT_KNOWLEDGE_RELATION,
                target_id=target,
                knowledge_registry=validated_knowledge,
                source_registry=validated_problems,
            )

    for mid in sorted(validated_methods):
        doc = validated_methods[mid]
        if "knowledge" not in doc.data:
            continue
        for target in _list_targets(doc.knowledge):
            _add_edge(
                edge_keys,
                source_id=mid,
                relation=OBJECT_KNOWLEDGE_RELATION,
                target_id=target,
                knowledge_registry=validated_knowledge,
                source_registry=validated_methods,
            )

    ordered = tuple(
        RelationEdge(source_id=s, relation=r, target_id=t)
        for s, r, t in sorted(edge_keys)
    )
    return KnowledgeRelationSnapshot(edges=ordered)
