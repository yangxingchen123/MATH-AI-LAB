"""Knowledge Associated Evidence Projection v1 — pure derived computation."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping

from tools.attempt_validator.models import AttemptDocument
from tools.knowledge_validator.models import KnowledgeDocument
from tools.problem_validator.models import ProblemDocument

from .builder import DerivedEvidenceBuildError, _assistance_bucket, _increment_counts
from .constants import ASSISTANCE_CATEGORIES, OUTCOME_CATEGORIES
from .models import (
    DerivedEvidenceSnapshot,
    KnowledgeAssociatedEvidenceRollup,
    KnowledgeAssociatedEvidenceSnapshot,
    empty_assistance_counts,
    empty_outcome_counts,
)


def _problem_knowledge_ids(problem: ProblemDocument) -> list[str] | None:
    if "knowledge" not in problem.data:
        return None
    knowledge = problem.data["knowledge"]
    if not isinstance(knowledge, list) or len(knowledge) == 0:
        return None
    return [str(k) for k in knowledge]


def _dedupe_preserve_order(ids: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in ids:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def build_knowledge_associated_evidence(
    validated_knowledge: Mapping[str, KnowledgeDocument],
    validated_problems: Mapping[str, ProblemDocument],
    validated_attempts: Mapping[str, AttemptDocument],
    derived_snapshot: DerivedEvidenceSnapshot,
) -> KnowledgeAssociatedEvidenceSnapshot:
    """Project whole-target Attempt evidence to Knowledge via formal P.knowledge only."""

    pending: dict[str, set[str]] = defaultdict(set)

    for state in derived_snapshot.target_states.values():
        if state.target.part is not None:
            continue

        problem_id = state.target.problem_id
        problem = validated_problems.get(problem_id)
        if problem is None:
            raise DerivedEvidenceBuildError(
                f"Whole-target state references unknown Problem {problem_id!r}"
            )

        knowledge_ids = _problem_knowledge_ids(problem)
        if knowledge_ids is None:
            continue

        unique_kids = _dedupe_preserve_order(knowledge_ids)
        for kid in unique_kids:
            if kid not in validated_knowledge:
                raise DerivedEvidenceBuildError(
                    f"Problem {problem_id} references unknown Knowledge {kid!r}"
                )
            for aid in state.attempt_ids:
                if aid not in validated_attempts:
                    raise DerivedEvidenceBuildError(
                        f"Target state references unknown Attempt {aid!r}"
                    )
                pending[kid].add(aid)

    rollups: dict[str, KnowledgeAssociatedEvidenceRollup] = {}
    for kid in sorted(pending):
        attempt_ids = sorted(pending[kid])
        outcome = empty_outcome_counts()
        assistance = empty_assistance_counts()
        for aid in attempt_ids:
            doc = validated_attempts[aid]
            if "part" in doc.data:
                raise DerivedEvidenceBuildError(
                    f"Attempt {aid} associated to {kid} is not whole-target"
                )
            outcome_key = str(doc.outcome or "")
            assistance_key = _assistance_bucket(doc)
            _increment_counts(outcome, outcome_key, OUTCOME_CATEGORIES)
            _increment_counts(assistance, assistance_key, ASSISTANCE_CATEGORIES)

        count = len(attempt_ids)
        if sum(outcome.values()) != count or sum(assistance.values()) != count:
            raise DerivedEvidenceBuildError(f"Invariant violation for Knowledge {kid!r}")

        rollups[kid] = KnowledgeAssociatedEvidenceRollup(
            knowledge_id=kid,
            associated_attempt_ids=tuple(attempt_ids),
            associated_attempt_count=count,
            associated_outcome_counts=dict(outcome),
            associated_assistance_counts=dict(assistance),
        )

    return KnowledgeAssociatedEvidenceSnapshot(knowledge_rollups=rollups)
