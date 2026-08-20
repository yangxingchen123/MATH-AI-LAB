"""Stable constants for Attempt Validator v1 (Frozen Attempt Schema v1)."""

from __future__ import annotations

VALIDATOR_VERSION = "1"
SCHEMA_OBJECT_TYPE = "attempt"
SCHEMA_VERSION = 1
SCHEMA_STATUS = "frozen"
SCHEMA_FROZEN_DATE = "2026-08-19"

ATTEMPT_DIR_NAME = "11_学习证据/尝试记录"
SCHEMA_MARKER_FILE = "元数据规范.md"
STORAGE_FORMAT_LEDGER = "problem_attempt_ledger_v1"

LEDGER_FILENAME_RE = r"^P\d{4}\.md$"
LEGACY_ATTEMPT_FILENAME_RE = r"^A\d{6}\.md$"

ID_PATTERN = r"^A\d{6}$"
RESERVED_ATTEMPT_ID = "A000000"
PROBLEM_ID_PATTERN = r"^P\d{4}$"

OUTCOME_VALUES = frozenset(
    {"correct", "incorrect", "partial", "unsolved", "abandoned", "unassessed"}
)
ASSISTANCE_VALUES = frozenset({"independent", "assisted"})

FROZEN_FIELDS = frozenset(
    {
        "schema_version",
        "id",
        "type",
        "problem",
        "part",
        "outcome",
        "assistance",
        "attempted_at",
        "corrections",
    }
)

REQUIRED_FIELDS = frozenset(
    {"schema_version", "id", "type", "problem", "outcome", "attempted_at"}
)

RULES: dict[str, tuple[str, str]] = {
    "A-DISC-E001": ("ERROR", "Invalid project root"),
    "A-DISC-E002": ("ERROR", "Invalid check-file target"),
    "A-DISC-E003": ("ERROR", "Attempt directory not found"),
    "A-PARSE-E001": ("ERROR", "YAML Front Matter cannot be parsed"),
    "A-PARSE-E002": ("ERROR", "Missing closing Front Matter delimiter"),
    "A-PARSE-E003": ("ERROR", "YAML root is not a mapping"),
    "A-PARSE-E004": ("ERROR", "Duplicate YAML key"),
    "A-PARSE-E005": ("ERROR", "Missing YAML Front Matter"),
    "A-FIELD-E001": ("ERROR", "Unknown metadata field"),
    "A-BASE-E001": ("ERROR", "schema_version missing"),
    "A-BASE-E002": ("ERROR", "schema_version must be integer 1"),
    "A-BASE-E010": ("ERROR", "Invalid Attempt ID"),
    "A-BASE-E011": ("ERROR", "Real object uses reserved ID A000000"),
    "A-BASE-E012": ("ERROR", "id missing"),
    "A-BASE-E020": ("ERROR", "type missing"),
    "A-BASE-E021": ("ERROR", "type must be attempt"),
    "A-BASE-E030": ("ERROR", "Required field missing"),
    "A-ID-E001": ("ERROR", "Duplicate Attempt ID"),
    "A-PROB-E001": ("ERROR", "Invalid Problem ID format"),
    "A-PROB-E002": ("ERROR", "Unknown Problem reference"),
    "A-PROB-E010": ("ERROR", "Problem dependency validation failed"),
    "A-PART-E001": ("ERROR", "part must be a single scalar anchor"),
    "A-PART-E002": ("ERROR", "Unknown part reference"),
    "A-PART-E003": ("ERROR", "Problem has no parts but part is present"),
    "A-OUT-E001": ("ERROR", "Invalid outcome value"),
    "A-ASST-E001": ("ERROR", "Invalid assistance value"),
    "A-TEMP-E001": ("ERROR", "Temporal value must be a string scalar"),
    "A-TEMP-E002": ("ERROR", "Invalid temporal string format"),
    "A-CORR-E001": ("ERROR", "corrections must be a non-empty list"),
    "A-CORR-E002": ("ERROR", "correction item must be a mapping"),
    "A-CORR-E003": ("ERROR", "correction item has unknown keys"),
    "A-CORR-E004": ("ERROR", "correction item missing required keys"),
    "A-CORR-E005": ("ERROR", "correction note must be a non-empty string"),
    "A-STOR-E001": ("ERROR", "Legacy per-Attempt file is not allowed"),
    "A-LEDG-E001": ("ERROR", "Invalid ledger filename"),
    "A-LEDG-E002": ("ERROR", "Invalid ledger storage_format"),
    "A-LEDG-E003": ("ERROR", "Ledger problem mismatch"),
    "A-LEDG-E004": ("ERROR", "Ledger attempts list invalid"),
    "A-LEDG-E005": ("ERROR", "Duplicate Attempt ID within ledger"),
    "A-LEDG-E006": ("ERROR", "Attempt problem mismatch with ledger"),
    "A-LEDG-E007": ("ERROR", "Metadata Attempt missing narrative section"),
    "A-LEDG-E008": ("ERROR", "Orphan narrative section"),
    "A-LEDG-E009": ("ERROR", "Non-canonical attempts ordering"),
    "A-LEDG-E010": ("ERROR", "Narrative order mismatch"),
}
