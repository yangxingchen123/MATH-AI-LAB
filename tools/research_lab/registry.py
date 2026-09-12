"""Open-problem stage machine. Not Frozen Schema; not a Dossier Record."""

from __future__ import annotations

from pathlib import Path

import yaml

from .constants import PROBLEMS_DIR

STAGES: tuple[str, ...] = (
    "INBOX",
    "TRIAGED",
    "PRIOR_ART_CHECKED",
    "STATEMENT_REVIEWED",
    "FALSIFICATION",
    "CANDIDATE_SURVIVED",
    "PROOF_PLANNED",
    "PROVED_INFORMAL",
    "PROVED_FORMAL",
    "EXTERNAL_REVIEWED",
    "PAPER_READY",
)

TERMINAL_STAGES: tuple[str, ...] = (
    "REJECTED_FALSE",
    "REJECTED_KNOWN",
    "REJECTED_TRIVIAL",
    "REJECTED_LOW_VALUE",
    "BLOCKED_MISSING_THEORY",
    "PAUSED_COST",
)

REQUIRED_FIELDS: tuple[str, ...] = (
    "id",
    "title",
    "track",
    "stage",
    "evaluator",
    "success_level",
)

PRIOR_ART_RELATIONS: tuple[str, ...] = (
    "same",
    "special_case",
    "corollary",
    "similar_method",
    "numeric_only",
    "unknown",
)


def validate_prior_art(prior: object, *, required: bool = False) -> list[str]:
    errors: list[str] = []
    if required and not prior:
        errors.append("novelty_claim requires prior_art")
        return errors
    if prior is None:
        return errors
    if not isinstance(prior, list):
        errors.append("prior_art must be a list")
        return errors
    for index, row in enumerate(prior):
        if not isinstance(row, dict) or row.get("relation") not in PRIOR_ART_RELATIONS:
            errors.append(f"prior_art[{index}] needs a known relation")
    return errors


def load_record(path: Path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("problem record must be a mapping")
    return data


def validate_record(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["record must be a mapping"]
    for key in REQUIRED_FIELDS:
        if not data.get(key):
            errors.append(f"missing {key}")
    stage = data.get("stage")
    allowed = set(STAGES) | set(TERMINAL_STAGES)
    if stage and stage not in allowed:
        errors.append(f"unknown stage: {stage}")
    track = data.get("track")
    if track and track not in {"A", "B", "C"}:
        errors.append("track must be A, B, or C")
    if data.get("stage") == "PAPER_READY" and data.get("success_level") not in {"S3", "S4", "S5"}:
        errors.append("PAPER_READY requires success_level S3+")
    if data.get("stage") in {"EXTERNAL_REVIEWED", "PAPER_READY"} and not data.get("human_pi_signoff"):
        errors.append("human_pi_signoff required")
    if data.get("novelty_claim") == "first" and not data.get("expert_signoff"):
        errors.append("novelty_claim=first requires expert_signoff")
    claim = data.get("novelty_claim")
    if claim in {"known", "first"}:
        errors.extend(validate_prior_art(data.get("prior_art"), required=True))
    elif data.get("prior_art") is not None:
        errors.extend(validate_prior_art(data.get("prior_art"), required=False))
    return errors


def list_problem_paths(root: Path | None = None) -> list[Path]:
    base = Path(root) if root is not None else PROBLEMS_DIR
    if not base.is_dir():
        return []
    return sorted(base.glob("*.yaml"))

