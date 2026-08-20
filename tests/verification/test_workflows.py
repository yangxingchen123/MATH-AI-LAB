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
    assert "latex_build build" not in text
    assert "workspace_indexer sync" not in text
    assert "lualatex" not in text.lower()
    assert "pdflatex" not in text.lower()
    on = data.get("on")
    if on is True or on is None:
        on = data[True]
    assert "workflow_dispatch" in on
    paths = on["push"]["paths"]
    for required in (
        "04_LATEX/**",
        "tools/latex_build/**",
        "tests/latex_build/**",
        "tools/verification/**",
        "tests/verification/**",
        ".github/workflows/latex-smoke.yml",
    ):
        assert required in paths
    assert "cron" not in str(data)


def test_no_weekly_schedule_workflow() -> None:
    names = {p.name for p in WORKFLOWS.glob("*.yml")}
    assert "weekly.yml" not in names
