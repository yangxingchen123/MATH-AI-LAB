"""Open-data catalog discovery sidecar (not Frozen Schema)."""

from .discover import discover_open_data, write_candidates
from .licenses import classify_license

__all__ = ["classify_license", "discover_open_data", "write_candidates"]
