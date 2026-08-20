"""Workspace Indexer v1.2 — derived workspace views."""

from .constants import INDEXER_VERSION
from .models import IndexOperationResult, IndexResultKind, WorkspaceSnapshot
from .service import build_expected_outputs, build_workspace_snapshot_from_root, check_index, rebuild_index, sync_index

__all__ = [
    "INDEXER_VERSION",
    "IndexOperationResult",
    "IndexResultKind",
    "WorkspaceSnapshot",
    "build_expected_outputs",
    "build_workspace_snapshot_from_root",
    "check_index",
    "rebuild_index",
    "sync_index",
]
__version__ = INDEXER_VERSION
