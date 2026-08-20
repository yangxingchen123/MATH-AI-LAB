"""Fixtures for workspace indexer tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from tests.attempt_validator.conftest import attempt_record, write_ledger
from tests.knowledge_indexer.conftest import write_reviewed_pair
from tests.problem_validator.conftest import problem_md, write_project
from tools.attempt_validator.ledger import load_ledger_file, serialize_ledger


def ensure_attempt_root(project: Path) -> Path:
    root = project / "11_学习证据" / "尝试记录"
    root.mkdir(parents=True, exist_ok=True)
    return root


def ensure_method_root(project: Path) -> Path:
    root = project / "12_方法库"
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_method(
    project: Path,
    relative: str,
    *,
    mid: str = "M0001",
    title: str = "Test Method",
    status: str = "draft",
    extras: str = "",
    body: str = "body\n",
) -> Path:
    ensure_method_root(project)
    extra = (extras.rstrip() + "\n") if extras.strip() else ""
    text = (
        "---\n"
        "schema_version: 1\n"
        f"id: {mid}\n"
        "type: method\n"
        f"title: {title}\n"
        f"status: {status}\n"
        f"{extra}"
        "---\n\n"
        f"{body}"
    )
    path = project / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_problem(
    project: Path,
    relative: str,
    *,
    pid: str,
    title: str = "示例",
    status: str = "draft",
    extras: str = "",
) -> Path:
    path = project / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        problem_md(pid=pid, title=title, status=status, extras=extras),
        encoding="utf-8",
    )
    return path


def write_attempt(
    project: Path,
    relative: str,
    *,
    aid: str = "A000001",
    problem: str = "P0002",
    part: str | None = "b",
    outcome: str = "correct",
    assistance: str | None = "assisted",
    attempted_at: str = "2026-08-19T21:36+08:00",
    extras: str = "",
    body: str = "body\n",
) -> Path:
    ensure_attempt_root(project)
    ledger_path = project / "11_学习证据" / "尝试记录" / f"{problem}.md"
    record = attempt_record(
        aid=aid,
        problem=problem,
        part=part,
        outcome=outcome,
        assistance=assistance,
        attempted_at=attempted_at.strip('"'),
    )
    records: list[dict[str, Any]] = []
    sections: dict[str, str] = {}
    if ledger_path.is_file():
        loaded = load_ledger_file(ledger_path, project)
        records = [dict(r) for r in loaded.attempts]
        sections = dict(loaded.sections)
    records = [r for r in records if r.get("id") != aid]
    records.append(record)
    sections[aid] = body.rstrip()
    ledger_path.write_text(
        serialize_ledger(problem_id=problem, attempts=records, sections=sections),
        encoding="utf-8",
    )
    return ledger_path


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = write_project(tmp_path)
    write_reviewed_pair(root)
    ensure_attempt_root(root)
    ensure_method_root(root)
    return root
