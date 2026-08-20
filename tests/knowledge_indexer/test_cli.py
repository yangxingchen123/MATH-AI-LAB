from __future__ import annotations

import json
from pathlib import Path

from tools.knowledge_indexer.cli import run
from tools.knowledge_indexer.models import IndexResultKind
from tools.knowledge_indexer.service import build_index

from .conftest import write_knowledge, write_reviewed_pair


def test_cli_build_and_check(project: Path, capsys) -> None:
    write_reviewed_pair(project)
    code = run(["build", "--root", str(project)])
    assert code == 0
    out = capsys.readouterr().out
    assert "BUILT" in out or "UP_TO_DATE" in out

    code2 = run(["check", "--root", str(project), "--format", "json"])
    assert code2 == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["result"] == "CURRENT"


def test_cli_summary(project: Path, capsys) -> None:
    write_reviewed_pair(project)
    build_index(root=project)
    code = run(["check", "--root", str(project), "--summary"])
    assert code == 0
    assert "CURRENT" in capsys.readouterr().out


def test_strict_warnings(project: Path) -> None:
    write_knowledge(project, "01_知识库/a.md", kid="K0001", extras="prerequisites:\n  - K0002")
    write_knowledge(project, "01_知识库/b.md", kid="K0002")
    op_ok = build_index(root=project, strict_warnings=False)
    assert op_ok.result == IndexResultKind.BUILT
    # recreate clean
    import shutil

    shutil.rmtree(project / "01_知识库" / "_索引", ignore_errors=True)
    op_fail = build_index(root=project, strict_warnings=True)
    assert op_fail.result == IndexResultKind.FAIL
    assert any(i.rule_id == "KI-VALIDATE-002" for i in op_fail.issues)
