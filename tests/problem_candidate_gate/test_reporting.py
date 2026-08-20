import json
from pathlib import Path

from tools.problem_candidate_gate.cli import run
from tools.problem_candidate_gate.readiness import check_file, check_project, status_project
from tools.problem_candidate_gate.report import format_json

from .conftest import problem_md


def test_check_json_parse(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    r = check_project(root=project)
    payload = json.loads(format_json(r, include_readiness=False))
    assert payload["gate_version"] == "0.1"
    assert payload["candidate_schema"]["status"] == "candidate"
    assert "issues" in payload
    assert payload["automated_gates"]["result"] == "PASS"


def test_check_file_json_parse(project: Path) -> None:
    path = project / "02_题目库" / "a.md"
    path.write_text(problem_md(), encoding="utf-8")
    r = check_file(path, root=project)
    payload = json.loads(format_json(r, include_readiness=False))
    assert payload["summary"]["result"] in {"PASS", "FAIL"}


def test_status_json_parse(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    r = status_project(root=project)
    payload = json.loads(format_json(r, include_readiness=True))
    assert "manual_review_items" in payload
    assert payload["result"] in {
        "READY_FOR_FINAL_REVIEW",
        "READY_WITH_WARNINGS",
        "NOT_READY",
    }
    assert all("rule_id" in i for i in payload["issues"])


def test_cli_json_roundtrip(project: Path) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    code = run(["status", "--root", str(project), "--format", "json"])
    assert code == 0
