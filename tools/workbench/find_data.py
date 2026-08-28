"""Search public catalogs for open-license dataset *candidates*."""

from __future__ import annotations

from pathlib import Path

from tools.open_data.discover import Fetcher, discover_open_data, write_candidates
from tools.research_project.constants import REPO_ROOT


def _safe_name(name: str) -> bool:
    if not name or name != name.strip():
        return False
    if any(item in name for item in ("/", "\\", "..", "\x00")):
        return False
    return True


def find_contest_data(
    *,
    name: str,
    queries: tuple[str, ...] | list[str] | None = None,
    repo_root: Path | None = None,
    fetcher: Fetcher | None = None,
    include_seeds: bool = True,
) -> dict:
    if not _safe_name(name):
        return {
            "status": "REJECTED",
            "core_impact": False,
            "message": "name must be a single path segment",
            "hits": [],
        }
    root = Path(repo_root or REPO_ROOT)
    project = root / "07_项目" / name
    if not project.is_dir():
        return {
            "status": "REJECTED",
            "core_impact": False,
            "message": "contest project missing",
            "hits": [],
        }
    report = discover_open_data(
        queries=queries,
        fetcher=fetcher,
        include_seeds=include_seeds,
    )
    path = write_candidates(project, report)
    out = dict(report)
    out["written"] = str(path)
    out["message"] = "wrote open-data candidates; not ingested as literature"
    return out
