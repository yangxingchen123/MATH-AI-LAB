"""Fixtures for Knowledge Workflow tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.knowledge_indexer.conftest import write_knowledge, write_reviewed_pair
from tests.knowledge_validator.conftest import knowledge_md, write_project


@pytest.fixture
def project(tmp_path: Path) -> Path:
    return write_project(tmp_path)


__all__ = ["knowledge_md", "write_knowledge", "write_project", "write_reviewed_pair"]
