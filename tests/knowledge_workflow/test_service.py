from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from tools.knowledge_indexer import IndexOperationResult, IndexResultKind, IndexerIssue, build_index
from tools.knowledge_workflow.constants import (
    RESULT_FILE_VALIDATION_FAILED,
    RESULT_FULL_VALIDATION_FAILED,
    RESULT_HEALTHY,
    RESULT_INDEX_BUILD_FAILED,
    RESULT_INDEX_MISSING,
    RESULT_INDEX_STALE,
    RESULT_SUCCESS,
    STAGE_FAIL,
    STAGE_PASS,
    STAGE_SKIPPED,
)
from tools.knowledge_workflow.service import check_file_workflow, status, sync_file

from tests.knowledge_indexer.conftest import write_knowledge, write_reviewed_pair


def test_sync_success(project: Path) -> None:
    write_reviewed_pair(project)
    path = project / "01_知识库/数学变换/勒让德变换.md"
    result = sync_file(path, root=project)
    assert result.result == RESULT_SUCCESS
    assert result.stages["file_validation"].status == STAGE_PASS
    assert result.stages["full_validation"].status == STAGE_PASS
    assert result.stages["index"].detail in ("BUILT", "UP_TO_DATE")
    assert (project / "01_知识库/_索引/knowledge_index.json").is_file()


def test_file_validation_fail_skips_and_preserves_index(project: Path) -> None:
    write_reviewed_pair(project)
    build_index(root=project)
    index_readme = project / "01_知识库/_索引/README.md"
    index_readme.write_text("OLD", encoding="utf-8")

    bad = project / "01_知识库/bad.md"
    write_knowledge(project, "01_知识库/bad.md", kid="K00A1")
    result = sync_file(bad, root=project)
    assert result.result == RESULT_FILE_VALIDATION_FAILED
    assert result.stages["file_validation"].status == STAGE_FAIL
    assert result.stages["full_validation"].status == STAGE_SKIPPED
    assert result.stages["index"].status == STAGE_SKIPPED
    assert index_readme.read_text(encoding="utf-8") == "OLD"
    assert any(i.rule_id == "K-BASE-010" for i in result.stages["file_validation"].issues)


def test_target_ok_but_full_library_fails(project: Path) -> None:
    write_reviewed_pair(project)
    build_index(root=project)
    old = (project / "01_知识库/_索引/README.md").read_text(encoding="utf-8")
    write_knowledge(
        project,
        "01_知识库/broken.md",
        kid="K0009",
        status="reviewed",
        aliases="",
        extras="prerequisites: []\nrelated: []",
    )
    target = project / "01_知识库/数学变换/勒让德变换.md"
    result = sync_file(target, root=project)
    assert result.stages["file_validation"].status == STAGE_PASS
    assert result.stages["full_validation"].status == STAGE_FAIL
    assert result.stages["index"].status == STAGE_SKIPPED
    assert result.result == RESULT_FULL_VALIDATION_FAILED
    assert (project / "01_知识库/_索引/README.md").read_text(encoding="utf-8") == old


def test_sync_rebuilds_stale_index(project: Path) -> None:
    write_reviewed_pair(project)
    build_index(root=project)
    (project / "01_知识库/_索引/README.md").write_text("STALE", encoding="utf-8")
    target = project / "01_知识库/数学变换/勒让德变换.md"
    result = sync_file(target, root=project)
    assert result.result == RESULT_SUCCESS
    assert result.stages["index"].detail == "BUILT"


def test_sync_up_to_date(project: Path) -> None:
    write_reviewed_pair(project)
    target = project / "01_知识库/优化理论/凸函数.md"
    assert sync_file(target, root=project).stages["index"].detail == "BUILT"
    second = sync_file(target, root=project)
    assert second.result == RESULT_SUCCESS
    assert second.stages["index"].detail == "UP_TO_DATE"


def test_check_current_does_not_write(project: Path) -> None:
    write_reviewed_pair(project)
    target = project / "01_知识库/数学变换/勒让德变换.md"
    sync_file(target, root=project)
    before = {
        p: p.read_bytes()
        for p in (project / "01_知识库/_索引").iterdir()
        if p.is_file()
    }
    result = check_file_workflow(target, root=project)
    assert result.result == RESULT_SUCCESS
    assert result.stages["index"].detail == "CURRENT"
    after = {
        p: p.read_bytes()
        for p in (project / "01_知识库/_索引").iterdir()
        if p.is_file()
    }
    assert before == after


