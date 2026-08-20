"""Prerequisite DAG validation (related cycles are intentionally not checked)."""

from __future__ import annotations

from typing import Mapping

from .models import KnowledgeDocument, Severity, ValidationIssue


def find_prerequisite_cycles(
    registry: Mapping[str, KnowledgeDocument],
) -> list[ValidationIssue]:
    """
    Detect directed cycles in the prerequisites graph.

    Edge direction: source -> prerequisite.
    """
    graph: dict[str, list[str]] = {}
    for kid, doc in registry.items():
        if doc.prerequisites is None:
            graph[kid] = []
            continue
        # Keep only targets that exist in registry (dangling handled elsewhere)
        graph[kid] = [t for t in doc.prerequisites if t in registry and t != kid]

    # Ensure all nodes appear
    for kid in registry:
        graph.setdefault(kid, [])

    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {n: WHITE for n in graph}
    parent: dict[str, str | None] = {n: None for n in graph}
    cycles: list[list[str]] = []

    def dfs(u: str) -> None:
        color[u] = GRAY
        for v in sorted(graph[u]):  # stable neighbor order
            if color[v] == WHITE:
                parent[v] = u
                dfs(v)
            elif color[v] == GRAY:
                # reconstruct cycle u -> ... -> v -> u? Actually edge u->v where v is on stack
                cycle = [v]
                cur = u
                while cur != v and cur is not None:
                    cycle.append(cur)
                    cur = parent[cur]
                cycle.append(v)
                cycle.reverse()
                # cycle is v -> ... -> u -> v
                cycles.append(cycle)
        color[u] = BLACK

    for node in sorted(graph.keys()):
        if color[node] == WHITE:
            dfs(node)

    # Deduplicate cycles by normalized rotation
    unique_cycles: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for cycle in cycles:
        if len(cycle) < 2:
            continue
        body = cycle[:-1]  # drop repeated end
        # normalize by rotating to lexicographically smallest node
        if not body:
            continue
        min_i = min(range(len(body)), key=lambda i: body[i])
        rotated = body[min_i:] + body[:min_i]
        key = tuple(rotated)
        if key not in seen:
            seen.add(key)
            unique_cycles.append(list(rotated) + [rotated[0]])

    issues: list[ValidationIssue] = []
    for cycle in sorted(unique_cycles, key=lambda c: " -> ".join(c)):
        path = " -> ".join(cycle)
        # Attach issue to first node in cycle for reporting stability
        first = cycle[0]
        first_doc = registry[first]
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                rule_id="K-GRAPH-001",
                message=f"prerequisite cycle detected: {path}",
                file=first_doc.relative_path,
                object_id=first,
                field="prerequisites",
                details={"cycle": cycle, "cycle_path": path},
            )
        )
    return issues
