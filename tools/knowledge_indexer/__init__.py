"""Knowledge Indexer v1.0 — derived index from validated Knowledge Metadata."""

from .constants import INDEXER_VERSION
from .models import IndexOperationResult, IndexResultKind, IndexerIssue
from .service import (
    build_from_validation,
    build_index,
    check_from_validation,
    check_index,
)

__all__ = [
    "INDEXER_VERSION",
    "IndexOperationResult",
    "IndexResultKind",
    "IndexerIssue",
    "build_from_validation",
    "build_index",
    "check_from_validation",
    "check_index",
]
__version__ = INDEXER_VERSION
