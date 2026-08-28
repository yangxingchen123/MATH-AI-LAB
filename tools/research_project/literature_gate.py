"""Read-only v1.3 literature gate. Does not write production Source."""

from __future__ import annotations

from .constants import (
    FIXTURE_ROOT,
    LITERATURE_GATE_METRIC_NAMES,
)
from .gate import THRESHOLD_RATE, THRESHOLD_ZERO, _metric, _rate_status
from .literature import (
    citation_coverage,
    classify_fixture_rate,
    hype_violations,
    open_blocking_reviews,
    retraction_violations,
    unsupported_attributions,
)
from .parser import parse_project
from .validator import validate_project


def evaluate_literature_gate() -> dict:
    metrics = [
        _coverage_metric(),
        _unsupported_metric(),
        _retraction_metric(),
        _classify_metric(),
        _hype_metric(),
        _review_metric(),
    ]
    by_name = {item["name"]: item for item in metrics}
    ordered = [by_name[name] for name in LITERATURE_GATE_METRIC_NAMES]
    status = "PASS" if all(item["status"] == "PASS" for item in ordered) else "FAIL"
    return {"contract_version": "1.3", "status": status, "metrics": ordered}


def _coverage_metric() -> dict:
    project = FIXTURE_ROOT / "literature" / "cited_core_claim"
    docs = parse_project(project)
    covered, total, missing = citation_coverage(docs)
    return _metric(
        "core_claim_citation_coverage",
        covered,
        total or 1,
        THRESHOLD_RATE,
        _rate_status(covered, total) if total else "FAIL",
        f"missing={missing or 'none'}",
    )


def _unsupported_metric() -> dict:
    project = FIXTURE_ROOT / "literature" / "cited_core_claim"
    docs = parse_project(project)
    issues = unsupported_attributions(docs)
    return _metric(
        "unsupported_attribution_count",
        len(issues),
        1,
        THRESHOLD_ZERO,
        "PASS" if not issues else "FAIL",
        "; ".join(issues) or "none",
    )


def _retraction_metric() -> dict:
    bad = FIXTURE_ROOT / "literature" / "retracted_unacked"
    good = FIXTURE_ROOT / "literature" / "retracted_acked"
    detected = not validate_project(bad).ok
    allowed = validate_project(good).ok
    numerator = int(detected) + int(allowed)
    return _metric(
        "retraction_correction_detection_rate",
        numerator,
        2,
        THRESHOLD_RATE,
        _rate_status(numerator, 2),
        f"unacked_fail={detected}; acked_pass={allowed}",
    )


def _classify_metric() -> dict:
    correct, total = classify_fixture_rate(FIXTURE_ROOT / "literature" / "classify")
    return _metric(
        "quote_paraphrase_inference_classification_rate",
        correct,
        total,
        THRESHOLD_RATE,
        _rate_status(correct, total),
        str(FIXTURE_ROOT / "literature" / "classify"),
    )


def _hype_metric() -> dict:
    bad = FIXTURE_ROOT / "literature" / "hype_without_novelty"
    good = FIXTURE_ROOT / "literature" / "hype_with_novelty"
    blocked = not validate_project(bad).ok
    allowed = validate_project(good).ok
    docs_bad = parse_project(bad)
    docs_good = parse_project(good)
    blocked = blocked and bool(hype_violations(docs_bad))
    allowed = allowed and not hype_violations(docs_good)
    numerator = int(blocked) + int(allowed)
    return _metric(
        "novelty_hype_block_rate",
        numerator,
        2,
        THRESHOLD_RATE,
        _rate_status(numerator, 2),
        f"hype_blocked={blocked}; evidenced_pass={allowed}",
    )


def _review_metric() -> dict:
    project = FIXTURE_ROOT / "literature" / "blocking_review"
    docs = parse_project(project)
    open_refs = open_blocking_reviews(docs)
    blocked = bool(open_refs)
    return _metric(
        "blocking_review_formal_block_rate",
        int(blocked),
        1,
        THRESHOLD_RATE,
        _rate_status(int(blocked), 1),
        f"open_blocking={open_refs}",
    )
