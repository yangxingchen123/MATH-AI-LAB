"""Knowledge field and dependency tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from tools.knowledge_validator.models import ValidationSummary
from tools.knowledge_validator.models import ValidationResult as KnowledgeValidationResult
from tools.knowledge_validator.validator import validate_project as validate_knowledge_project
from tools.problem_validator.validator import validate_project
from tests.problem_validator.conftest import knowledge_md, problem_md


def _k(project: Path, kid: str = "K0001", status: str = "reviewed") -> None:
    (project / "01_知识库" / f"{kid}.md").write_text(
        knowledge_md(kid=kid, status=status), encoding="utf-8"
    )


def test_draft_missing_knowledge_passes(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(problem_md(), encoding="utf-8")
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_reviewed_missing_knowledge_error(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(status="reviewed"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert any(i.rule_id == "P-KNOW-E002" for i in result.issues)


def test_reviewed_empty_knowledge_passes(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(status="reviewed", extras="knowledge: []"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_knowledge_non_list(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras="knowledge: K0001"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert any(i.rule_id == "P-KNOW-E001" for i in result.issues)


def test_invalid_k_target(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras="knowledge:\n  - bad"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert any(i.rule_id == "P-KNOW-E003" for i in result.issues)


def test_k0000_forbidden(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras="knowledge:\n  - K0000"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert any(i.rule_id == "P-KNOW-E004" for i in result.issues)


def test_duplicate_k_target(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras="knowledge:\n  - K0001\n  - K0001"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert any(i.rule_id == "P-KNOW-E005" for i in result.issues)


def test_missing_k_target(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras="knowledge:\n  - K9999"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert any(i.rule_id == "P-KNOW-E006" for i in result.issues)


def test_reviewed_to_draft_k_error(project: Path) -> None:
    _k(project, status="draft")
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(status="reviewed", extras="knowledge:\n  - K0001"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert any(i.rule_id == "P-KNOW-E008" for i in result.issues)


def test_reviewed_to_reviewed_k_passes(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(status="reviewed", extras="knowledge:\n  - K0001"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_auto_calls_knowledge_validator(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(problem_md(), encoding="utf-8")
    with patch(
        "tools.problem_validator.validator.validate_knowledge_project",
        wraps=validate_knowledge_project,
    ) as mock_kv:
        validate_project(root=project)
        assert mock_kv.call_count == 1


def test_injected_knowledge_result_not_revalidated(project: Path) -> None:
    _k(project)
    (project / "02_题目库" / "P0001.md").write_text(problem_md(), encoding="utf-8")
    kv = validate_knowledge_project(root=project)
    with patch(
        "tools.problem_validator.validator.validate_knowledge_project",
    ) as mock_kv:
        validate_project(root=project, knowledge_result=kv)
        mock_kv.assert_not_called()


def test_dependency_failure_reports_p_know_e010(project: Path) -> None:
    _k(project, status="draft")
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras="knowledge:\n  - K0001"), encoding="utf-8"
    )
    bad_kv = KnowledgeValidationResult(
        project_root=project,
        summary=ValidationSummary(errors=1, result="FAIL"),
    )
    result = validate_project(root=project, knowledge_result=bad_kv)
    assert any(i.rule_id == "P-KNOW-E010" for i in result.issues)
    assert not any(i.rule_id == "P-KNOW-E006" for i in result.issues)


def test_draft_to_draft_k_warning(project: Path) -> None:
    _k(project, status="draft")
    (project / "02_题目库" / "P0001.md").write_text(
        problem_md(extras="knowledge:\n  - K0001"), encoding="utf-8"
    )
    result = validate_project(root=project)
    assert any(i.rule_id == "P-KNOW-W001" for i in result.issues)
    assert result.summary.errors == 0
