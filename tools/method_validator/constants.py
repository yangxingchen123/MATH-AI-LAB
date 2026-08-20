"""Stable constants for Method Validator v1 (Frozen Method Schema v1)."""

from __future__ import annotations

VALIDATOR_VERSION = "1"
SCHEMA_OBJECT_TYPE = "method"
SCHEMA_VERSION = 1
SCHEMA_STATUS = "frozen"
SCHEMA_FROZEN_DATE = "2026-08-20"

METHOD_DIR_NAME = "12_方法库"
SCHEMA_MARKER_FILE = "元数据规范.md"

ID_PATTERN = r"^M\d{4}$"
KNOWLEDGE_ID_PATTERN = r"^K\d{4}$"
RESERVED_METHOD_ID = "M0000"
RESERVED_KNOWLEDGE_ID = "K0000"
ALLOWED_STATUSES = frozenset({"draft", "reviewed", "archived"})

FROZEN_FIELDS = frozenset(
    {
        "schema_version",
        "id",
        "type",
        "title",
        "status",
        "knowledge",
    }
)

RULES: dict[str, tuple[str, str]] = {
    "M-DISC-E001": ("ERROR", "Invalid project root"),
    "M-DISC-E002": ("ERROR", "Invalid check-file target"),
    "M-DISC-E003": ("ERROR", "Method directory not found"),
    "M-PARSE-E001": ("ERROR", "YAML Front Matter cannot be parsed"),
    "M-PARSE-E002": ("ERROR", "Missing closing Front Matter delimiter"),
    "M-PARSE-E003": ("ERROR", "YAML root is not a mapping"),
    "M-PARSE-E004": ("ERROR", "Duplicate YAML key"),
    "M-PARSE-E005": ("ERROR", "Missing YAML Front Matter"),
    "M-BASE-E001": ("ERROR", "schema_version missing"),
    "M-BASE-E002": ("ERROR", "schema_version must be integer 1"),
    "M-BASE-E010": ("ERROR", "Invalid Method ID"),
    "M-BASE-E011": ("ERROR", "Real object uses reserved ID M0000"),
    "M-BASE-E012": ("ERROR", "id missing"),
    "M-BASE-E020": ("ERROR", "type missing"),
    "M-BASE-E021": ("ERROR", "type must be method"),
    "M-BASE-E030": ("ERROR", "title missing or empty"),
    "M-ID-E001": ("ERROR", "Duplicate Method ID"),
    "M-STATE-E001": ("ERROR", "Invalid status"),
    "M-FIELD-E001": ("ERROR", "Unknown metadata field"),
    "M-KNOW-E001": ("ERROR", "knowledge must be a list of Knowledge IDs"),
    "M-KNOW-E002": ("ERROR", "knowledge empty list is invalid; omit field instead"),
    "M-KNOW-E003": ("ERROR", "Invalid Knowledge target ID"),
    "M-KNOW-E004": ("ERROR", "Knowledge target uses reserved ID K0000"),
    "M-KNOW-E005": ("ERROR", "Duplicate Knowledge target"),
    "M-KNOW-E006": ("ERROR", "Knowledge target does not exist"),
    "M-KNOW-E007": ("ERROR", "Knowledge target type is not knowledge"),
    "M-KNOW-E010": ("ERROR", "Knowledge dependency validation failed"),
}
