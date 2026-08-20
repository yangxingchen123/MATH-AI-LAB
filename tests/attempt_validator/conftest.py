"""Shared fixtures for Attempt Validator tests."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest

from tests.problem_validator.conftest import knowledge_md, problem_md, write_project
from tools.attempt_validator.ledger import serialize_ledger


def write_attempt_project(root: Path) -> Path:
    write_project(root)
    attempt_root = root / "11_学习证据" / "尝试记录"
    attempt_root.mkdir(parents=True, exist_ok=True)
    return root


def attempt_record(
    *,
    aid: str = "A000001",
    problem: str = "P0002",
    part: str | None = "b",
    outcome: str = "correct",
    assistance: str | None = "assisted",
    attempted_at: str = "2026-08-19T21:36+08:00",
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_version": 1,
        "id": aid,
        "type": "attempt",
        "problem": problem,
        "outcome": outcome,
        "attempted_at": attempted_at,
    }
    if part is not None:
        record["part"] = part
    if assistance is not None:
        record["assistance"] = assistance
    if extras:
        record.update(extras)
    return record


def write_ledger(
    project: Path,
    problem: str,
    records: list[dict[str, Any]],
    sections: dict[str, str],
    *,
    filename: str | None = None,
) -> Path:
    root = project / "11_学习证据" / "尝试记录"
    root.mkdir(parents=True, exist_ok=True)
    path = root / (filename or f"{problem}.md")
    path.write_text(
        serialize_ledger(problem_id=problem, attempts=records, sections=sections),
        encoding="utf-8",
    )
    return path


def attempt_md(
    *,
    aid: str = "A000001",
    problem: str = "P0002",
    part: str | None = "b",
    outcome: str = "correct",
    assistance: str | None = "assisted",
    attempted_at: str = '"2026-08-19T21:36+08:00"',
    extras: str = "",
    body: str = "body\n",
    filename: str | None = None,
) -> str:
    """Build ledger file content (single Attempt) for tests."""
    ts = attempted_at.strip('"')
    record = attempt_record(
        aid=aid,
        problem=problem,
        part=part,
        outcome=outcome,
        assistance=assistance,
        attempted_at=ts,
    )
    return serialize_ledger(
        problem_id=problem,
        attempts=[record],
        sections={aid: body.rstrip()},
    )


def write_single_attempt(
    project: Path,
    *,
    aid: str = "A000001",
    problem: str = "P0002",
    part: str | None = "b",
    outcome: str = "correct",
    assistance: str | None = "assisted",
    attempted_at: str = "2026-08-19T21:36+08:00",
    body: str = "body\n",
    filename: str | None = None,
) -> Path:
    root = project / "11_学习证据" / "尝试记录"
    root.mkdir(parents=True, exist_ok=True)
    path = root / (filename or f"{problem}.md")
    record = attempt_record(
        aid=aid,
        problem=problem,
        part=part,
        outcome=outcome,
        assistance=assistance,
        attempted_at=attempted_at,
    )
    path.write_text(
        serialize_ledger(problem_id=problem, attempts=[record], sections={aid: body.rstrip()}),
        encoding="utf-8",
    )
    return path


def setup_p0002_multipart(project: Path) -> None:
    kb = project / "01_知识库"
    (kb / "K0001.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    pb = project / "02_题目库"
    (pb / "P0002.md").write_text(
        problem_md(
            pid="P0002",
            extras=dedent(
                """\
                parts:
                  - a
                  - b
                  - c
                """
            ),
        ),
        encoding="utf-8",
    )


def setup_p0001_no_parts(project: Path) -> None:
    kb = project / "01_知识库"
    (kb / "K0001.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    pb = project / "02_题目库"
    (pb / "P0001.md").write_text(problem_md(pid="P0001"), encoding="utf-8")


@pytest.fixture
def attempt_project(tmp_path: Path) -> Path:
    return write_attempt_project(tmp_path)
