from pathlib import Path

from tools.workbench.pipeline import run_contest_pipeline


def _scaffold(tmp_path: Path, name: str) -> None:
    project = tmp_path / "07_项目" / name
    for folder in ("documents", "runs", "artifacts", "reviews"):
        (project / folder).mkdir(parents=True)
    (project / "reviews" / "reviews.md").write_text("# Reviews\n", encoding="utf-8")
    (project / "research_dossier.md").write_text(
        "# T\n\n<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED BEGIN -->\n"
        "<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED END -->\n",
        encoding="utf-8",
    )
    (project / "assumptions.md").write_text("# Assumptions\n", encoding="utf-8")
    (project / "evidence.md").write_text("# Evidence\n", encoding="utf-8")
    (project / "decisions.md").write_text("# Decisions\n", encoding="utf-8")
    (project / "negative_results.md").write_text("# Negative\n", encoding="utf-8")
    (project / "governance.md").write_text(
        "# Governance\n\n"
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=GOVERNANCE ref=GOV-0001 BEGIN -->\n"
        "- project_data_level: PERSONAL\n"
        "- external_processing_authorized: false\n"
        "- license_status: LOCAL_ONLY\n"
        "---\n"
        "gov\n"
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=GOVERNANCE ref=GOV-0001 END -->\n",
        encoding="utf-8",
    )
    (project / "literature.md").write_text("# Literature\n", encoding="utf-8")
    code = tmp_path / "05_代码" / name
    (code / "configs").mkdir(parents=True)
    (code / "outputs").mkdir()
    (code / "configs" / "candidates.yaml").write_text(
        "candidates:\n"
        "  - name: energy_balance_soc\n"
        "    target_question: q\n"
        "    why: because\n"
        "    data_requirement: none\n"
        "    identifiable_when: always\n"
        "    falsifiable_when: never\n",
        encoding="utf-8",
    )
    tex_dir = tmp_path / "04_LATEX" / "数学建模" / name
    tex_dir.mkdir(parents=True)
    (tex_dir / f"{name}.tex").write_text("% draft\n", encoding="utf-8")


def test_pipeline_runs_auto_steps_and_keeps_human_gates(tmp_path: Path):
    name = "ContestA"
    _scaffold(tmp_path, name)

    project = tmp_path / "07_项目" / name
    evidence_before = (project / "evidence.md").read_text(encoding="utf-8")

    def fetcher(_url: str) -> dict:
        raise OSError("offline")

    report = run_contest_pipeline(
        name=name,
        repo_root=tmp_path,
        fetcher=fetcher,
        engines=("soc",),
    )
    assert report["status"] == "INCOMPLETE"
    assert report["core_impact"] is False
    assert report["paper_complete"] is False
    assert (project / "documents" / "pipeline_report.md").is_file()
    assert (project / "documents" / "coverage.md").is_file()
    assert (project / "literature.md").read_text(encoding="utf-8") == "# Literature\n"
    assert (project / "evidence.md").read_text(encoding="utf-8") == evidence_before
    assert not (tmp_path / "08_成果输出").exists()
    names = [item["name"] for item in report["steps"]]
    assert "select" in names
    assert "experiment:soc" in names
    assert "coverage" in names
    assert "evidence_candidates" in names
    assert report["human_gates"]
    assert report["paper_complete"] is False


def test_pipeline_skips_existing_run(tmp_path: Path):
    name = "ContestA"
    _scaffold(tmp_path, name)
    first = run_contest_pipeline(
        name=name,
        repo_root=tmp_path,
        fetcher=lambda _url: {"hits": {"hits": []}},
        engines=("soc",),
        include_seeds=False,
    )
    second = run_contest_pipeline(
        name=name,
        repo_root=tmp_path,
        fetcher=lambda _url: {"hits": {"hits": []}},
        engines=("soc",),
        include_seeds=False,
    )
    exp = [item for item in second["steps"] if item["name"] == "experiment:soc"][0]
    assert first["status"] == "INCOMPLETE"
    assert exp["status"] == "SKIPPED"


def test_pipeline_rejects_missing_scaffold(tmp_path: Path):
    report = run_contest_pipeline(name="missing", repo_root=tmp_path)
    assert report["status"] == "REJECTED"
    assert report["paper_complete"] is False
