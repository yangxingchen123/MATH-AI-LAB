from pathlib import Path

from tools.reference_library.ingest import doctor, ingest_paper


def test_doctor_reports_taxonomy(tmp_path: Path):
    report = doctor(repo_root=tmp_path)
    assert report["core_impact"] is False
    assert report["status"] == "DEGRADED"
    (tmp_path / "03_参考资料" / "教材").mkdir(parents=True)
    (tmp_path / "03_参考资料" / "论文").mkdir()
    (tmp_path / "03_参考资料" / "竞赛").mkdir()
    (tmp_path / "03_参考资料" / "讲义").mkdir()
    assert doctor(repo_root=tmp_path)["status"] == "PASS"


def test_ingest_paper_writes_identity(tmp_path: Path):
    template = tmp_path / "03_参考资料" / "_模板" / "文献条目_v1.md"
    template.parent.mkdir(parents=True)
    template.write_text(
        "# {{TITLE}}\n- slug: {{SLUG}}\n- domain: {{DOMAIN}}\n"
        "- identity_kind: {{IDENTITY_KIND}}\n- source_path: {{SOURCE_PATH}}\n"
        "- source_sha256: {{SOURCE_SHA256}}\n- parse_status: NONE\n",
        encoding="utf-8",
        newline="\n",
    )
    pdf = tmp_path / "sample.pdf"
    pdf.write_bytes(b"%PDF-1.1 fake")
    result = ingest_paper(
        slug="demo-paper",
        title="Demo",
        domain="optimization",
        pdf=pdf,
        repo_root=tmp_path,
    )
    assert result.status == "WRITTEN"
    assert result.parse_status == "DEGRADED"
    assert result.source_sha256
    identity = tmp_path / "03_参考资料" / "论文" / "optimization" / "demo-paper" / "identity.md"
    assert identity.is_file()
    text = identity.read_text(encoding="utf-8")
    assert "Demo" in text
    assert (identity.parent / "source.pdf").is_file()


def test_ingest_rejects_path_escape(tmp_path: Path):
    result = ingest_paper(
        slug="../evil",
        title="x",
        domain="optimization",
        repo_root=tmp_path,
    )
    assert result.status == "REJECTED"
