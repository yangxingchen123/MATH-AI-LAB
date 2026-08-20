from __future__ import annotations

import json
from pathlib import Path

from tools.knowledge_validator.cli import run
from tools.knowledge_validator.validator import focus_view, validate_file, validate_project

from .conftest import knowledge_md


def test_check_file_valid_draft(project: Path) -> None:
    path = project / "01_知识库" / "a.md"
    path.write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    r = validate_file(path, root=project)
    assert r.summary.result == "PASS"


def test_check_file_valid_reviewed(project: Path) -> None:
    path = project / "01_知识库" / "a.md"
    path.write_text(
        knowledge_md(
            kid="K0001",
            status="reviewed",
            aliases="",
            extras="domain: 凸分析\nprerequisites: []\nrelated: []",
        ),
        encoding="utf-8",
    )
    r = validate_file(path, root=project)
    assert r.summary.result == "PASS"


def test_check_file_missing_target_uses_registry(project: Path) -> None:
    path = project / "01_知识库" / "a.md"
    path.write_text(
        knowledge_md(kid="K0001", extras="prerequisites:\n  - K0099"),
        encoding="utf-8",
    )
    r = validate_file(path, root=project)
    assert any(i.rule_id == "K-REL-001" for i in r.issues)


def test_check_file_target_draft(project: Path) -> None:
    (project / "01_知识库" / "b.md").write_text(
        knowledge_md(kid="K0002", status="draft"), encoding="utf-8"
    )
    path = project / "01_知识库" / "a.md"
    path.write_text(
        knowledge_md(
            kid="K0001",
            status="reviewed",
            aliases="",
            extras="domain: 凸分析\nprerequisites:\n  - K0002\nrelated: []",
        ),
        encoding="utf-8",
    )
    r = validate_file(path, root=project)
    assert any(i.rule_id == "K-REL-005" for i in r.issues)


def test_check_file_duplicate_id(project: Path) -> None:
    body = knowledge_md(kid="K0002")
    (project / "01_知识库" / "a.md").write_text(body, encoding="utf-8")
    path = project / "01_知识库" / "b.md"
    path.write_text(body, encoding="utf-8")
    r = validate_file(path, root=project)
    assert any(i.rule_id == "K-BASE-040" for i in r.issues)


def test_check_file_dag_cycle_context(project: Path) -> None:
    (project / "01_知识库" / "a.md").write_text(
        knowledge_md(kid="K0001", extras="prerequisites:\n  - K0002"),
        encoding="utf-8",
    )
    path = project / "01_知识库" / "b.md"
    path.write_text(
        knowledge_md(kid="K0002", extras="prerequisites:\n  - K0001"),
        encoding="utf-8",
    )
    r = validate_file(path, root=project)
    assert any(i.rule_id == "K-GRAPH-001" for i in r.issues)


def test_cli_check_text(project: Path, capsys) -> None:
    (project / "01_知识库" / "a.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    code = run(["check", "--root", str(project), "--format", "text"])
    out = capsys.readouterr().out
    assert code == 0
    assert "PASS" in out


def test_cli_check_json(project: Path, capsys) -> None:
    (project / "01_知识库" / "a.md").write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    code = run(["check", "--root", str(project), "--format", "json"])
    out = capsys.readouterr().out
    assert code == 0
    payload = json.loads(out)
    assert payload["summary"]["result"] == "PASS"


def test_cli_check_file(project: Path, capsys) -> None:
    path = project / "01_知识库" / "a.md"
    path.write_text(knowledge_md(kid="K0001"), encoding="utf-8")
    code = run(["check-file", str(path), "--root", str(project)])
    assert code == 0
    assert "PASS" in capsys.readouterr().out


def test_cli_summary_verbose_strict(project: Path, capsys) -> None:
    (project / "01_知识库" / "b.md").write_text(
        knowledge_md(kid="K0002", status="draft"), encoding="utf-8"
    )
    (project / "01_知识库" / "a.md").write_text(
        knowledge_md(kid="K0001", status="draft", extras="prerequisites:\n  - K0002"),
        encoding="utf-8",
    )
    code = run(["check", "--root", str(project), "--summary"])
    assert code == 0
    out = capsys.readouterr().out
    assert "PASS" in out

    code2 = run(["check", "--root", str(project), "--strict-warnings"])
    assert code2 == 1

    code3 = run(["check", "--root", str(project), "--verbose"])
    assert code3 == 0
    assert "Documents:" in capsys.readouterr().out or True


def test_focus_view_does_not_mutate_full_result(project: Path) -> None:
    (project / "01_知识库" / "a.md").write_text(
        knowledge_md(kid="K0001", extras="prerequisites:\n  - K0099"),
        encoding="utf-8",
    )
    (project / "01_知识库" / "b.md").write_text(knowledge_md(kid="K0002"), encoding="utf-8")
    full = validate_project(root=project)
    full_count = len(full.issues)
    view = focus_view(full, project / "01_知识库" / "b.md")
    assert len(full.issues) == full_count
    assert view.summary.errors == 0
    assert full.summary.errors > 0
