"""UI operation gateway constants. Not Frozen Schema."""

from __future__ import annotations

CONTRACT_VERSION = 1

OPERATIONS = frozenset(
    {
        "RecordAttempt",
        "MoveProblemWorkflow",
        "CreateProblem",
        "CreateKnowledge",
        "CreateMethod",
        "PromoteInboxItem",
        "UpdateMarkdownBody",
    }
)

WORKFLOW_DIRS = ("未解决", "研究中", "已解决")
OUTCOMES = frozenset(
    {"correct", "incorrect", "partial", "unsolved", "abandoned", "unassessed"}
)
ASSISTANCE = frozenset({"independent", "assisted"})
PROMOTE_TYPES = frozenset({"problem", "knowledge", "method"})
