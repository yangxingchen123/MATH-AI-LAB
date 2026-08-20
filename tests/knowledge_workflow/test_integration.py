from __future__ import annotations

from pathlib import Path

from tools.knowledge_indexer import check_index
from tools.knowledge_validator import validate_project
from tools.knowledge_workflow.service import sync_file

from tests.knowledge_indexer.conftest import write_reviewed_pair


def test_workflow_uses_same_stack(project: Path) -> None:
    write_reviewed_pair(project)
    target = project / "01_知识库/数学变换/勒让德变换.md"
    result = sync_file(target, root=project)
    assert result.result == "SUCCESS"
    assert validate_project(root=project).summary.result == "PASS"
    assert check_index(root=project).result.value == "CURRENT"
