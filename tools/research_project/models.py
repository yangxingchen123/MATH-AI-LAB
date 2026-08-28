"""Domain result and record types for research projects.

Never reuse tools.normal_operation result types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ResearchProjectOperationKind(str, Enum):
    WRITTEN = "WRITTEN"
    NO_OP = "NO_OP"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ResearchProjectOperationResult:
    kind: ResearchProjectOperationKind
    message: str
    project: Path | None = None
    touched_paths: tuple[Path, ...] = ()


@dataclass(frozen=True)
class ResearchProjectValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResearchProjectStatusResult:
    project: Path
    freshness: str
    reconcile_required: bool
    contract_version: str
    external_processing: str
    message: str = ""


@dataclass(frozen=True)
class ExternalProcessingAssessment:
    verdict: str
    reason_codes: tuple[str, ...] = ()
    message: str = ""


@dataclass(frozen=True)
class LocalRef:
    prefix: str
    number: int
    text: str


@dataclass
class ResearchRecord:
    type: str
    ref: str
    metadata: dict[str, str]
    body: str
    raw: str = ""


@dataclass
class AssumptionRecord:
    ref: str
    status: str
    scope: str
    rationale: str
    falsifiable_when: str
    body: str
    impacts: list[str] = field(default_factory=list)
    supersedes: str | None = None
    superseded_by: str | None = None
    reviewed: str | None = None
    record: ResearchRecord | None = None


@dataclass
class ClaimRecord:
    ref: str
    status: str
    body: str
    evidence_refs: list[str] = field(default_factory=list)
    core: str | None = None
    record: ResearchRecord | None = None


@dataclass
class EvidenceRecord:
    ref: str
    claim_ref: str
    polarity: str
    kind: str
    body: str
    source_citation: str | None = None
    source_sha256: str | None = None
    literature_ref: str | None = None
    acknowledges_status: str | None = None
    record: ResearchRecord | None = None


@dataclass
class DecisionRecord:
    ref: str
    date: str
    question: str
    options: str
    choice: str
    basis: str
    cost: str
    reversible: str
    revisit_when: str
    body: str
    opposes: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    supersedes: str | None = None
    record: ResearchRecord | None = None


@dataclass
class NegativeResultRecord:
    ref: str
    status: str
    failed_route: str
    failure_evidence_refs: list[str]
    impact: str
    retry_when: str
    body: str
    related_claims: list[str] = field(default_factory=list)
    related_decisions: list[str] = field(default_factory=list)
    record: ResearchRecord | None = None


@dataclass
class GovernanceRecord:
    ref: str
    project_data_level: str
    external_processing_authorized: str
    license_status: str
    body: str
    notes: str | None = None
    record: ResearchRecord | None = None


@dataclass
class AiContributionRecord:
    ref: str
    date: str
    role: str
    summary: str
    human_review: str
    body: str
    tools: str | None = None
    record: ResearchRecord | None = None


@dataclass
class LiteratureRecord:
    ref: str
    title: str
    authors: str
    year: str
    identity_kind: str
    publication_status: str
    body: str
    doi: str | None = None
    isbn: str | None = None
    arxiv: str | None = None
    venue: str | None = None
    version: str | None = None
    url: str | None = None
    accessed_at: str | None = None
    source_sha256: str | None = None
    license_status: str | None = None
    supersedes: str | None = None
    notes: str | None = None
    record: ResearchRecord | None = None


@dataclass
class NoveltyRecord:
    ref: str
    dimension: str
    existing_work: str
    current_work: str
    addition_evidence_refs: list[str]
    body: str
    notes: str | None = None
    record: ResearchRecord | None = None


@dataclass
class ReviewRecord:
    ref: str
    role: str
    severity: str
    status: str
    target_ref: str
    body: str
    disposition: str | None = None
    waiver_reason: str | None = None
    record: ResearchRecord | None = None


@dataclass
class ProjectDocumentSet:
    assumptions: list[AssumptionRecord] = field(default_factory=list)
    claims: list[ClaimRecord] = field(default_factory=list)
    evidence: list[EvidenceRecord] = field(default_factory=list)
    decisions: list[DecisionRecord] = field(default_factory=list)
    negative_results: list[NegativeResultRecord] = field(default_factory=list)
    governance: GovernanceRecord | None = None
    ai_contributions: list[AiContributionRecord] = field(default_factory=list)
    literature: list[LiteratureRecord] = field(default_factory=list)
    novelty: list[NoveltyRecord] = field(default_factory=list)
    reviews: list[ReviewRecord] = field(default_factory=list)
    preambles: dict[str, str] = field(default_factory=dict)
    dossier_text: str = ""
    records_by_file: dict[str, list[ResearchRecord]] = field(default_factory=dict)


@dataclass(frozen=True)
class ProjectContract:
    contract_version: str
    required_files: tuple[str, ...]
    required_dirs: tuple[str, ...]
    template_root: Path
