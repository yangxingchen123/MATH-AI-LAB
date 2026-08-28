"""Static review of GitHub workflow files. Does not execute remote CI."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    return yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))


def test_core_workflow_is_thin_and_read_only() -> None:
    data = _load("core-verification.yml")
    text = (WORKFLOWS / "core-verification.yml").read_text(encoding="utf-8")
    assert "python -m tools.verification core" in text
    assert "workspace_indexer sync" not in text
    assert "workspace_indexer rebuild" not in text
    assert "latex_build build" not in text
    assert "matrix:" not in text
    jobs = data["jobs"]
    job = next(iter(jobs.values()))
    assert job["runs-on"] == "ubuntu-latest"


def test_latex_workflow_path_filters_and_smoke_command() -> None:
    data = _load("latex-smoke.yml")
    text = (WORKFLOWS / "latex-smoke.yml").read_text(encoding="utf-8")
    assert "python -m tools.verification latex-smoke" in text
    assert "04_LATEX/专题讲义/数学变换/勒让德变换" in text
    assert "python -m pytest -q tests/normal_operation/test_real_latex.py" in text
    assert "latex_build build" not in text
    assert "workspace_indexer sync" not in text
    assert "lualatex" not in text.lower()
    assert "pdflatex" not in text.lower()
    on = data.get("on")
    if on is True or on is None:
        on = data[True]
    assert "workflow_dispatch" in on
    push_paths = on["push"]["paths"]
    pr_paths = on["pull_request"]["paths"]
    for required in (
        "04_LATEX/**",
        "tools/latex_build/**",
        "tests/latex_build/**",
        "tools/verification/**",
        "tests/verification/**",
        "tests/normal_operation/test_real_latex.py",
        ".github/workflows/latex-smoke.yml",
    ):
        assert required in push_paths
        assert required in pr_paths
    assert "cron" not in str(data)


def test_no_weekly_schedule_workflow() -> None:
    names = {p.name for p in WORKFLOWS.glob("*.yml")}
    assert "weekly.yml" not in names


def test_dossier_smoke_workflow_contract():
    text = Path(".github/workflows/dossier-smoke.yml").read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    on = data.get("on")
    if on is None and True in data:
        on = data[True]
    assert isinstance(on, dict)
    assert "pull_request" in on and "push" in on
    paths = set()
    for event in ("pull_request", "push"):
        cfg = on[event]
        if isinstance(cfg, dict):
            paths.update(cfg.get("paths", []))
    required = {
        "tools/research_project/**",
        "tools/source_io/**",
        "tests/research_project/**",
        "tests/verification/**",
        "07_项目/**",
        "docs/superpowers/specs/**",
        "docs/superpowers/plans/**v1.1-research-project*",
        ".github/workflows/dossier-smoke.yml",
        "requirements.txt",
    }
    assert required <= paths
    assert "fetch-depth: 0" in text or "fetch-depth:0" in text.replace(" ", "")
    assert "python-version: \"3.13\"" in text or "python-version: '3.13'" in text
    assert "requirements.txt" in text
    assert "tests/research_project" in text
    assert "tools.research_project gate" in text or "research_project gate" in text
    assert "check-append-only" in text and "--all" in text
    assert "pull_request.base.sha" in text
    assert "github.event.before" in text
    assert "0000000000000000000000000000000000000000" in text
    assert "texlive" not in text.lower()
    assert "mineru" not in text.lower()
    assert "leanprover" not in text.lower()
    assert "upload-artifact" in text.lower() or "actions/upload-artifact" in text
