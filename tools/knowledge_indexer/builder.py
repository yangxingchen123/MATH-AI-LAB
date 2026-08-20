"""Build KnowledgeIndexModel from a validated Knowledge registry."""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from typing import Any

from tools.knowledge_validator.models import KnowledgeDocument

from .models import KnowledgeIndexEntry, KnowledgeIndexModel
from .relations import (
    compute_related_effective,
    compute_required_by,
    count_prerequisite_edges,
    count_related_declared_edges,
    count_related_effective_undirected,
    declared_prerequisites,
    declared_related,
)


def _iso_date(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return str(value)


def _field_or_null(doc: KnowledgeDocument, key: str, computed: Any) -> Any:
    """Preserve null vs []: omitted keys stay None even if computed is empty list."""
    if key not in doc.data:
        return None
    return computed


def _canonical_source_payload(registry: dict[str, KnowledgeDocument]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for kid in sorted(registry.keys()):
        doc = registry[kid]
        # Only path + YAML metadata keys that affect the index
        meta: dict[str, Any] = {}
        for key in (
            "schema_version",
            "id",
            "type",
            "title",
            "aliases",
            "status",
            "created",
            "updated",
            "domain",
            "prerequisites",
            "related",
        ):
            if key not in doc.data:
                meta[key] = None
            else:
                val = doc.data[key]
                if isinstance(val, date) and not isinstance(val, datetime):
                    meta[key] = val.isoformat()
                elif isinstance(val, datetime):
                    meta[key] = val.date().isoformat()
                else:
                    meta[key] = val
        rows.append({"path": doc.relative_path.replace("\\", "/"), "metadata": meta})
    return rows


def compute_source_metadata_sha256(registry: dict[str, KnowledgeDocument]) -> str:
    payload = _canonical_source_payload(registry)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_index_model(registry: dict[str, KnowledgeDocument]) -> KnowledgeIndexModel:
    required_by = compute_required_by(registry)
    related_effective = compute_related_effective(registry)

    entries: dict[str, KnowledgeIndexEntry] = {}
    status_counts = {"draft": 0, "reviewed": 0, "archived": 0}
    domains: dict[str, list[str]] = {}
    without_domain: list[str] = []

    for kid in sorted(registry.keys()):
        doc = registry[kid]
        status = doc.status or str(doc.data.get("status") or "")
        if status in status_counts:
            status_counts[status] += 1

        aliases = _field_or_null(
            doc, "aliases", list(doc.aliases) if doc.aliases is not None else []
        )
        domain = _field_or_null(doc, "domain", doc.domain)
        prereqs = _field_or_null(doc, "prerequisites", declared_prerequisites(doc))
        related = _field_or_null(doc, "related", declared_related(doc))

        title = doc.data.get("title")
        if not isinstance(title, str):
            title = kid

        entry = KnowledgeIndexEntry(
            object_id=kid,
            path=doc.relative_path.replace("\\", "/"),
            schema_version=doc.data.get("schema_version") if "schema_version" in doc.data else None,
            type_value=doc.data.get("type") if "type" in doc.data else None,
            title=title,
            aliases=aliases if aliases is None else list(aliases),
            status=status,
            created=_iso_date(doc.created) if doc.created is not None else (
                _iso_date(doc.data.get("created")) if "created" in doc.data else None
            ),
            updated=_iso_date(doc.updated) if doc.updated is not None else (
                _iso_date(doc.data.get("updated")) if "updated" in doc.data else None
            ),
            domain=domain if domain is None else str(domain),
            prerequisites=prereqs if prereqs is None else list(prereqs),
            related=related if related is None else list(related),
            required_by=list(required_by.get(kid, [])),
            related_effective=list(related_effective.get(kid, [])),
        )
        entries[kid] = entry

        if domain is None or (isinstance(domain, str) and domain.strip() == ""):
            without_domain.append(kid)
        else:
            domains.setdefault(str(domain), []).append(kid)

    for d in list(domains.keys()):
        domains[d] = sorted(domains[d])
    domains = {k: domains[k] for k in sorted(domains.keys())}
    without_domain = sorted(without_domain)

    return KnowledgeIndexModel(
        entries=entries,
        domains=domains,
        without_domain=without_domain,
        status_counts=status_counts,
        prerequisite_edges=count_prerequisite_edges(registry),
        related_declared_edges=count_related_declared_edges(registry),
        related_effective_edges=count_related_effective_undirected(related_effective),
        source_metadata_sha256=compute_source_metadata_sha256(registry),
    )
