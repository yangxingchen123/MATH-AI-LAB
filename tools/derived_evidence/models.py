"""Data models for Descriptive Evidence State v1 (Derived Contract)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, order=True)
class TargetKey:
    """Derived composite key — not a Source identity."""

    problem_id: str
    part: str | None = None


def empty_outcome_counts() -> dict[str, int]:
    from .constants import OUTCOME_CATEGORIES

    return {name: 0 for name in OUTCOME_CATEGORIES}


def empty_assistance_counts() -> dict[str, int]:
    from .constants import ASSISTANCE_CATEGORIES

    return {name: 0 for name in ASSISTANCE_CATEGORIES}


@dataclass(frozen=True)
class TargetEvidenceState:
    target: TargetKey
    attempt_ids: tuple[str, ...]
    attempt_count: int
    outcome_counts: Mapping[str, int]
    assistance_counts: Mapping[str, int]


@dataclass(frozen=True)
class ProblemEvidenceRollup:
    problem_id: str
    attempt_ids: tuple[str, ...]
    attempt_count: int
    outcome_counts: Mapping[str, int]
    assistance_counts: Mapping[str, int]
    whole_problem_attempt_count: int
    attempted_parts: tuple[str, ...]
    part_attempt_counts: Mapping[str, int]


@dataclass(frozen=True)
class DerivedEvidenceSnapshot:
    target_states: Mapping[TargetKey, TargetEvidenceState] = field(default_factory=dict)
    problem_rollups: Mapping[str, ProblemEvidenceRollup] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeAssociatedEvidenceRollup:
    knowledge_id: str
    associated_attempt_ids: tuple[str, ...]
    associated_attempt_count: int
    associated_outcome_counts: Mapping[str, int]
    associated_assistance_counts: Mapping[str, int]


@dataclass(frozen=True)
class KnowledgeAssociatedEvidenceSnapshot:
    knowledge_rollups: Mapping[str, KnowledgeAssociatedEvidenceRollup] = field(default_factory=dict)
