"""Lemma dependency graph from correspondence. Acyclic; not a LeanBlueprint site."""

from __future__ import annotations

from collections import defaultdict, deque

import yaml

from .constants import CORRESPONDENCE_PATH


def lemma_graph(path=None) -> dict:
    data = yaml.safe_load((path or CORRESPONDENCE_PATH).read_text(encoding="utf-8")) or {}
    theorems = [item for item in (data.get("theorems") or []) if isinstance(item, dict) and item.get("id")]
    nodes = [str(item["id"]) for item in theorems]
    edges: list[tuple[str, str]] = []
    by_file: dict[str, list[str]] = defaultdict(list)
    for item in theorems:
        ident = str(item["id"])
        for dep in item.get("depends_on") or []:
            edges.append((str(dep), ident))
        by_file[str(item.get("lean_file") or "")].append(ident)
    for _file, ids in by_file.items():
        for left, right in zip(ids, ids[1:]):
            edges.append((left, right))
    cyclic = _has_cycle(nodes, edges)
    return {
        "ok": not cyclic and bool(nodes),
        "nodes": nodes,
        "edges": [{"from": a, "to": b} for a, b in edges],
        "acyclic": not cyclic,
        "writes_source": False,
        "blueprint_site": False,
        "note": "File order and optional depends_on. Not a LeanBlueprint website.",
    }


def _has_cycle(nodes: list[str], edges: list[tuple[str, str]]) -> bool:
    indeg = {node: 0 for node in nodes}
    adj: dict[str, list[str]] = defaultdict(list)
    for src, dst in edges:
        if src not in indeg or dst not in indeg:
            continue
        adj[src].append(dst)
        indeg[dst] += 1
    queue = deque([node for node, deg in indeg.items() if deg == 0])
    seen = 0
    while queue:
        node = queue.popleft()
        seen += 1
        for nxt in adj[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)
    return seen != len(nodes)


def reasoning_graph(path=None) -> dict:
    """depends_on only. File order is not a reasoning edge. Never a theorem."""
    data = yaml.safe_load((path or CORRESPONDENCE_PATH).read_text(encoding="utf-8")) or {}
    theorems = [item for item in (data.get("theorems") or []) if isinstance(item, dict) and item.get("id")]
    known = {str(item["id"]) for item in theorems}
    depended: set[str] = set()
    for item in theorems:
        for dep in item.get("depends_on") or []:
            if str(dep) in known:
                depended.add(str(dep))
    nodes: list[dict] = []
    edges: list[dict] = []
    for item in theorems:
        ident = str(item["id"])
        deps = [str(dep) for dep in (item.get("depends_on") or []) if str(dep) in known and str(dep) != ident]
        if not deps:
            kind = "premise"
        elif ident in depended:
            kind = "intermediate"
        else:
            kind = "conclusion"
        nodes.append(
            {
                "id": ident,
                "kind": kind,
                "content": str(item.get("natural_language") or ident),
            }
        )
        for dep in deps:
            edges.append(
                {
                    "id": f"requires:{ident}:{dep}",
                    "type": "requires",
                    "source": ident,
                    "target": dep,
                }
            )
    return {
        "nodes": nodes,
        "edges": edges,
        "proves_theorem": False,
        "file_order_excluded": True,
        "not_a_theorem": True,
        "writes_source": False,
        "note": "Declared depends_on only. File adjacency is not a reasoning edge.",
    }
