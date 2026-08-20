"""Knowledge relation validation tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from tools.knowledge_validator.models import ValidationSummary
from tools.knowledge_validator.models import ValidationResult as KnowledgeValidationResult
from tools.knowledge_validator.validator import validate_project as validate_knowledge_project
from tools.method_validator.validator import validate_project
from tests.method_validator.conftest import knowledge_md, method_md


def _k(project: Path, kid: str = "K0001", status: str = "reviewed") -> None:
    (project / "01_知识库" / f"{kid}.md").write_text(
        knowledge_md(kid=kid, status=status), encoding="utf-8"
    )


def _m(project: Path, name: str, content: str) -> None:
    (project / "12_方法库" / name).write_text(content, encoding="utf-8")


def test_knowledge_omitted_passes(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md())
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_valid_knowledge_list_passes(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(extras="knowledge:\n  - K0001"))
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_knowledge_empty_list_fails(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(extras="knowledge: []"))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-KNOW-E002" for i in result.issues)


def test_knowledge_scalar_fails(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(extras="knowledge: K0001"))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-KNOW-E001" for i in result.issues)


def test_invalid_k_lexical(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(extras="knowledge:\n  - bad"))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-KNOW-E003" for i in result.issues)


def test_k0000_forbidden(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(extras="knowledge:\n  - K0000"))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-KNOW-E004" for i in result.issues)


def test_duplicate_k_ref(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(extras="knowledge:\n  - K0001\n  - K0001"))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-KNOW-E005" for i in result.issues)


def test_nonexistent_k_ref(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md(extras="knowledge:\n  - K9999"))
    result = validate_project(root=project)
    assert any(i.rule_id == "M-KNOW-E006" for i in result.issues)


def test_knowledge_ordering_not_required(project: Path) -> None:
    _k(project, "K0001")
    _k(project, "K0002")
    _m(project, "M0001.md", method_md(extras="knowledge:\n  - K0002\n  - K0001"))
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_draft_method_with_draft_k_passes(project: Path) -> None:
    _k(project, status="draft")
    _m(
        project,
        "M0001.md",
        method_md(status="draft", extras="knowledge:\n  - K0001"),
    )
    result = validate_project(root=project)
    assert result.summary.errors == 0


def test_auto_calls_knowledge_validator(project: Path) -> None:
    _k(project)
    _m(project, "M0001.md", method_md())
    with patch(
        "tools.method_validator.validator.validate_knowledge_project",
        wraps=validate_knowledge_project,
    ) as mock_kv:
        validate_project(root=project)
        assert mock_kv.call_count == 1


def test_invalid_knowledge_dependency_blocks_registry(project: Path) -> None:
    _m(project, "M0001.md", method_md())
    bad_kv = KnowledgeValidationResult(
        project_root=project,
        summary=ValidationSummary(result="FAIL", errors=1),
    )
    result = validate_project(root=project, knowledge_result=bad_kv)
    assert any(i.rule_id == "M-KNOW-E010" for i in result.issues)
    assert result.registry == {}
