"""v1.5 Figure Contract constants. Renderers stay out of root requirements."""

from __future__ import annotations

CONTRACT_VERSION = "1.5"
REQUIRED_FIELDS: tuple[str, ...] = (
    "figure_id",
    "family",
    "claim_refs",
    "run_refs",
    "source_code",
    "inputs",
    "config",
    "engine",
    "outputs",
    "semantic_checks",
    "determinism",
    "trust_level",
)

FAMILIES: frozenset[str] = frozenset(
    {
        "numerical_uncertainty",
        "network",
        "exact_function",
        "architecture",
        "concept",
        "sensitivity",
    }
)

DETERMINISM_LEVELS: frozenset[str] = frozenset(
    {"BYTE_EXACT", "NORMALIZED_EXACT", "SEMANTIC_EXACT", "TOLERANCE"}
)
TRUST_LEVELS: frozenset[str] = frozenset({"DERIVED", "REVIEWED", "FORMAL"})
AI_ENGINES: frozenset[str] = frozenset({"ai-image", "image-generator", "dalle", "midjourney"})

GATE_METRIC_NAMES: tuple[str, ...] = (
    "four_pilot_provenance_coverage",
    "rebuild_success_rate",
    "semantic_check_pass_rate",
    "grayscale_colorvision_pass_rate",
    "export_only_edit_count",
    "unprovenanced_latex_count",
    "ai_as_exact_count",
)
