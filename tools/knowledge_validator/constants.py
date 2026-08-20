"""Stable constants and rule registry for Knowledge Validator v1.1."""

from __future__ import annotations

VALIDATOR_VERSION = "1.1"
SCHEMA_OBJECT_TYPE = "knowledge"
SCHEMA_VERSION = 1
SCHEMA_STATUS = "frozen"

KNOWLEDGE_DIR_NAME = "01_知识库"
SCHEMA_MARKER_FILE = "元数据规范.md"
TEMPLATE_RELATIVE_PATH = "01_知识库/知识库模板.md"
# Generated derived index (Knowledge Indexer); not a Knowledge source.
INDEX_DIR_RELATIVE = "01_知识库/_索引"

ID_PATTERN = r"^K\d{4}$"
RESERVED_ID = "K0000"
ALLOWED_STATUSES = frozenset({"draft", "reviewed", "archived"})
KNOWN_FIELDS = frozenset(
    {
        "schema_version",
        "id",
        "type",
        "title",
        "aliases",
        "status",
        "created",
        "updated",
        "domain",
        "prerequisites",
        "related",
    }
)

# rule_id -> (default_severity, short_description)
RULES: dict[str, tuple[str, str]] = {
    "K-DISC-001": ("ERROR", "Invalid project root"),
    "K-DISC-INFO-001": ("INFO", "Skipped Markdown without Knowledge metadata"),
    "K-PARSE-001": ("ERROR", "YAML Front Matter cannot be parsed"),
    "K-PARSE-002": ("ERROR", "Missing closing Front Matter delimiter"),
    "K-PARSE-003": ("ERROR", "YAML root is not a mapping"),
    "K-PARSE-004": ("ERROR", "Duplicate YAML key"),
    "K-BASE-001": ("ERROR", "schema_version missing"),
    "K-BASE-002": ("ERROR", "schema_version must be integer 1"),
    "K-BASE-010": ("ERROR", "Invalid Knowledge ID"),
    "K-BASE-011": ("ERROR", "Real object uses reserved ID K0000"),
    "K-BASE-012": ("ERROR", "id missing"),
    "K-BASE-020": ("ERROR", "type missing"),
    "K-BASE-021": ("ERROR", "type must be knowledge"),
    "K-BASE-030": ("ERROR", "title missing or empty"),
    "K-BASE-040": ("ERROR", "Duplicate Knowledge ID"),
    "K-STATE-001": ("ERROR", "Invalid status"),
    "K-DATE-001": ("ERROR", "Invalid created date"),
    "K-DATE-002": ("ERROR", "Invalid updated date"),
    "K-DATE-003": ("ERROR", "updated < created"),
    "K-FIELD-001": ("ERROR", "aliases must be a list of non-empty strings"),
    "K-FIELD-002": ("ERROR", "alias duplicates title"),
    "K-FIELD-003": ("ERROR", "duplicate alias"),
    "K-FIELD-004": ("ERROR", "domain must be non-empty string"),
    "K-FIELD-005": ("ERROR", "prerequisites must be a list of Knowledge IDs"),
    "K-FIELD-006": ("ERROR", "related must be a list of Knowledge IDs"),
    "K-FIELD-007": ("ERROR", "reviewed requires aliases"),
    "K-FIELD-008": ("ERROR", "reviewed requires domain"),
    "K-FIELD-009": ("ERROR", "reviewed requires prerequisites"),
    "K-FIELD-010": ("ERROR", "reviewed requires related"),
    "K-FIELD-W001": ("WARNING", "Unknown metadata field"),
    "K-REL-001": ("ERROR", "Relation target does not exist"),
    "K-REL-002": ("ERROR", "Relation self-reference"),
    "K-REL-003": ("ERROR", "Duplicate relation reference"),
    "K-REL-004": ("ERROR", "prerequisites / related overlap"),
    "K-REL-005": ("ERROR", "reviewed source points to non-reviewed target"),
    "K-REL-006": ("ERROR", "Relation target uses reserved ID K0000"),
    "K-REL-007": ("ERROR", "Invalid relation target ID format"),
    "K-REL-W001": ("WARNING", "draft source points to draft target"),
    "K-REL-W002": ("WARNING", "draft source points to archived target (schema ambiguous)"),
    "K-GRAPH-001": ("ERROR", "prerequisite cycle detected"),
}
