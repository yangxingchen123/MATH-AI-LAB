"""Internal models for Knowledge Indexer."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from enum import Enum
from typing import Any

from tools.knowledge_validator.models import ValidationIssue


class IndexResultKind(str, Enum):
    BUILT = "BUILT"
    UP_TO_DATE = "UP_TO_DATE"
    CURRENT = "CURRENT"
    STALE = "STALE"
    MISSING = "MISSING"
    FAIL = "FAIL"


@dataclass(frozen=True)
class IndexerIssue:
    severity: str
    rule_id: str
    message: str
    details: dict[str, Any] = dc_field(default_factory=dict)


@dataclass
class KnowledgeIndexEntry:
    object_id: str
    path: str  # relative to project root, posix
    # metadata: declared fields; omitted optional fields use None (null)
    schema_version: int | None
    type_value: str | None
    title: str
    aliases: list[str] | None
    status: str
    created: str | None
    updated: str | None
    domain: str | None
    prerequisites: list[str] | None
    related: list[str] | None
    # derived
    required_by: list[str] = dc_field(default_factory=list)
    related_effective: list[str] = dc_field(default_factory=list)

    def metadata_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.object_id,
            "type": self.type_value,
            "title": self.title,
            "aliases": self.aliases,
            "status": self.status,
            "created": self.created,
            "updated": self.updated,
            "domain": self.domain,
            "prerequisites": self.prerequisites,
            "related": self.related,
        }

    def derived_dict(self) -> dict[str, Any]:
        return {
            "required_by": list(self.required_by),
            "related_effective": list(self.related_effective),
        }


@dataclass
class KnowledgeIndexModel:
    entries: dict[str, KnowledgeIndexEntry]
    domains: dict[str, list[str]]  # domain -> sorted IDs
    without_domain: list[str]
    status_counts: dict[str, int]
    prerequisite_edges: int
    related_declared_edges: int
    related_effective_edges: int
    source_metadata_sha256: str

    @property
    def knowledge_objects(self) -> int:
        return len(self.entries)


@dataclass
class RenderedIndex:
    """In-memory snapshot of the four managed index files."""

    files: dict[str, str]  # filename -> text (UTF-8)

    def bytes_map(self) -> dict[str, bytes]:
        return {name: text.encode("utf-8") for name, text in sorted(self.files.items())}


@dataclass
class IndexOperationResult:
    result: IndexResultKind
    project_root: str
    index_dir: str
    model: KnowledgeIndexModel | None = None
    validator_errors: int = 0
    validator_warnings: int = 0
    validator_result: str = "PASS"
    validator_issues: list[ValidationIssue] = dc_field(default_factory=list)
    issues: list[IndexerIssue] = dc_field(default_factory=list)
    knowledge_objects: int = 0
    domains: int = 0
    prerequisite_edges: int = 0
    related_declared_edges: int = 0
    related_effective_edges: int = 0
