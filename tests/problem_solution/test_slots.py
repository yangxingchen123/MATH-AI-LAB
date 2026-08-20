"""Tests for canonical Solution slot parsing and upsert."""

from __future__ import annotations

from pathlib import Path

from tests.problem_validator.conftest import problem_md, write_project
from tools.problem_solution.slots import (
    content_equal,
    find_slot,
    upsert_body,
    wrap_slot_content,
)
from tools.problem_solution.writer import upsert_canonical_solution


def _write_problem(project: Path, pid: str = "P0001", body: str = "# Title\n\n## 题目\n\nQ\n") -> Path:
    write_project(project)
    kb = project / "01_知识库"
    (kb / "K0001.md").write_text(
        """---
schema_version: 1
id: K0001
type: knowledge
title: K
aliases: []
status: reviewed
created: 2026-08-19
updated: 2026-08-19
domain: 线性代数
prerequisites: []
---

body
""",
        encoding="utf-8",
    )
    path = project / "02_题目库" / f"{pid}.md"
    path.write_text(problem_md(pid=pid, body=body), encoding="utf-8")
    return path


def test_first_solution_creates_slot() -> None:
    body = "# T\n\n## 题目\n\nQ\n"
    new_body, action = upsert_body(body, problem_id="P0001", part="a", content="answer one")
    assert action == "CREATE"
    assert "## 解答" in new_body
    assert "target=P0001/a BEGIN" in new_body
    assert "answer one" in new_body


def test_same_target_updates_same_slot() -> None:
    body = "# T\n\n## 解答\n\n" + wrap_slot_content("P0001/a", "old")
    new_body, action = upsert_body(body, problem_id="P0001", part="a", content="new answer")
    assert action == "UPDATE"
    assert new_body.count("target=P0001/a BEGIN") == 1
    assert "new answer" in new_body
    assert "old" not in new_body


def test_identical_content_no_op() -> None:
    body = "# T\n\n## 解答\n\n" + wrap_slot_content("P0001/a", "same")
    new_body, action = upsert_body(body, problem_id="P0001", part="a", content="same")
    assert action == "NO_OP"
    assert new_body == body


def test_different_parts_separate_slots() -> None:
    body = "# T\n\n## 解答\n\n" + wrap_slot_content("P0001/a", "a ans")
    new_body, action = upsert_body(body, problem_id="P0001", part="b", content="b ans")
    assert action == "CREATE"
    assert find_slot(new_body, problem_id="P0001", part="a") is not None
    assert find_slot(new_body, problem_id="P0001", part="b") is not None


def test_legacy_part_slot_detected() -> None:
    body = "# T\n\n## 研究记录\n\n### (a) AI-generated Solution\n\nlegacy content\n"
    slot = find_slot(body, problem_id="P0002", part="a")
    assert slot is not None
    assert content_equal(slot.content, "legacy content")


def test_legacy_identical_content_migrates_to_canonical() -> None:
    body = "# T\n\n## 研究记录\n\n### (a) AI-generated Solution\n\nlegacy content\n"
    new_body, action = upsert_body(body, problem_id="P0002", part="a", content="legacy content")
    assert action == "UPDATE"
    assert "target=P0002/a BEGIN" in new_body
    assert "### (a) AI-generated Solution" not in new_body



def test_missing_problem_does_not_modify_existing(tmp_path: Path) -> None:
    path = _write_problem(tmp_path, body="# T\n\n## 题目\n\nQ\n")
    before = path.read_text(encoding="utf-8")
    bad = upsert_canonical_solution(tmp_path, problem_id="P9999", part="a", content="x")
    assert bad.written is False
    assert path.read_text(encoding="utf-8") == before


def test_unrelated_problem_content_preserved(tmp_path: Path) -> None:
    path = _write_problem(tmp_path, body="# T\n\n## 题目\n\nKeep this line.\n")
    upsert_canonical_solution(tmp_path, problem_id="P0001", part="a", content="ans")
    text = path.read_text(encoding="utf-8")
    assert "Keep this line." in text
