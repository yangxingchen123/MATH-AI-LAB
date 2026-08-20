from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from tools.knowledge_indexer.models import IndexResultKind, RenderedIndex
from tools.knowledge_indexer.publisher import PublishError, publish_index
from tools.knowledge_indexer.service import build_index

from .conftest import write_reviewed_pair


def test_publish_replaces_old(project: Path) -> None:
    write_reviewed_pair(project)
    index = project / "01_知识库" / "_索引"
    index.mkdir(parents=True)
    (index / "README.md").write_text("OLD", encoding="utf-8")
    op = build_index(root=project)
    assert op.result == IndexResultKind.BUILT
    assert (index / "README.md").read_text(encoding="utf-8") != "OLD"
    assert (index / "knowledge_index.json").is_file()


def test_publish_rollback_on_swap_failure(project: Path) -> None:
    write_reviewed_pair(project)
    # First successful build
    assert build_index(root=project).result == IndexResultKind.BUILT
    index = project / "01_知识库" / "_索引"
    old_readme = (index / "README.md").read_text(encoding="utf-8")

    # Force failure on second replace (temp -> index)
    real_replace = __import__("os").replace

    def flaky_replace(src, dst):
        if "._索引_build_" in str(src):
            raise OSError("simulated swap failure")
        return real_replace(src, dst)

    rendered = RenderedIndex(
        files={
            "README.md": "NEW_SHOULD_NOT_PUBLISH",
            "按领域.md": "x",
            "关系索引.md": "y",
            "knowledge_index.json": '{"index_version": 1, "knowledge": {}}',
        }
    )
    with patch("tools.knowledge_indexer.publisher.os.replace", side_effect=flaky_replace):
        with pytest.raises(PublishError):
            publish_index(project, rendered)

    assert index.is_dir()
    assert (index / "README.md").read_text(encoding="utf-8") == old_readme
