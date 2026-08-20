from __future__ import annotations

import json
from pathlib import Path

from tools.knowledge_workflow.cli import run

from tests.knowledge_indexer.conftest import write_knowledge, write_reviewed_pair


def test_cli_sync_check_status(project: Path, capsys) -> None:
    write_reviewed_pair(project)
    path = str(project / "01_知识库/数学变换/勒让德变换.md")
    code = run(["sync", path, "--root", str(project)])
    assert code == 0
    out = capsys.readouterr().out
    assert "SUCCESS" in out

    code = run(["check", path, "--root", str(project), "--format", "json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["result"] == "SUCCESS"

    code = run(["status", "--root", str(project), "--summary"])
    assert code == 0
    assert "HEALTHY" in capsys.readouterr().out


def test_cli_strict_warnings(project: Path, capsys) -> None:
    write_knowledge(project, "01_知识库/a.md", kid="K0001", extras="prerequisites:\n  - K0002")
    write_knowledge(project, "01_知识库/b.md", kid="K0002")
    path = str(project / "01_知识库/a.md")
    code = run(["sync", path, "--root", str(project)])
    assert code == 0
    capsys.readouterr()
    code = run(["sync", path, "--root", str(project), "--strict-warnings"])
    assert code == 1


def test_cli_json_status(project: Path, capsys) -> None:
    write_reviewed_pair(project)
    path = str(project / "01_知识库/优化理论/凸函数.md")
    run(["sync", path, "--root", str(project)])
    capsys.readouterr()
    code = run(["status", "--root", str(project), "--format", "json"])
    assert code == 0
    json.loads(capsys.readouterr().out)
