from tools.research_project.cli import main


def test_cli_check_readonly(tmp_project, capsys):
    code = main(["check", "--project", str(tmp_project)])
    assert code == 0
    out = capsys.readouterr().out
    assert "PASS" in out or "OK" in out


def test_cli_doctor_reports_contract_version(capsys):
    code = main(["doctor"])
    assert code == 0
    assert "1.1" in capsys.readouterr().out


def test_cli_status_mentions_freshness(tmp_project, capsys):
    code = main(["status", "--project", str(tmp_project)])
    assert code == 0
    out = capsys.readouterr().out.lower()
    assert "fresh" in out or "stale" in out or "reconcile_required" in out


def test_cli_add_claim_and_update_governance_help():
    assert main(["add-claim", "--help"]) == 0
    assert main(["update-governance", "--help"]) == 0
    assert main(["gate", "--help"]) == 0


def test_cli_doctor_requires_usage_guide(monkeypatch, capsys):
    from pathlib import Path

    monkeypatch.setattr(
        "tools.research_project.constants.USAGE_GUIDE_PATH",
        Path("10_提示词/Research_Project_Usage_Guide.md.MISSING"),
    )
    monkeypatch.setattr(
        "tools.research_project.service.USAGE_GUIDE_PATH",
        Path("10_提示词/Research_Project_Usage_Guide.md.MISSING"),
    )
    code = main(["doctor"])
    out = capsys.readouterr().out
    assert code != 0
    assert "Research_Project_Usage_Guide.md" in out
