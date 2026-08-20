"""focus_view and check-file context tests."""

from __future__ import annotations

from pathlib import Path

from tools.problem_validator.validator import focus_view, validate_project
from tests.problem_validator.conftest import knowledge_md, problem_md


def _setup_duplicate(project: Path) -> tuple[Path, Path]:
    kb = project / "01_知识库"
    (kb / "K0001.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    base = project / "02_题目库"
    a = base / "a.md"
    b = base / "b.md"
    a.write_text(problem_md(pid="P0001"), encoding="utf-8")
    b.write_text(problem_md(pid="P0001", title="dup"), encoding="utf-8")
    return a, b


def test_focus_view_shows_duplicate_for_target_file(project: Path) -> None:
    a, _ = _setup_duplicate(project)
    full = validate_project(root=project)
    view = focus_view(full, a)
    assert any(i.rule_id == "P-ID-E001" for i in view.issues)


def test_no_legacy_filename_issue(project: Path) -> None:
    kb = project / "01_知识库"
    (kb / "K0001.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    path = project / "02_题目库" / "P001_legacy_name.md"
    path.write_text(problem_md(pid="P0001"), encoding="utf-8")
    result = validate_project(root=project)
    assert not any("legacy" in i.message.lower() or "filename" in i.message.lower() for i in result.issues)


def test_no_content_review_marker_issue(project: Path) -> None:
    kb = project / "01_知识库"
    (kb / "K0001.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    path = project / "02_题目库" / "P0001.md"
    path.write_text(
        problem_md(body="Candidate Content Review: PENDING\n"),
        encoding="utf-8",
    )
    result = validate_project(root=project)
    assert not any("content review" in i.message.lower() for i in result.issues)
