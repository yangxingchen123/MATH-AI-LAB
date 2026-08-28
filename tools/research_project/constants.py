"""v1.1 Research Project contract constants."""

from __future__ import annotations

from pathlib import Path

CONTRACT_VERSION = "1.1"

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = REPO_ROOT / "07_项目" / "_模板" / "研究项目_v1.1"
CONTEST_TEMPLATE_ROOT = REPO_ROOT / "07_项目" / "_模板" / "数学建模竞赛_v1"
LITERATURE_TEMPLATE_ROOT = REPO_ROOT / "07_项目" / "_模板" / "文献精读_v1"
USAGE_GUIDE_PATH = REPO_ROOT / "10_提示词" / "Research_Project_Usage_Guide.md"

PROJECT_KINDS: frozenset[str] = frozenset({"research", "contest_modeling", "literature"})
KIND_OVERLAY: dict[str, Path | None] = {
    "research": None,
    "contest_modeling": CONTEST_TEMPLATE_ROOT,
    "literature": LITERATURE_TEMPLATE_ROOT,
}
FIXTURE_ROOT = REPO_ROOT / "tests" / "research_project" / "fixtures"

PROJECTS_DIRNAME = "07_项目"
TEMPLATE_DIRNAME = "_模板"

DOSSIER_BEGIN = "<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED BEGIN -->"
DOSSIER_END = "<!-- MATH-AI-LAB:RESEARCH-DOSSIER GENERATED END -->"

RECORD_MARKER_PREFIX = "<!-- MATH-AI-LAB:RESEARCH-RECORD"

REQUIRED_FILES: tuple[str, ...] = (
    "research_dossier.md",
    "assumptions.md",
    "evidence.md",
    "decisions.md",
    "negative_results.md",
    "governance.md",
)

REQUIRED_DIRS: tuple[str, ...] = (
    "documents",
    "runs",
    "artifacts",
    "reviews",
)

OPTIONAL_LEDGER_FILES: tuple[str, ...] = (
    "literature.md",
    "novelty.md",
    "reviews/reviews.md",
)

LITERATURE_EXTENSION_VERSION = "1.3"

FILE_ALLOWED_TYPES: dict[str, frozenset[str]] = {
    "assumptions.md": frozenset({"ASSUMPTION"}),
    "evidence.md": frozenset({"CLAIM", "EVIDENCE"}),
    "decisions.md": frozenset({"DECISION"}),
    "negative_results.md": frozenset({"NEGATIVE_RESULT"}),
    "governance.md": frozenset({"GOVERNANCE", "AI_CONTRIBUTION"}),
    "literature.md": frozenset({"LITERATURE"}),
    "novelty.md": frozenset({"NOVELTY"}),
    "reviews/reviews.md": frozenset({"REVIEW"}),
}

TYPE_PREFIX: dict[str, str] = {
    "ASSUMPTION": "ASM",
    "CLAIM": "CLM",
    "EVIDENCE": "EVD",
    "DECISION": "DEC",
    "NEGATIVE_RESULT": "NEG",
    "GOVERNANCE": "GOV",
    "AI_CONTRIBUTION": "AIC",
    "LITERATURE": "LIT",
    "NOVELTY": "NOV",
    "REVIEW": "REV",
}

PREFIX_TYPE = {prefix: type_name for type_name, prefix in TYPE_PREFIX.items()}

TYPE_REQUIRED_KEYS: dict[str, tuple[str, ...]] = {
    "ASSUMPTION": ("status", "scope", "rationale", "falsifiable_when"),
    "CLAIM": ("status",),
    "EVIDENCE": ("claim_ref", "polarity", "kind"),
    "DECISION": (
        "date",
        "question",
        "options",
        "choice",
        "basis",
        "cost",
        "reversible",
        "revisit_when",
    ),
    "NEGATIVE_RESULT": (
        "status",
        "failed_route",
        "failure_evidence_refs",
        "impact",
        "retry_when",
    ),
    "GOVERNANCE": (
        "project_data_level",
        "external_processing_authorized",
        "license_status",
    ),
    "AI_CONTRIBUTION": ("date", "role", "summary", "human_review"),
    "LITERATURE": (
        "title",
        "authors",
        "year",
        "identity_kind",
        "publication_status",
    ),
    "NOVELTY": (
        "dimension",
        "existing_work",
        "current_work",
        "addition_evidence_refs",
    ),
    "REVIEW": ("role", "severity", "status", "target_ref"),
}

