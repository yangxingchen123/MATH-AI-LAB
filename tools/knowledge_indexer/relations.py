"""Derived relation computation (required_by, related_effective)."""

from __future__ import annotations

from tools.knowledge_validator.models import KnowledgeDocument


def declared_prerequisites(doc: KnowledgeDocument) -> list[str]:
    return list(doc.prerequisites) if doc.prerequisites is not None else []


def declared_related(doc: KnowledgeDocument) -> list[str]:
    return list(doc.related) if doc.related is not None else []


def compute_required_by(
    registry: dict[str, KnowledgeDocument],
) -> dict[str, list[str]]:
    """
    If A.prerequisites contains B, then B.required_by contains A.
    Returns map: target_id -> sorted list of source IDs.
    """
    required_by: dict[str, set[str]] = {kid: set() for kid in registry}
    for source_id, doc in registry.items():
        for target in declared_prerequisites(doc):
            if target in required_by:
                required_by[target].add(source_id)
    return {kid: sorted(vals) for kid, vals in sorted(required_by.items())}


def compute_related_effective(
    registry: dict[str, KnowledgeDocument],
) -> dict[str, list[str]]:
    """
    Symmetric closure of related edges, deduplicated, sorted.
    Does not mutate source documents.
    """
    effective: dict[str, set[str]] = {kid: set() for kid in registry}
    for source_id, doc in registry.items():
        for target in declared_related(doc):
            if target not in registry:
                continue
            if target == source_id:
                continue
            effective[source_id].add(target)
            effective[target].add(source_id)
    return {kid: sorted(vals) for kid, vals in sorted(effective.items())}


def count_related_effective_undirected(
    related_effective: dict[str, list[str]],
) -> int:
    """Count undirected pairs once."""
    seen: set[tuple[str, str]] = set()
    for a, targets in related_effective.items():
        for b in targets:
            pair = (a, b) if a < b else (b, a)
            seen.add(pair)
    return len(seen)


def count_prerequisite_edges(registry: dict[str, KnowledgeDocument]) -> int:
    return sum(len(declared_prerequisites(doc)) for doc in registry.values())


def count_related_declared_edges(registry: dict[str, KnowledgeDocument]) -> int:
    return sum(len(declared_related(doc)) for doc in registry.values())
