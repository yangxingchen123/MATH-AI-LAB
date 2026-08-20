"""Stable constants for Problem Candidate Gate v0.1 (not Problem Validator v1)."""

from __future__ import annotations

GATE_VERSION = "0.1"
SCHEMA_OBJECT_TYPE = "problem"
SCHEMA_VERSION = 1
SCHEMA_STATUS = "candidate"

PROBLEM_DIR_NAME = "02_题目库"
KNOWLEDGE_DIR_NAME = "01_知识库"
SCHEMA_MARKER_FILE = "元数据规范.md"
TEMPLATE_RELATIVE_PATH = "02_题目库/题目模板.md"

ID_PATTERN = r"^P\d{4}$"
KNOWLEDGE_ID_PATTERN = r"^K\d{4}$"
RESERVED_PROBLEM_ID = "P0000"
RESERVED_KNOWLEDGE_ID = "K0000"
ALLOWED_STATUSES = frozenset({"draft", "reviewed", "archived"})
CONTENT_REVIEW_MARKER = "Candidate Content Review: PENDING"

KNOWN_FIELDS = frozenset(
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

MANUAL_REVIEW_ITEMS: tuple[str, ...] = (
    "parts 是否应 Frozen 进入 Problem v1",
    "multipart local anchor 是否足以支持 future Attempt",
    "legacy structured registration date 策略",
    "P0002 Content Review",
    "Deferred 字段是否继续保持 Deferred",
    "当前 Candidate 是否还有会改变核心字段的现实问题",
)

# rule_id -> (default_severity, short_description)
RULES: dict[str, tuple[str, str]] = {
    "PCG-DISC-001": ("ERROR", "Invalid project root"),
    "PCG-DISC-002": ("ERROR", "Invalid check-file target"),
    "PCG-DISC-W001": ("WARNING", "Markdown without Problem Candidate metadata"),
    "PCG-DISC-I001": ("INFO", "Directory workflow state is non-authoritative"),
    "PCG-PARSE-001": ("ERROR", "YAML Front Matter cannot be parsed"),
    "PCG-PARSE-002": ("ERROR", "Missing closing Front Matter delimiter"),
    "PCG-PARSE-003": ("ERROR", "YAML root is not a mapping"),
    "PCG-PARSE-004": ("ERROR", "Duplicate YAML key"),
    "PCG-BASE-001": ("ERROR", "schema_version missing"),
    "PCG-BASE-002": ("ERROR", "schema_version must be integer 1"),
    "PCG-BASE-010": ("ERROR", "Invalid Problem ID"),
    "PCG-BASE-011": ("ERROR", "Real object uses reserved ID P0000"),
    "PCG-BASE-012": ("ERROR", "id missing"),
    "PCG-BASE-020": ("ERROR", "type missing"),
    "PCG-BASE-021": ("ERROR", "type must be problem"),
    "PCG-BASE-030": ("ERROR", "title missing or empty"),
    "PCG-ID-001": ("ERROR", "Duplicate Problem ID"),
    "PCG-STATE-001": ("ERROR", "Invalid status"),
    "PCG-DATE-001": ("ERROR", "Invalid created date"),
    "PCG-DATE-002": ("ERROR", "Invalid updated date"),
    "PCG-DATE-003": ("ERROR", "updated < created"),
    "PCG-KNOW-001": ("ERROR", "knowledge must be a list of Knowledge IDs"),
    "PCG-KNOW-002": ("ERROR", "reviewed requires explicit knowledge list"),
    "PCG-KNOW-003": ("ERROR", "Invalid Knowledge target ID"),
    "PCG-KNOW-004": ("ERROR", "Knowledge target uses reserved ID K0000"),
    "PCG-KNOW-005": ("ERROR", "Duplicate Knowledge target"),
    "PCG-KNOW-006": ("ERROR", "Knowledge target does not exist"),
    "PCG-KNOW-007": ("ERROR", "Knowledge target type is not knowledge"),
    "PCG-KNOW-008": ("ERROR", "reviewed Problem points to non-reviewed Knowledge"),
    "PCG-KNOW-E010": ("ERROR", "Knowledge Validator dependency failed"),
    "PCG-KNOW-W001": ("WARNING", "draft Problem points to draft Knowledge"),
    "PCG-PART-001": ("ERROR", "parts must be a list of strings"),
    "PCG-PART-002": ("ERROR", "parts token empty after trim"),
    "PCG-PART-003": ("ERROR", "duplicate parts token"),
    "PCG-PART-004": ("ERROR", "parts length < 2 (Candidate v0.1 provisional)"),
    "PCG-PART-W001": ("WARNING", "complex parts token"),
    "PCG-LEGACY-W001": ("WARNING", "Legacy filename ID does not match canonical Pdddd ID"),
    "PCG-READY-W001": ("WARNING", "Candidate Content Review pending"),
    "PCG-FIELD-W001": ("WARNING", "Unknown metadata field"),
}