TYPE_OPTIONAL_KEYS: dict[str, tuple[str, ...]] = {
    "ASSUMPTION": ("impacts", "supersedes", "superseded_by", "reviewed"),
    "CLAIM": ("evidence_refs", "core"),
    "EVIDENCE": (
        "source_citation",
        "source_sha256",
        "literature_ref",
        "acknowledges_status",
    ),
    "DECISION": ("opposes", "evidence_refs", "supersedes"),
    "NEGATIVE_RESULT": ("related_claims", "related_decisions"),
    "GOVERNANCE": ("notes",),
    "AI_CONTRIBUTION": ("tools",),
    "LITERATURE": (
        "doi",
        "isbn",
        "arxiv",
        "venue",
        "version",
        "url",
        "accessed_at",
        "source_sha256",
        "license_status",
        "supersedes",
        "notes",
    ),
    "NOVELTY": ("notes",),
    "REVIEW": ("disposition", "waiver_reason"),
}

TYPE_ENUMS: dict[str, dict[str, frozenset[str]]] = {
    "ASSUMPTION": {"status": frozenset({"ACTIVE", "SUPERSEDED", "RETIRED"})},
    "CLAIM": {
        "status": frozenset({"OPEN", "SUPPORTED", "CONTESTED", "WITHDRAWN"}),
        "core": frozenset({"true", "false"}),
    },
    "EVIDENCE": {
        "polarity": frozenset({"SUPPORT", "OPPOSE", "LIMIT"}),
        "kind": frozenset({"QUOTE", "PARAPHRASE", "INFERENCE", "COMPUTATION"}),
        "acknowledges_status": frozenset({"true", "false"}),
    },
    "DECISION": {"reversible": frozenset({"true", "false"})},
    "NEGATIVE_RESULT": {"status": frozenset({"OPEN", "CLOSED"})},
    "GOVERNANCE": {
        "project_data_level": frozenset({"PUBLIC", "PERSONAL", "RESTRICTED"}),
        "external_processing_authorized": frozenset({"true", "false"}),
        "license_status": frozenset(
            {"UNKNOWN", "LOCAL_ONLY", "VERIFIED_FOR_EXTERNAL_PROCESSING"}
        ),
    },
    "AI_CONTRIBUTION": {
        "human_review": frozenset({"PENDING", "ACCEPTED", "REJECTED"})
    },
    "LITERATURE": {
        "identity_kind": frozenset({"DOI", "ISBN", "ARXIV", "URL", "LOCAL"}),
        "publication_status": frozenset(
            {
                "PREPRINT",
                "ACCEPTED",
                "VERSION_OF_RECORD",
                "CORRECTED",
                "RETRACTED",
                "WITHDRAWN",
            }
        ),
    },
    "NOVELTY": {
        "dimension": frozenset(
            {
                "PROBLEM",
                "ASSUMPTION",
                "METHOD",
                "DATA",
                "THEORY",
                "EXPERIMENT",
                "RESULT",
            }
        )
    },
    "REVIEW": {
        "role": frozenset(
            {
                "PROOF",
                "EVIDENCE_REVIEW",
                "MODEL",
                "REPRODUCIBILITY",
                "FORMALIZATION",
                "EDITOR",
            }
        ),
        "severity": frozenset({"BLOCKING", "MAJOR", "MINOR"}),
        "status": frozenset({"OPEN", "ADDRESSED", "WAIVED"}),
    },
}

LIST_KEYS: frozenset[str] = frozenset(
    {
        "evidence_refs",
        "failure_evidence_refs",
        "related_claims",
        "related_decisions",
        "addition_evidence_refs",
        "impacts",
        "opposes",
    }
)

IDENTITY_KIND_FIELDS: dict[str, str] = {
    "DOI": "doi",
    "ISBN": "isbn",
    "ARXIV": "arxiv",
    "URL": "url",
    "LOCAL": "source_sha256",
}

STATUS_REQUIRING_ACK: frozenset[str] = frozenset({"RETRACTED", "CORRECTED"})
HYPE_TERMS: tuple[str, ...] = ("首次", "创新", "显著领先")
CORE_CLAIM_STATUSES: frozenset[str] = frozenset({"OPEN", "SUPPORTED", "CONTESTED"})

LITERATURE_GATE_METRIC_NAMES: tuple[str, ...] = (
    "core_claim_citation_coverage",
    "unsupported_attribution_count",
    "retraction_correction_detection_rate",
    "quote_paraphrase_inference_classification_rate",
    "novelty_hype_block_rate",
    "blocking_review_formal_block_rate",
)

EXTERNAL_SOURCE_KINDS: frozenset[str] = frozenset({"QUOTE", "PARAPHRASE"})

GATE_METRIC_NAMES: tuple[str, ...] = (
    "project_scaffold_completeness_rate",
    "duplicate_fixture_detection_rate",
    "append_only_fixture_detection_rate",
    "decision_history_overwrite_count",
    "failed_write_byte_stability_rate",
    "unauthorized_knowledge_create_count",
    "attempt_pollution_count",
    "dossier_generated_boundary_violation_count",
    "unauthorized_external_processing_block_rate",
)
