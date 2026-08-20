"""Data models for Workspace Indexer v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from tools.derived_evidence.models import DerivedEvidenceSnapshot, KnowledgeAssociatedEvidenceSnapshot
from tools.knowledge_relations.models import KnowledgeRelationSnapshot


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
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeIndexRow:
    object_id: str
    title: str
    status: str
    domain: str
    source_path: str


@dataclass
class ProblemIndexRow:
    object_id: str
    title: str
    yaml_status: str
    operational_workflow: str
    parts: str
    attempt_count: int
    source_path: str


@dataclass
class OutputIndexRow:
    relative_path: str
    kind: str
    filename: str


@dataclass
class AttemptIndexRow:
    object_id: str
    problem_id: str
    target: str
    outcome: str
    assistance: str
    attempted_at: str
    source_path: str


@dataclass
class MethodIndexRow:
    object_id: str
    title: str
    status: str
    knowledge: str
    source_path: str


@dataclass
class WorkspaceSnapshot:
    project_root: Path
    knowledge_rows: list[KnowledgeIndexRow] = field(default_factory=list)
    problem_rows: list[ProblemIndexRow] = field(default_factory=list)
    attempt_rows: list[AttemptIndexRow] = field(default_factory=list)
    method_rows: list[MethodIndexRow] = field(default_factory=list)
    output_rows: list[OutputIndexRow] = field(default_factory=list)
    knowledge_status_counts: dict[str, int] = field(default_factory=dict)
    problem_yaml_status_counts: dict[str, int] = field(default_factory=dict)
    problem_workflow_counts: dict[str, int] = field(default_factory=dict)
    problem_attempt_counts: dict[str, int] = field(default_factory=dict)
    attempt_outcome_counts: dict[str, int] = field(default_factory=dict)
    attempt_assistance_counts: dict[str, int] = field(default_factory=dict)
    method_status_counts: dict[str, int] = field(default_factory=dict)
    latex_project_count: int = 0
    pdf_count: int = 0
    image_count: int = 0
    derived_evidence: DerivedEvidenceSnapshot | None = None
    knowledge_associated_evidence: KnowledgeAssociatedEvidenceSnapshot | None = None
    knowledge_relations: KnowledgeRelationSnapshot | None = None


@dataclass
class RenderedWorkspaceIndex:
    files: dict[str, str]


@dataclass
class IndexOperationResult:
    result: IndexResultKind
    project_root: str
    index_dir: str
    knowledge_validator_result: str = "UNKNOWN"
    problem_validator_result: str = "UNKNOWN"
    attempt_validator_result: str = "UNKNOWN"
    method_validator_result: str = "UNKNOWN"
    knowledge_errors: int = 0
    problem_errors: int = 0
    attempt_errors: int = 0
    method_errors: int = 0
    issues: list[IndexerIssue] = field(default_factory=list)
