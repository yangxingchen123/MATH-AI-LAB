"""Deterministic JSON renderer for knowledge_index.json."""

from __future__ import annotations

import json
from typing import Any

from .constants import INDEX_VERSION, INDEXER_NAME, INDEXER_VERSION
from .models import KnowledgeIndexModel


def model_to_json_dict(model: KnowledgeIndexModel) -> dict[str, Any]:
    knowledge: dict[str, Any] = {}
    for kid in sorted(model.entries.keys()):
        entry = model.entries[kid]
        knowledge[kid] = {
            "path": entry.path,
            "metadata": entry.metadata_dict(),
            "derived": entry.derived_dict(),
        }

    return {
        "index_version": INDEX_VERSION,
        "indexer": {
            "name": INDEXER_NAME,
            "version": INDEXER_VERSION,
        },
        "schema": {
            "object_type": "knowledge",
            "schema_version": 1,
            "status": "frozen",
        },
        "source_metadata_sha256": model.source_metadata_sha256,
        "summary": {
            "knowledge_objects": model.knowledge_objects,
            "status_counts": {
                "draft": model.status_counts.get("draft", 0),
                "reviewed": model.status_counts.get("reviewed", 0),
                "archived": model.status_counts.get("archived", 0),
            },
            "domain_count": len(model.domains),
            "prerequisite_edges": model.prerequisite_edges,
            "related_declared_edges": model.related_declared_edges,
            "related_effective_edges": model.related_effective_edges,
        },
        "knowledge": knowledge,
        "domains": model.domains,
        "without_domain": list(model.without_domain),
    }


def render_json(model: KnowledgeIndexModel) -> str:
    payload = model_to_json_dict(model)
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
