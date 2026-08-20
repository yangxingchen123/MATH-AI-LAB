import json
from pathlib import Path

from tools.problem_candidate_gate.cli import run

from .conftest import problem_md


def test_cli_check(project: Path, capsys) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    code = run(["check", "--root", str(project)])
    out = capsys.readouterr().out
    assert code == 0
    assert "Problem Candidate Gate v0.1" in out
    assert "PASS" in out


def test_cli_check_file(project: Path, capsys) -> None:
    path = project / "02_题目库" / "a.md"
    path.write_text(problem_md(), encoding="utf-8")
    code = run(["check-file", str(path), "--root", str(project), "--format", "text"])
    assert code == 0
    assert "PASS" in capsys.readouterr().out


def test_cli_status(project: Path, capsys) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    code = run(["status", "--root", str(project), "--summary"])
    out = capsys.readouterr().out
    assert code == 0
    assert "READY" in out or "PASS" in out


def test_cli_format_json(project: Path, capsys) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    code = run(["check", "--root", str(project), "--format", "json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["gate_version"] == "0.1"


def test_cli_verbose(project: Path, capsys) -> None:
    (project / "02_题目库" / "a.md").write_text(problem_md(), encoding="utf-8")
    code = run(["check", "--root", str(project), "--verbose"])
    assert code == 0
    out = capsys.readouterr().out
    assert "PCG-DISC-I001" in out
