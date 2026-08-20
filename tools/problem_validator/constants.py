"""Stable constants for Problem Validator v1 (Frozen Problem Schema v1)."""

from __future__ import annotations

VALIDATOR_VERSION = "1"
SCHEMA_OBJECT_TYPE = "problem"
SCHEMA_VERSION = 1
SCHEMA_STATUS = "frozen"
SCHEMA_FROZEN_DATE = "2026-08-19"

PROBLEM_DIR_NAME = "02_题目库"
KNOWLEDGE_DIR_NAME = "01_知识库"
SCHEMA_MARKER_FILE = "元数据规范.md"
TEMPLATE_RELATIVE_PATH = "02_题目库/题目模板.md"

ID_PATTERN = r"^P\d{4}$"
KNOWLEDGE_ID_PATTERN = r"^K\d{4}$"
RESERVED_PROBLEM_ID = "P0000"
RESERVED_KNOWLEDGE_ID = "K0000"
ALLOWED_STATUSES = frozenset({"draft", "reviewed", "archived"})

FROZEN_FIELDS = frozenset(
    {
        "schema_version",
        "id",
        "type",
        "title",
        "status",
        "created",
        "updated",
        "knowledge",
        "parts",
    }
)

RULES: dict[str, tuple[str, str]] = {
    "P-DISC-E001": ("ERROR", "Invalid project root"),
    "P-DISC-E002": ("ERROR", "Invalid check-file target"),
    "P-DISC-E003": ("ERROR", "Problem directory not found"),
    "P-PARSE-E001": ("ERROR", "YAML Front Matter cannot be parsed"),
    "P-PARSE-E002": ("ERROR", "Missing closing Front Matter delimiter"),
    "P-PARSE-E003": ("ERROR", "YAML root is not a mapping"),
    "P-PARSE-E004": ("ERROR", "Duplicate YAML key"),
    "P-PARSE-E005": ("ERROR", "Missing YAML Front Matter"),
    "P-BASE-E001": ("ERROR", "schema_version missing"),
    "P-BASE-E002": ("ERROR", "schema_version must be integer 1"),
    "P-BASE-E010": ("ERROR", "Invalid Problem ID"),
    "P-BASE-E011": ("ERROR", "Real object uses reserved ID P0000"),
    "P-BASE-E012": ("ERROR", "id missing"),
    "P-BASE-E020": ("ERROR", "type missing"),
    "P-BASE-E021": ("ERROR", "type must be problem"),
    "P-BASE-E030": ("ERROR", "title missing or empty"),
    "P-ID-E001": ("ERROR", "Duplicate Problem ID"),
    "P-STATE-E001": ("ERROR", "Invalid status"),
    "P-DATE-E001": ("ERROR", "Invalid created date"),
    "P-DATE-E002": ("ERROR", "Invalid updated date"),
    "P-DATE-E003": ("ERROR", "updated < created"),
    "P-KNOW-E001": ("ERROR", "knowledge must be a list of Knowledge IDs"),
    "P-KNOW-E002": ("ERROR", "reviewed requires explicit knowledge list"),
    "P-KNOW-E003": ("ERROR", "Invalid Knowledge target ID"),
    "P-KNOW-E004": ("ERROR", "Knowledge target uses reserved ID K0000"),
    "P-KNOW-E005": ("ERROR", "Duplicate Knowledge target"),
    "P-KNOW-E006": ("ERROR", "Knowledge target does not exist"),
    "P-KNOW-E007": ("ERROR", "Knowledge target type is not knowledge"),
    "P-KNOW-E008": ("ERROR", "reviewed Problem points to non-reviewed Knowledge"),
    "P-KNOW-E010": ("ERROR", "Knowledge dependency validation failed"),
    "P-KNOW-W001": ("WARNING", "draft Problem points to draft Knowledge"),
    "P-PART-E001": ("ERROR", "parts must be a list of strings"),
    "P-PART-E002": ("ERROR", "parts token empty after trim"),
    "P-PART-E003": ("ERROR", "duplicate parts token"),
    "P-PART-E004": ("ERROR", "parts length < 2"),
    "P-FIELD-W001": ("WARNING", "Unknown metadata field"),
}