def test_check_stale_does_not_build(project: Path) -> None:
    write_reviewed_pair(project)
    target = project / "01_知识库/数学变换/勒让德变换.md"
    sync_file(target, root=project)
    (project / "01_知识库/_索引/README.md").write_text("STALE", encoding="utf-8")
    result = check_file_workflow(target, root=project)
    assert result.result == RESULT_INDEX_STALE
    assert result.stages["file_validation"].status == STAGE_PASS
    assert result.stages["full_validation"].status == STAGE_PASS
    assert any(i.rule_id == "KI-STALE-002" for i in result.stages["index"].issues)
    assert (project / "01_知识库/_索引/README.md").read_text(encoding="utf-8") == "STALE"


def test_status_healthy(project: Path) -> None:
    write_reviewed_pair(project)
    sync_file(project / "01_知识库/数学变换/勒让德变换.md", root=project)
    result = status(root=project)
    assert result.result == RESULT_HEALTHY
    assert result.target is None


def test_status_stale(project: Path) -> None:
    write_reviewed_pair(project)
    sync_file(project / "01_知识库/数学变换/勒让德变换.md", root=project)
    (project / "01_知识库/_索引/extra.txt").write_text("x", encoding="utf-8")
    result = status(root=project)
    assert result.result == RESULT_INDEX_STALE


def test_reject_template(project: Path) -> None:
    result = sync_file(project / "01_知识库/知识库模板.md", root=project)
    assert result.result == RESULT_FILE_VALIDATION_FAILED
    assert any(i.rule_id == "KW-FILE-001" for i in result.stages["file_validation"].issues)


def test_reject_generated_index(project: Path) -> None:
    write_reviewed_pair(project)
    sync_file(project / "01_知识库/数学变换/勒让德变换.md", root=project)
    result = sync_file(project / "01_知识库/_索引/README.md", root=project)
    assert any(i.rule_id == "KW-FILE-001" for i in result.stages["file_validation"].issues)


def test_reject_outside_knowledge(project: Path) -> None:
    other = project / "02_题目库"
    other.mkdir()
    path = other / "x.md"
    path.write_text("# x\n", encoding="utf-8")
    result = sync_file(path, root=project)
    assert any(i.rule_id == "KW-FILE-001" for i in result.stages["file_validation"].issues)


def test_missing_file(project: Path) -> None:
    result = sync_file(project / "01_知识库/nope.md", root=project)
    assert any(i.rule_id == "KW-FILE-002" for i in result.stages["file_validation"].issues)


def test_reject_non_md(project: Path) -> None:
    path = project / "01_知识库/note.txt"
    path.write_text("x", encoding="utf-8")
    result = sync_file(path, root=project)
    assert any(i.rule_id == "KW-FILE-001" for i in result.stages["file_validation"].issues)


def test_strict_warnings(project: Path) -> None:
    write_knowledge(project, "01_知识库/a.md", kid="K0001", extras="prerequisites:\n  - K0002")
    write_knowledge(project, "01_知识库/b.md", kid="K0002")
    target = project / "01_知识库/a.md"
    ok = sync_file(target, root=project, strict_warnings=False)
    assert ok.result == RESULT_SUCCESS
    blocked = sync_file(target, root=project, strict_warnings=True)
    assert blocked.result == RESULT_FILE_VALIDATION_FAILED


def test_index_build_failure_keeps_ki_rule(project: Path) -> None:
    write_reviewed_pair(project)
    target = project / "01_知识库/数学变换/勒让德变换.md"
    fail_op = IndexOperationResult(
        result=IndexResultKind.FAIL,
        project_root=str(project),
        index_dir="01_知识库/_索引",
    )
    fail_op.issues.append(
        IndexerIssue(severity="ERROR", rule_id="KI-PUBLISH-001", message="simulated")
    )
    with patch(
        "tools.knowledge_workflow.service.build_from_validation",
        return_value=fail_op,
    ):
        result = sync_file(target, root=project)
    assert result.result == RESULT_INDEX_BUILD_FAILED
    assert result.stages["file_validation"].status == STAGE_PASS
    assert result.stages["full_validation"].status == STAGE_PASS
    assert result.stages["index"].status == STAGE_FAIL
    assert any(i.rule_id == "KI-PUBLISH-001" and i.source == "indexer" for i in result.stages["index"].issues)


def test_source_protection(project: Path) -> None:
    write_reviewed_pair(project)
    sources = {
        p: p.read_bytes()
        for p in (project / "01_知识库").rglob("*.md")
        if "_索引" not in p.parts
    }
    sync_file(project / "01_知识库/数学变换/勒让德变换.md", root=project)
    for p, content in sources.items():
        assert p.read_bytes() == content


def test_check_missing_index(project: Path) -> None:
    write_reviewed_pair(project)
    result = check_file_workflow(project / "01_知识库/数学变换/勒让德变换.md", root=project)
    assert result.result == RESULT_INDEX_MISSING
    assert not (project / "01_知识库/_索引").exists()
