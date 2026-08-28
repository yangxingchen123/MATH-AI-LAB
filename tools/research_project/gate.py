"""Read-only v1.1 gate evaluator. Does not write production Source."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from pathlib import Path

from .append_only import assert_decisions_append_only
from .constants import (
    FIXTURE_ROOT,
    GATE_METRIC_NAMES,
    REQUIRED_DIRS,
    REQUIRED_FILES,
    TEMPLATE_ROOT,
)
from .governance import assess_external_processing
from .models import ResearchProjectOperationKind
from .operations import (
    add_assumption,
    add_claim,
    add_evidence,
    init_project,
    reconcile_project,
)
from .parser import parse_project
from .stale import dossier_is_stale, split_dossier
from .validator import validate_project

THRESHOLD_RATE = "100%"
THRESHOLD_ZERO = 0


def _metric(
    name: str,
    numerator: int,
    denominator: int,
    threshold,
    status: str,
    evidence: str,
) -> dict:
    if name.endswith("_count"):
        value: int | str = numerator
    elif denominator == 0:
        value = "0%"
    else:
        value = f"{int(round(100 * numerator / denominator))}%"
    return {
        "name": name,
        "numerator": numerator,
        "denominator": denominator,
        "value": value,
        "threshold": threshold,
        "status": status,
        "evidence": evidence,
    }


def _rate_status(numerator: int, denominator: int) -> str:
    return "PASS" if denominator and numerator == denominator else "FAIL"


def _scaffold_metric() -> dict:
    items = list(REQUIRED_FILES) + list(REQUIRED_DIRS)
    present = sum(
        1
        for name in REQUIRED_FILES
        if (TEMPLATE_ROOT / name).is_file()
    ) + sum(1 for name in REQUIRED_DIRS if (TEMPLATE_ROOT / name).is_dir())
    return _metric(
        "project_scaffold_completeness_rate",
        present,
        len(items),
        THRESHOLD_RATE,
        _rate_status(present, len(items)),
        str(TEMPLATE_ROOT),
    )


def _duplicate_metric() -> dict:
    fixture = FIXTURE_ROOT / "duplicate_ref"
    result = validate_project(fixture)
    detected = any("duplicate" in item.lower() for item in result.errors)
    numerator = 1 if detected else 0
    return _metric(
        "duplicate_fixture_detection_rate",
        numerator,
        1,
        THRESHOLD_RATE,
        _rate_status(numerator, 1),
        str(fixture),
    )


def _append_only_metric() -> dict:
    base = (
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0001 BEGIN -->\n"
        "- date: 2026-08-20\n"
        "- question: q\n"
        "- options: a|b\n"
        "- choice: a\n"
        "- basis: b\n"
        "- cost: c\n"
        "- reversible: false\n"
        "- revisit_when: never\n"
        "---\n"
        "body1\n"
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=DECISION ref=DEC-0001 END -->\n"
    )
    cases = [
        base.replace("body1", "body1-edited"),
        "",
        base.replace("body1\n", "body1 \n"),
    ]
    detected = 0
    for bad in cases:
        try:
            assert_decisions_append_only(base, bad)
        except ValueError:
            detected += 1
    return _metric(
        "append_only_fixture_detection_rate",
        detected,
        len(cases),
        THRESHOLD_RATE,
        _rate_status(detected, len(cases)),
        "in-memory historical Decision mutation matrix",
    )


def _sha256_tree(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*")):
        if path.is_file():
            out[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return out


def _disposable_metrics() -> tuple[dict, dict, dict, dict, dict]:
    overwrite = 0
    stable = 0
    knowledge_create = 0
    attempt_pollute = 0
    boundary_violation = 0
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        knowledge = repo / "01_知识库"
        attempts = repo / "11_学习证据"
        knowledge.mkdir(parents=True)
        attempts.mkdir(parents=True)
        (knowledge / "KEEP.md").write_text("unchanged\n", encoding="utf-8", newline="\n")
        (attempts / "KEEP.md").write_text("unchanged\n", encoding="utf-8", newline="\n")
        before_k = _sha256_tree(knowledge)
        before_a = _sha256_tree(attempts)
        project = repo / "07_项目" / "Gate_Project"
        init_project(project, "Gate", repo_root=repo)
        before_asm = (project / "assumptions.md").read_bytes()
        bad = Path(tmp) / "bad.md"
        bad.write_text("not a record\n", encoding="utf-8", newline="\n")
        add_assumption(project, bad)
        if (project / "assumptions.md").read_bytes() == before_asm:
            stable = 1
        cand = Path(tmp) / "asm.md"
        cand.write_text(
            "<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0001 BEGIN -->\n"
            "- status: ACTIVE\n"
            "- scope: s\n"
            "- rationale: r\n"
            "- falsifiable_when: f\n"
            "---\n"
            "assumption body\n"
            "<!-- MATH-AI-LAB:RESEARCH-RECORD type=ASSUMPTION ref=ASM-0001 END -->\n",
            encoding="utf-8",
            newline="\n",
        )
        add_assumption(project, cand)
        if "ASM-0001" not in (project / "assumptions.md").read_text(encoding="utf-8"):
            overwrite += 1
        clm = Path(tmp) / "clm.md"
        clm.write_text(
            "<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 BEGIN -->\n"
            "- status: OPEN\n"
            "---\n"
            "claim body\n"
            "<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 END -->\n",
            encoding="utf-8",
            newline="\n",
        )
        add_claim(project, clm)
        human_before, _, _ = split_dossier(
            (project / "research_dossier.md").read_text(encoding="utf-8")
        )
        reconcile_project(project)
        human_after, _, _ = split_dossier(
            (project / "research_dossier.md").read_text(encoding="utf-8")
        )
        if human_before != human_after:
            boundary_violation += 1
        if _sha256_tree(knowledge) != before_k:
            knowledge_create += 1
        if _sha256_tree(attempts) != before_a:
            attempt_pollute += 1
        if dossier_is_stale(project):
            boundary_violation += 1
    return (
        _metric(
            "decision_history_overwrite_count",
            overwrite,
            1,
            THRESHOLD_ZERO,
            "PASS" if overwrite == 0 else "FAIL",
            "disposable assumption write retained historical ref",
        ),
        _metric(
            "failed_write_byte_stability_rate",
            stable,
            1,
            THRESHOLD_RATE,
            _rate_status(stable, 1),
            "disposable invalid candidate left official bytes unchanged",
        ),
        _metric(
            "unauthorized_knowledge_create_count",
            knowledge_create,
            1,
            THRESHOLD_ZERO,
            "PASS" if knowledge_create == 0 else "FAIL",
            "01_知识库 tree hash unchanged",
        ),
        _metric(
            "attempt_pollution_count",
            attempt_pollute,
            1,
            THRESHOLD_ZERO,
            "PASS" if attempt_pollute == 0 else "FAIL",
            "11_学习证据 tree hash unchanged",
        ),
        _metric(
            "dossier_generated_boundary_violation_count",
            boundary_violation,
            1,
            THRESHOLD_ZERO,
            "PASS" if boundary_violation == 0 else "FAIL",
            "human dossier region preserved across reconcile",
        ),
    )


def _external_metric() -> dict:
    table = [
        ("missing_data_level", "BLOCKED"),
        ("restricted_unauthorized", "BLOCKED"),
        ("personal_unauthorized", "BLOCKED"),
        ("public_authorized_verified", "ALLOWED"),
        ("public_authorized_local_only", "BLOCKED"),
        ("public_authorized_unknown", "BLOCKED"),
        ("unauthorized_false", "BLOCKED"),
    ]
    correct = 0
    evidence = []
    for name, expected in table:
        path = FIXTURE_ROOT / "governance" / name
        actual = assess_external_processing(path).verdict
        evidence.append(f"{name}:{actual}")
        if actual == expected:
            correct += 1
    return _metric(
        "unauthorized_external_processing_block_rate",
        correct,
        len(table),
        THRESHOLD_RATE,
        _rate_status(correct, len(table)),
        ", ".join(evidence),
    )


def evaluate_gate() -> dict:
    metrics = [
        _scaffold_metric(),
        _duplicate_metric(),
        _append_only_metric(),
    ]
    metrics.extend(_disposable_metrics())
    metrics.append(_external_metric())
    ordered = []
    by_name = {item["name"]: item for item in metrics}
    for name in GATE_METRIC_NAMES:
        ordered.append(by_name[name])
    status = "PASS" if all(item["status"] == "PASS" for item in ordered) else "FAIL"
    return {"contract_version": "1.1", "status": status, "metrics": ordered}
