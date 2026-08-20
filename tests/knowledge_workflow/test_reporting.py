from __future__ import annotations

import json
from pathlib import Path

from tools.knowledge_workflow.report import format_json, format_text
from tools.knowledge_workflow.service import check_file_workflow, status, sync_file

from tests.knowledge_indexer.conftest import write_knowledge, write_reviewed_pair


def test_json_sync_pass(project: Path) -> None:
    write_reviewed_pair(project)
    result = sync_file(project / "01_知识库/数学变换/勒让德变换.md", root=project)
    payload = json.loads(format_json(result))
    assert payload["workflow_version"] == "1.0"
    assert payload["result"] == "SUCCESS"
    assert "file_validation" in payload["stages"]
    assert payload["target"].endswith("勒让德变换.md")


def test_json_file_fail(project: Path) -> None:
    write_knowledge(project, "01_知识库/bad.md", kid="K00A1")
    result = sync_file(project / "01_知识库/bad.md", root=project)
    payload = json.loads(format_json(result))
    assert payload["result"] == "FILE_VALIDATION_FAILED"
    assert payload["stages"]["full_validation"]["status"] == "SKIPPED"
    ids = [i["rule_id"] for i in payload["stages"]["file_validation"]["issues"]]
    assert "K-BASE-010" in ids
    assert all(i["source"] in ("validator", "workflow") for i in payload["stages"]["file_validation"]["issues"])


def test_json_check_stale(project: Path) -> None:
    write_reviewed_pair(project)
    target = project / "01_知识库/数学变换/勒让德变换.md"
    sync_file(target, root=project)
    (project / "01_知识库/_索引/README.md").write_text("STALE", encoding="utf-8")
    result = check_file_workflow(target, root=project)
    payload = json.loads(format_json(result))
    assert payload["result"] == "INDEX_STALE"
    assert any(i["rule_id"] == "KI-STALE-002" for i in payload["stages"]["index"]["issues"])


def test_json_status_healthy(project: Path) -> None:
    write_reviewed_pair(project)
    sync_file(project / "01_知识库/数学变换/勒让德变换.md", root=project)
    payload = json.loads(format_json(status(root=project)))
    assert payload["target"] is None
    assert payload["result"] == "HEALTHY"


def test_text_status_report(project: Path) -> None:
    write_reviewed_pair(project)
    sync_file(project / "01_知识库/数学变换/勒让德变换.md", root=project)
    text = format_text(status(root=project))
    assert "[1/2] Full Knowledge validation" in text
    assert "HEALTHY" in text
    write_reviewed_pair(project)
    result = sync_file(project / "01_知识库/数学变换/勒让德变换.md", root=project)
    text = format_text(result)
    assert "Knowledge Workflow v1.0" in text
    assert "[1/3] File validation" in text
    assert "SUCCESS" in text
    summary = format_text(result, summary_only=True)
    assert "FILE: PASS" in summary
