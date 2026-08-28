from pathlib import Path

from tools.workbench.coverage import audit_contest_coverage, write_coverage_report
from tools.workbench.evidence_candidates import write_evidence_candidates


def test_coverage_marks_questions_and_ocr(tmp_path: Path):
    project = tmp_path / "07_项目" / "P"
    project.mkdir(parents=True)
    (project / "problem.md").write_text(
        "## 要交付的问号\n\n"
        "1. **连续时间 SOC 模型.** body\n"
        "2. **Time-to-Empty.** body\n"
        "**OCR 损坏（不得补写）.** gap\n",
        encoding="utf-8",
    )
    (project / "evidence.md").write_text(
        "CLM-0001 连续时间 SOC tte_hours energy_balance\n",
        encoding="utf-8",
    )
    (project / "literature.md").write_text("# Literature\n", encoding="utf-8")
    tex = tmp_path / "04_LATEX" / "数学建模" / "P" / "P.tex"
    tex.parent.mkdir(parents=True)
    tex.write_text("\\section{Assumptions}\n\\section{The Model}\n", encoding="utf-8")
    report = audit_contest_coverage(project, tex)
    assert report["ocr_unresolved"] is True
    assert report["literature_records_present"] is False
    ids = {item["id"] for item in report["questions"]}
    assert ids == {"Q1", "Q2"}
    q1 = next(item for item in report["questions"] if item["id"] == "Q1")
    assert q1["covered"] is True
    _, path = write_coverage_report(project, tex)
    text = path.read_text(encoding="utf-8")
    assert "Q1 [COVERED]" in text
    assert "paper_complete: False" in text


def test_evidence_candidate_does_not_write_official_ledger(tmp_path: Path):
    project = tmp_path / "07_项目" / "P"
    (project / "documents").mkdir(parents=True)
    (project / "evidence.md").write_text(
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 BEGIN -->\n"
        "- status: OPEN\n---\nbody\n"
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 END -->\n",
        encoding="utf-8",
    )
    code = tmp_path / "05_代码" / "P"
    run = code / "outputs" / "soc-pipeline-001"
    run.mkdir(parents=True)
    (run / "metrics.json").write_text('{"tte_hours": 5.0}\n', encoding="utf-8")
    before = (project / "evidence.md").read_text(encoding="utf-8")
    written = write_evidence_candidates(project, code)
    assert written
    candidate = project / "documents" / "candidates" / "evd_soc-pipeline-001.md"
    assert candidate.is_file()
    assert (project / "evidence.md").read_text(encoding="utf-8") == before
    body = candidate.read_text(encoding="utf-8")
    assert "CANDIDATE ONLY" in body
    assert "ref=EVD-0001" in body
    assert "claim_ref: CLM-0001" in body
    assert "source_citation: run:05_代码/P/outputs/soc-pipeline-001" in body


def test_evidence_candidate_uses_next_free_evd(tmp_path: Path):
    project = tmp_path / "07_项目" / "P"
    (project / "documents").mkdir(parents=True)
    (project / "evidence.md").write_text(
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0005 BEGIN -->\n"
        "- claim_ref: CLM-0001\n- polarity: SUPPORT\n- kind: COMPUTATION\n---\n"
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=EVIDENCE ref=EVD-0005 END -->\n"
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 BEGIN -->\n"
        "- status: OPEN\n---\nbody\n"
        "<!-- MATH-AI-LAB:RESEARCH-RECORD type=CLAIM ref=CLM-0001 END -->\n",
        encoding="utf-8",
    )
    code = tmp_path / "05_代码" / "P"
    run = code / "outputs" / "soc-new-001"
    run.mkdir(parents=True)
    (run / "metrics.json").write_text('{"tte_hours": 5.0}\n', encoding="utf-8")
    write_evidence_candidates(project, code)
    body = (project / "documents" / "candidates" / "evd_soc-new-001.md").read_text(
        encoding="utf-8"
    )
    assert "ref=EVD-0006" in body


def test_evidence_candidate_skips_run_already_in_ledger(tmp_path: Path):
    project = tmp_path / "07_项目" / "P"
    (project / "documents").mkdir(parents=True)
    (project / "evidence.md").write_text(
        "soc-pipeline-001 already cited\n",
        encoding="utf-8",
    )
    code = tmp_path / "05_代码" / "P"
    run = code / "outputs" / "soc-pipeline-001"
    run.mkdir(parents=True)
    (run / "metrics.json").write_text('{"tte_hours": 5.0}\n', encoding="utf-8")
    assert write_evidence_candidates(project, code) == []
