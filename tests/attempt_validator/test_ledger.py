"""Problem-scoped Attempt Ledger storage tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.attempt_validator import allocate_next_attempt_id, validate_project
from tools.attempt_validator.ledger import load_ledger_file, serialize_ledger
from tools.derived_evidence import TargetKey, build_derived_evidence_from_validation_results
from tools.problem_validator.validator import validate_project as validate_problem_project

from tests.attempt_validator.conftest import (
    attempt_record,
    setup_p0002_multipart,
    write_ledger,
    write_single_attempt,
)


def _baseline_snapshot(project: Path) -> dict[str, dict]:
    ar = validate_project(root=project)
    snap: dict[str, dict] = {}
    for doc in ar.documents:
        snap[doc.object_id or ""] = {
            k: doc.data.get(k)
            for k in (
                "schema_version",
                "id",
                "type",
                "problem",
                "part",
                "outcome",
                "assistance",
                "attempted_at",
                "corrections",
            )
        }
    return snap


def test_ledger_two_attempts_loader(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [
            attempt_record(aid="A000001", part="b", attempted_at="2026-08-19T21:36+08:00"),
            attempt_record(aid="A000002", part="a", outcome="partial", assistance="independent", attempted_at="2026-08-19T22:05+08:00"),
        ],
        {"A000001": "n1", "A000002": "n2"},
    )
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0
    assert len(result.documents) == 2
    assert set(result.registry) == {"A000001", "A000002"}


def test_two_ledgers_merge_registry(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_single_attempt(attempt_project, aid="A000001", problem="P0002", part="b")
    from tests.attempt_validator.conftest import setup_p0001_no_parts

    setup_p0001_no_parts(attempt_project)
    write_single_attempt(
        attempt_project,
        aid="A000002",
        problem="P0001",
        part=None,
        attempted_at="2026-08-19T22:00+08:00",
    )
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0
    assert len(result.registry) == 2


def test_ledger_filename_problem_mismatch(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [attempt_record(problem="P0003")],
        {"A000001": "body"},
        filename="P0003.md",
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-LEDG-E003" for i in result.issues)


def test_attempt_problem_mismatch(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [attempt_record(problem="P0001")],
        {"A000001": "body"},
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-LEDG-E006" for i in result.issues)


def test_duplicate_id_within_ledger(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    records = [
        attempt_record(aid="A000010", part="a", attempted_at="2026-08-19T21:00+08:00"),
        attempt_record(aid="A000010", part="b", attempted_at="2026-08-19T22:00+08:00"),
    ]
    write_ledger(attempt_project, "P0002", records, {"A000010": "body"})
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-LEDG-E005" for i in result.issues)


def test_duplicate_id_across_ledgers(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    from tests.attempt_validator.conftest import setup_p0001_no_parts

    setup_p0001_no_parts(attempt_project)
    write_single_attempt(attempt_project, aid="A000010", problem="P0002", part="a")
    write_single_attempt(
        attempt_project,
        aid="A000010",
        problem="P0001",
        part=None,
        attempted_at="2026-08-19T22:00+08:00",
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-ID-E001" for i in result.issues)


def test_invalid_attempt_record(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    bad = attempt_record()
    bad["outcome"] = "bad"
    write_ledger(attempt_project, "P0002", [bad], {"A000001": "body"})
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-OUT-E001" for i in result.issues)


def test_missing_narrative_section(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    root = attempt_project / "11_学习证据" / "尝试记录" / "P0002.md"
    root.write_text(
        """---
storage_format: problem_attempt_ledger_v1
problem: P0002
attempts:
  - schema_version: 1
    id: A000001
    type: attempt
    problem: P0002
    part: b
    outcome: correct
    assistance: assisted
    attempted_at: '2026-08-19T21:36+08:00'
---

# P0002 尝试记录

""",
        encoding="utf-8",
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-LEDG-E007" for i in result.issues)


def test_orphan_narrative_section(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    path = write_ledger(attempt_project, "P0002", [attempt_record()], {"A000001": "b1"})
    text = path.read_text(encoding="utf-8") + "\n## A000099\n\norphan\n"
    path.write_text(text, encoding="utf-8")
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-LEDG-E008" for i in result.issues)


def test_non_chronological_order(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    root = attempt_project / "11_学习证据" / "尝试记录" / "P0002.md"
    root.write_text(
        """---
storage_format: problem_attempt_ledger_v1
problem: P0002
attempts:
  - schema_version: 1
    id: A000002
    type: attempt
    problem: P0002
    part: a
    outcome: partial
    assistance: independent
    attempted_at: '2026-08-20T01:00+08:00'
  - schema_version: 1
    id: A000001
    type: attempt
    problem: P0002
    part: b
    outcome: correct
    assistance: assisted
    attempted_at: '2026-08-19T21:00+08:00'
---

# P0002 尝试记录

## A000002

n2

## A000001

n1
""",
        encoding="utf-8",
    )
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-LEDG-E009" for i in result.issues)


def test_corrections_round_trip(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    record = attempt_record(
        extras={
            "corrections": [
                {"at": "2026-08-20T10:20+08:00", "note": "修正了构造步骤。"},
            ]
        }
    )
    write_ledger(attempt_project, "P0002", [record], {"A000001": "body"})
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0
    assert result.documents[0].data["corrections"][0]["note"] == "修正了构造步骤。"


def test_empty_narrative_allowed(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(attempt_project, "P0002", [attempt_record()], {"A000001": ""})
    result = validate_project(root=attempt_project)
    assert result.summary.errors == 0


def test_derived_projection_unchanged(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [
            attempt_record(aid="A000001", part="b", attempted_at="2026-08-19T21:36+08:00"),
            attempt_record(aid="A000002", part="a", outcome="partial", assistance="independent", attempted_at="2026-08-19T22:05+08:00"),
        ],
        {"A000001": "n1", "A000002": "n2"},
    )
    pr = validate_problem_project(root=attempt_project)
    ar = validate_project(root=attempt_project)
    snap = build_derived_evidence_from_validation_results(pr, ar)
    a_state = snap.target_states[TargetKey("P0002", "a")]
    assert a_state.attempt_ids == ("A000002",)
    assert a_state.outcome_counts["partial"] == 1


def test_allocator_global_scan(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    write_ledger(
        attempt_project,
        "P0002",
        [
            attempt_record(aid="A000001", attempted_at="2026-08-19T21:00+08:00"),
            attempt_record(aid="A000004", part="a", attempted_at="2026-08-20T01:00+08:00"),
        ],
        {"A000001": "n1", "A000004": "n4"},
    )
    assert allocate_next_attempt_id(attempt_project) == "A000005"


def test_legacy_file_rejected(attempt_project: Path) -> None:
    setup_p0002_multipart(attempt_project)
    root = attempt_project / "11_学习证据" / "尝试记录"
    (root / "A000999.md").write_text("legacy\n", encoding="utf-8")
    result = validate_project(root=attempt_project)
    assert any(i.rule_id == "A-STOR-E001" for i in result.issues)
