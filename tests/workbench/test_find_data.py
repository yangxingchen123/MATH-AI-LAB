from pathlib import Path

from tools.workbench.find_data import find_contest_data


def test_find_data_writes_documents_not_literature(tmp_path: Path):
    project = tmp_path / "07_项目" / "美赛2026-A"
    (project / "documents").mkdir(parents=True)
    (project / "literature.md").write_text("# Literature\n", encoding="utf-8")

    def fetcher(_url: str) -> dict:
        raise OSError("offline")

    report = find_contest_data(
        name="美赛2026-A",
        repo_root=tmp_path,
        fetcher=fetcher,
    )
    assert report["status"] == "DEGRADED"
    written = Path(report["written"])
    assert written.is_file()
    assert "NASA PCoE" in written.read_text(encoding="utf-8")
    assert (project / "literature.md").read_text(encoding="utf-8") == "# Literature\n"


def test_find_data_rejects_missing_project(tmp_path: Path):
    report = find_contest_data(name="missing", repo_root=tmp_path)
    assert report["status"] == "REJECTED"
