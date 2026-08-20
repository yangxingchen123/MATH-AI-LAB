"""Descriptive Evidence State v1 — pure derived computation (not Source)."""

from __future__ import annotations

from .builder import (
    DerivedEvidenceBuildError,
    build_derived_evidence,
    build_derived_evidence_from_validation_results,
)
from .knowledge_projection import build_knowledge_associated_evidence
from .models import (
    DerivedEvidenceSnapshot,
    KnowledgeAssociatedEvidenceRollup,
    KnowledgeAssociatedEvidenceSnapshot,
    ProblemEvidenceRollup,
    TargetEvidenceState,
    TargetKey,
)

__all__ = [
    "DerivedEvidenceBuildError",
    "DerivedEvidenceSnapshot",
    "KnowledgeAssociatedEvidenceRollup",
    "KnowledgeAssociatedEvidenceSnapshot",
    "ProblemEvidenceRollup",
    "TargetEvidenceState",
    "TargetKey",
    "build_derived_evidence",
    "build_derived_evidence_from_validation_results",
    "build_knowledge_associated_evidence",
]
