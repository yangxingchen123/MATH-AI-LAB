from pathlib import Path

from tools.reference_library.ingest import ingest_contest


def test_ingest_contest_writes_identity(tmp_path: Path):
    template = tmp_path / "03_参考资料" / "_模板" / "文献条目_v1.md"
    template.parent.mkdir(parents=True)
    template.write_text(
        "# {{TITLE}}\n- slug: {{SLUG}}\n- domain: {{DOMAIN}}\n"
        "- source_path: {{SOURCE_PATH}}\n- source_sha256: {{SOURCE_SHA256}}\n"
        "- parse_status: NONE\n",
        encoding="utf-8",
        newline="\n",
    )
    result = ingest_contest(
        contest="MCM",
        slug="2026-A",
        title="Problem A",
        repo_root=tmp_path,
    )
    assert result.status == "WRITTEN"
    identity = tmp_path / "03_参考资料" / "竞赛" / "MCM" / "2026-A" / "identity.md"
    assert identity.is_file()
    assert "Problem A" in identity.read_text(encoding="utf-8")


def test_ingest_contest_rejects_escape(tmp_path: Path):
    result = ingest_contest(contest="../x", slug="a", title="t", repo_root=tmp_path)
    assert result.status == "REJECTED"
