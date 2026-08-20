"""Pure builder for Descriptive Evidence State v1."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping

from tools.attempt_validator.models import AttemptDocument
from tools.problem_validator.models import ProblemDocument

from .constants import ASSISTANCE_CATEGORIES, OUTCOME_CATEGORIES
from .models import (
    DerivedEvidenceSnapshot,
    ProblemEvidenceRollup,
    TargetEvidenceState,
    TargetKey,
    empty_assistance_counts,
    empty_outcome_counts,
)


class DerivedEvidenceBuildError(Exception):
    """Raised when derived evidence invariants cannot be satisfied."""


def _problem_registry_from_documents(documents: list[ProblemDocument]) -> dict[str, ProblemDocument]:
    registry: dict[str, ProblemDocument] = {}
    for doc in sorted(documents, key=lambda d: d.relative_path):
        if doc.object_id and doc.object_id not in registry:
            registry[doc.object_id] = doc
    return registry


def _attempt_target_key(doc: AttemptDocument) -> TargetKey:
    problem_id = str(doc.problem or "")
    if "part" not in doc.data:
        return TargetKey(problem_id=problem_id, part=None)
    part = doc.data["part"]
    return TargetKey(problem_id=problem_id, part=str(part).strip())


def _assistance_bucket(doc: AttemptDocument) -> str:
    if "assistance" not in doc.data:
        return "omitted"
    return str(doc.data["assistance"])


def _increment_counts(counts: dict[str, int], key: str, allowed: tuple[str, ...]) -> None:
    if key not in allowed:
        raise DerivedEvidenceBuildError(f"Unexpected category: {key!r}")
    counts[key] += 1


def _build_target_states(
    validated_attempts: Mapping[str, AttemptDocument],
) -> dict[TargetKey, TargetEvidenceState]:
    groups: dict[TargetKey, list[str]] = defaultdict(list)
    outcome_by_target: dict[TargetKey, dict[str, int]] = defaultdict(empty_outcome_counts)
    assistance_by_target: dict[TargetKey, dict[str, int]] = defaultdict(empty_assistance_counts)

    for aid in sorted(validated_attempts):
        doc = validated_attempts[aid]
        if not doc.object_id:
            continue
        target = _attempt_target_key(doc)
        if aid in groups[target]:
            raise DerivedEvidenceBuildError(f"Duplicate Attempt ID in target group: {aid}")
        groups[target].append(aid)

        outcome = str(doc.outcome or "")
        assistance = _assistance_bucket(doc)
        _increment_counts(outcome_by_target[target], outcome, OUTCOME_CATEGORIES)
        _increment_counts(assistance_by_target[target], assistance, ASSISTANCE_CATEGORIES)

    states: dict[TargetKey, TargetEvidenceState] = {}
    for target in sorted(groups, key=lambda k: (k.problem_id, k.part is not None, k.part or "")):
        attempt_ids = sorted(groups[target])
        oc = outcome_by_target[target]
        ac = assistance_by_target[target]
        if sum(oc.values()) != len(attempt_ids) or sum(ac.values()) != len(attempt_ids):
            raise DerivedEvidenceBuildError(f"Invariant violation for target {target!r}")
        states[target] = TargetEvidenceState(
            target=target,
            attempt_ids=tuple(attempt_ids),
            attempt_count=len(attempt_ids),
            outcome_counts=dict(oc),
            assistance_counts=dict(ac),
        )
    return states


def _declared_parts(problem: ProblemDocument | None) -> list[str]:
    if problem is None:
        return []
    parts_val = problem.parts
    if isinstance(parts_val, list):
        return [str(p) for p in parts_val]
    return []


def _ordered_attempted_parts(
    observed: set[str],
    declared: list[str],
) -> tuple[str, ...]:
    if declared:
        return tuple(p for p in declared if p in observed)
    return tuple(sorted(observed))


def _ordered_part_counts(
    counts: dict[str, int],
    declared: list[str],
) -> dict[str, int]:
    if declared:
        return {p: counts[p] for p in declared if p in counts}
    return {p: counts[p] for p in sorted(counts)}


def _build_problem_rollups(
    target_states: Mapping[TargetKey, TargetEvidenceState],
    validated_problems: Mapping[str, ProblemDocument],
) -> dict[str, ProblemEvidenceRollup]:
    by_problem: dict[str, list[TargetEvidenceState]] = defaultdict(list)
    for state in target_states.values():
        by_problem[state.target.problem_id].append(state)

    rollups: dict[str, ProblemEvidenceRollup] = {}
    for problem_id in sorted(by_problem):
        states = by_problem[problem_id]
        attempt_id_set: set[str] = set()
        outcome = empty_outcome_counts()
        assistance = empty_assistance_counts()
        whole_count = 0
        part_counts: dict[str, int] = {}

        for state in states:
            for aid in state.attempt_ids:
                if aid in attempt_id_set:
                    raise DerivedEvidenceBuildError(
                        f"Attempt {aid} counted twice in Problem rollup {problem_id}"
                    )
                attempt_id_set.add(aid)
            for key, value in state.outcome_counts.items():
                outcome[key] += value
            for key, value in state.assistance_counts.items():
                assistance[key] += value
            if state.target.part is None:
                whole_count += state.attempt_count
            else:
                part_counts[state.target.part] = state.attempt_count

        attempt_ids = tuple(sorted(attempt_id_set))
        count = len(attempt_ids)
        if sum(outcome.values()) != count or sum(assistance.values()) != count:
            raise DerivedEvidenceBuildError(f"Outcome/assistance invariant for Problem {problem_id}")
        if whole_count + sum(part_counts.values()) != count:
            raise DerivedEvidenceBuildError(f"Whole/part partition invariant for Problem {problem_id}")

        problem = validated_problems.get(problem_id)
        declared = _declared_parts(problem)
        attempted_parts = _ordered_attempted_parts(set(part_counts), declared)
        ordered_part_counts = _ordered_part_counts(part_counts, declared)

        rollups[problem_id] = ProblemEvidenceRollup(
            problem_id=problem_id,
            attempt_ids=attempt_ids,
            attempt_count=count,
            outcome_counts=dict(outcome),
            assistance_counts=dict(assistance),
            whole_problem_attempt_count=whole_count,
            attempted_parts=attempted_parts,
            part_attempt_counts=ordered_part_counts,
        )
    return rollups


def build_derived_evidence(
    validated_problems: Mapping[str, ProblemDocument] | list[ProblemDocument],
    validated_attempts: Mapping[str, AttemptDocument],
) -> DerivedEvidenceSnapshot:
    """Build DerivedEvidenceSnapshot from validated Problem + Attempt registries only."""

    if isinstance(validated_problems, list):
        problem_map = _problem_registry_from_documents(validated_problems)
    else:
        problem_map = dict(validated_problems)

    target_states = _build_target_states(validated_attempts)
    problem_rollups = _build_problem_rollups(target_states, problem_map)
    return DerivedEvidenceSnapshot(
        target_states=target_states,
        problem_rollups=problem_rollups,
    )


def build_derived_evidence_from_validation_results(
    problem_result,
    attempt_result,
) -> DerivedEvidenceSnapshot:
    """Convenience: build from Problem/Attempt ValidationResult objects."""

    problem_docs = [d for d in problem_result.documents if d.object_id]
    attempt_registry = dict(attempt_result.registry) if attempt_result.registry else {}
    if not attempt_registry:
        attempt_registry = {
            d.object_id: d for d in attempt_result.documents if d.object_id
        }
    return build_derived_evidence(problem_docs, attempt_registry)
