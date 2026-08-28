"""v1.4 Modeling framework constants. Engines stay out of root requirements."""

from __future__ import annotations

CONTRACT_VERSION = "1.4"
REQUIRED_MANIFEST_FIELDS: tuple[str, ...] = (
    "run_id",
    "status",
    "command",
    "inputs",
    "config_sha256",
    "environment",
    "randomness",
    "outputs",
)

ALLOWED_STATUS = frozenset(
    {"QUEUED", "RUNNING", "SUCCEEDED", "PARTIAL", "FAILED", "CANCELLED"}
)
SHA256_LEN = 64
