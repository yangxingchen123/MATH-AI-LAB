from pathlib import Path

from tools.workbench.attach import attach_contest_md


def _identity(repo: Path) -> Path:
    dest = repo / "03_参考资料" / "竞赛" / "美赛" / "2026-A"
    dest.mkdir(parents=True)
    path = dest / "identity.md"
    path.write_text(
        "# 2026 MCM Problem A\n- slug: 2026-A\n- parse_status: DEGRADED\n- notes: none\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def test_attach_md_copies_derived_and_hashes(tmp_path: Path):
    identity = _identity(tmp_path)
    md = tmp_path / "problem.md"
    md.write_text("2026 MCM Problem A\nYour task is to model SOC.\n", encoding="utf-8")
    result = attach_contest_md(
        contest="美赛",
        slug="2026-A",
        md=md,
        repo_root=tmp_path,
    )
    assert result.status == "WRITTEN"
    stored = tmp_path / "03_参考资料" / "竞赛" / "美赛" / "2026-A" / "derived" / "problem.md"
    assert stored.is_file()
    text = identity.read_text(encoding="utf-8")
    assert "derived_md:" in text
    assert "derived_sha256:" in text
    assert len(result.derived_sha256) == 64


def test_attach_md_is_noop_when_hash_matches(tmp_path: Path):
    _identity(tmp_path)
    md = tmp_path / "problem.md"
    md.write_text("same body\n", encoding="utf-8")
    first = attach_contest_md(contest="美赛", slug="2026-A", md=md, repo_root=tmp_path)
    second = attach_contest_md(contest="美赛", slug="2026-A", md=md, repo_root=tmp_path)
    assert first.status == "WRITTEN"
    assert second.status == "NO_OP"


def test_attach_md_updates_identity_when_derived_already_copied(tmp_path: Path):
    identity = _identity(tmp_path)
    md = tmp_path / "problem.md"
    md.write_text("already copied\n", encoding="utf-8")
    derived = tmp_path / "03_参考资料" / "竞赛" / "美赛" / "2026-A" / "derived"
    derived.mkdir(parents=True)
    (derived / "problem.md").write_text("already copied\n", encoding="utf-8")
    result = attach_contest_md(contest="美赛", slug="2026-A", md=md, repo_root=tmp_path)
    assert result.status == "WRITTEN"
    assert "derived_sha256:" in identity.read_text(encoding="utf-8")


def test_attach_md_rejects_missing_identity(tmp_path: Path):
    md = tmp_path / "problem.md"
    md.write_text("x\n", encoding="utf-8")
    result = attach_contest_md(contest="美赛", slug="2026-A", md=md, repo_root=tmp_path)
    assert result.status == "REJECTED"
