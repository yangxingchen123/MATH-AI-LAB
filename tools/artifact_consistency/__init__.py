"""v1.8 Artifact consistency."""

from .checks import (
    ConsistencyResult,
    check_ai_contribution,
    check_citations,
    check_knowledge_promotion,
    check_latex_figures,
    check_lean_refs,
    check_p9_publish_boundary,
)

__all__ = [
    "ConsistencyResult",
    "check_ai_contribution",
    "check_citations",
    "check_knowledge_promotion",
    "check_latex_figures",
    "check_lean_refs",
    "check_p9_publish_boundary",
]
